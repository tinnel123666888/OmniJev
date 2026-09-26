#!/usr/bin/env python3
"""OmniJev inference: a Jev-compatible `system_one(state, questions)` over the trained checkpoint.

Contract (mirrors TypeSafe's POST /v1/systemone answers, plus our two additions):
    noul    -> {"noul": P(yes)}
    choice  -> {"choice": <option key>, "probabilities": {key: p}, "confidence": c,
                "abstain": P(none of the above)}                       # abstain is ours
    score   -> {"score": <level>, "probabilities": {level: p}, "confidence": c}
  confidence = (K*p_max - 1)/(K - 1), Jev's definition.
  An option may be {"text": ...} or {"region": {"box": [x1,y1,x2,y2]}} (0-1000)  # region options are ours

The model returns probabilities without generating text. The Qwen3.5 branch path
shares the state prefix across question/option continuations.

CLI demo:
  python -m mso.infer --ckpt <ckpt_dir> --model <base> --image img.jpg \
     --questions '{"q1":{"type":"noul","instructions":"There is a cat."},
                   "q2":{"type":"choice","instructions":"Which animal?","criteria":{"cat":null,"dog":null}}}'
"""
import argparse
import json
import math
import os
import sys
import time
import tempfile

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mso.records as T
from mso import v04 as V4                                              # noqa: E402
from mso import branch as BR                                           # noqa: E402
from mso.head import choice_outputs, jev_confidence               # noqa: E402
from mso import panels
PANEL_DIR = os.environ.get("MSO_PANELS") or os.path.join(tempfile.gettempdir(), "mso_panels")


class MSO1:
    def __init__(self, ckpt, base_model, tiny=False, max_pixels=768 * 28 * 28, align_options=True):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        from peft import PeftModel
        acc = "cuda" if torch.cuda.is_available() else "cpu"
        if acc == "cpu":
            try:
                import torch_mlu  # noqa: F401
                if torch.mlu.is_available():
                    acc = "mlu"
            except ImportError:
                pass
        self.dev = torch.device("cpu" if tiny else acc)
        self.dtype = torch.float32 if self.dev.type == "cpu" else torch.bfloat16
        self.proc = AutoProcessor.from_pretrained(ckpt, max_pixels=max_pixels)
        if tiny:
            base = T.tiny_backbone(base_model)
        else:
            lkw = {"dtype": self.dtype}
            if os.environ.get("MSO_ATTN"):
                lkw["attn_implementation"] = os.environ["MSO_ATTN"]
            base = AutoModelForImageTextToText.from_pretrained(base_model, **lkw)
        T.add_option_tokens(base, self.proc, os.path.join(ckpt, "new_tok_emb.pt"))
        backbone = PeftModel.from_pretrained(base, ckpt).eval()
        self.model = T.MSO(backbone, base.config.text_config.hidden_size, head_norm=T.head_norm_of(ckpt)).to(self.dev)
        self.model.head.load_state_dict(torch.load(os.path.join(ckpt, "head.pt"), map_location=self.dev), strict=False)
        self.model.head.to(torch.float32).eval()
        self.coll = T.Collator(self.proc, max_pixels)
        self.align = align_options
        # optional post-hoc temperature recorded next to the head (fit on a dev split, see report)
        meta_p = os.path.join(ckpt, "head_meta.json")
        self.temp = float(json.load(open(meta_p)).get("temperature", 1.0)) if os.path.exists(meta_p) else 1.0
        _tt = (json.load(open(meta_p)).get("temperatures") or {}) if os.path.exists(meta_p) else {}
        self.temps = {k: float(_tt.get(k, self.temp)) for k in ("noul", "choice", "score")}
        # a shift of the log-odds, which is the only thing that can move a yes/no decision boundary; see _finish
        _bb = (json.load(open(meta_p)).get("biases") or {}) if os.path.exists(meta_p) else {}
        # only yes/no has a boundary a bias can move; loading one for choice or score would promise an effect the
        # renormalised softmax does not have, so it is deliberately not read
        _stray = [k for k in _bb if k != "noul"]
        if _stray:                                   # writing one and seeing nothing happen costs hours to diagnose
            raise ValueError("head_meta.json has biases for %s, but only noul has a boundary a bias can move; "
                             "a renormalised softmax over several options is unchanged by a constant" % ", ".join(sorted(_stray)))
        self.biases = {"noul": float(_bb.get("noul", 0.0))}
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        self.lm_feats = bool(meta.get("lm_feats"))
        self.ordinal = bool(meta.get("ordinal"))
        if self.ordinal and os.path.exists(os.path.join(ckpt, "ord.pt")):
            self.model.ord.load_state_dict(torch.load(os.path.join(ckpt, "ord.pt"), map_location=self.dev), strict=False)
            self.model.ord.to(torch.float32).eval()
        self.lm = V4.find_lm_head(self.model.backbone) if self.lm_feats else None
        self.open_len = len(self.coll.tok(T.OPT_OPEN, add_special_tokens=False)["input_ids"])
        self.close_len = len(self.coll.tok(T.OPT_CLOSE, add_special_tokens=False)["input_ids"])
        self.type_id = {"noul": 0, "choice": 1, "score": 2}
        # hybrid backbones (Qwen3.5: linear-attention layers) cannot isolate options with a mask;
        # they branch from a prefix cache instead (mso/branch.py). MSO_BRANCH=0 off, 2 force on.
        _b = os.environ.get("MSO_BRANCH", "1")
        self.branch = (_b == "2") or (_b != "0" and BR.is_hybrid(base))
        if self.branch:
            from mso import fast_kernels as FK
            FK.enable_fla()                  # fla Triton kernels for the linear-attention layers (MSO_FLA=0 off)
        self.open_ids = self.coll.tok(T.OPT_OPEN, add_special_tokens=False)["input_ids"]
        self.close_ids = self.coll.tok(T.OPT_CLOSE, add_special_tokens=False)["input_ids"]
        self.pad_id = self.coll.tok.pad_token_id if self.coll.tok.pad_token_id is not None else 0
        self.last_input_tokens = 0
        self._cache = {}                    # (image, video key, max_pixels) -> {pix, runs}
        self._cache_n = int(os.environ.get("MSO_STATE_CACHE", "4"))
        self.pad_tok = "<|image_pad|>"

    def _score(self, qtype, h_seq, ids, opens, closes, k):
        """u, zq (+ backbone features) -> mu for one question; shared by ask and ask_packed"""
        u = h_seq[closes[:k], :].float()
        q_end = max(0, opens[0] - 1) if opens else -1
        zq = h_seq[q_end, :].float() if opens else u.mean(0)
        if self.ordinal and qtype == "score":
            return self.model.ord(zq, u)
        feats = None
        if self.lm is not None:
            feats = V4.lm_option_feats(self.lm, h_seq, ids, opens[:k], closes[:k], q_end, self.open_len, self.close_len)
        return self.model.head(u, zq, self.type_id[qtype], feats)

    @staticmethod
    def _options(q):
        """Jev shape ('criteria' map / 'levels' list) or our shape ('options' list) -> (keys, opts)."""
        t = q["type"]
        if t == "noul":
            opts = [{"region": q["region"]}] if q.get("region") else [{"text": ""}]
            return ["yes"], opts
        if t == "score":
            lv = q.get("levels") or list((q.get("criteria") or {}).keys())
            return list(lv), [{"text": str(x)} for x in lv]
        if "options" in q:                      # our list form; entries may be region options
            keys, opts = [], []
            for i, o in enumerate(q["options"]):
                if o.get("abstain"):
                    continue
                keys.append(o.get("key") or o.get("text") or "option_{}".format(i))
                opts.append(o)
            return keys, opts
        crit = q.get("criteria") or {}          # Jev map form: key -> rubric
        keys = list(crit.keys())
        return keys, [{"text": k if crit[k] in (None, "") else "{}: {}".format(k, crit[k])} for k in keys]

    def _encode(self, image_path, video, q):
        keys, opts = self._options(q)
        b = {"img": image_path, "video": video, "instr": q["instructions"], "type": q["type"], "family": "api",
             "opt_text": [T.render_option(o) for o in opts], "tgt": [0.0] * len(opts)}
        batch = self.coll([b])
        enc = {k: (v.to(self.dev) if torch.is_tensor(v) else v) for k, v in batch["enc"].items()}
        return keys, opts, enc, batch["spans"][0]

    def _prompt(self, q, opts):
        """chat-template text for one question, with its option blocks appended"""
        body = "".join("{}{}{}".format(T.OPT_OPEN, T.render_option(o), T.OPT_CLOSE) for o in opts)
        key = (self._img, json.dumps(self._video, sort_keys=True) if self._video else "")
        if getattr(self, "_vc_key", None) != key:        # decode the state once per request, not once per question
            self._vc_key, self._vc = key, T.video_content(self._img, self._video, "")
        frames, content = self._vc[0], [dict(c) for c in self._vc[1]]
        content[-1] = {"type": "text", "text": q["instructions"]}
        prompt = self.proc.apply_chat_template([{"role": "user", "content": content}], tokenize=False, add_generation_prompt=True)
        return prompt + body, frames

    def _spans_of(self, row):
        o_ids = self.coll.tok(T.OPT_OPEN, add_special_tokens=False)["input_ids"]
        c_ids = self.coll.tok(T.OPT_CLOSE, add_special_tokens=False)["input_ids"]
        opens = [k for k in range(len(row) - len(o_ids) + 1) if row[k:k + len(o_ids)] == o_ids]
        closes = [k + len(c_ids) - 1 for k in range(len(row) - len(c_ids) + 1) if row[k:k + len(c_ids)] == c_ids]
        return opens, closes

    def _encode_many(self, image_path, video, questions, qids):
        """ONE processor call for the state; the other questions are tokenized as text with the
        image placeholders expanded to the same run lengths. -> (per-question lists, pix dict)"""
        self._img, self._video = image_path, video
        keys_l, opts_l, ids_l, spans_l = [], [], [], []
        pad_id = self.coll.tok.convert_tokens_to_ids(self.pad_tok)
        try:
            st = os.stat(image_path)
            sig = (int(st.st_size), int(st.st_mtime_ns))
        except OSError:
            sig = (0, 0)
        ck = (image_path, sig, json.dumps(video, sort_keys=True) if video else "", int(getattr(self.proc, "max_pixels", 0) or 0))
        hit = self._cache.get(ck)
        pix, runs = (hit["pix"], hit["runs"]) if hit else (None, None)
        if hit and hit.get("content"):                     # state-cache hit: no image decoding at all
            self._vc_key, self._vc = (image_path, ck[2]), (None, hit["content"])
        else:
            self._vc_key = None
        for i, qid in enumerate(qids):
            q = questions[qid]
            keys, opts = self._options(q)
            text, frames = self._prompt(q, opts)
            if pix is None:
                enc0 = self.proc(text=[text], images=frames, return_tensors="pt")
                ids = enc0["input_ids"][0].tolist()
                runs, n = [], 0
                for t in ids:
                    if t == pad_id:
                        n += 1
                    elif n:
                        runs.append(n)
                        n = 0
                if n:
                    runs.append(n)
                pix = {k: enc0[k] for k in ("pixel_values", "image_grid_thw", "pixel_values_videos", "video_grid_thw") if k in enc0}
                if len(self._cache) >= self._cache_n:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[ck] = {"pix": pix, "runs": runs, "content": self._vc[1]}
            else:
                parts = text.split(self.pad_tok)
                if len(parts) - 1 == len(runs):
                    ids = []                              # text parts tokenized alone, placeholder runs inserted as ids
                    for j, p_ in enumerate(parts):
                        if p_:
                            ids.extend(self.coll.tok(p_, add_special_tokens=False)["input_ids"])
                        if j < len(runs):
                            ids.extend([pad_id] * runs[j])
                else:                                     # layout changed: fall back to the processor
                    ids = self.proc(text=[text], images=frames, return_tensors="pt")["input_ids"][0].tolist()
            keys_l.append(keys)
            opts_l.append(opts)
            ids_l.append(ids)
            spans_l.append(self._spans_of(ids))
        pix = {k: (v.to(self.dev) if torch.is_tensor(v) else v) for k, v in pix.items()}
        return keys_l, opts_l, ids_l, spans_l, pix

    def _scale(self, vec, qtype="choice"):
        """post-hoc temperature on a probability vector: p^(1/T) renormalised (identity at T=1).
        v0.4 keeps one temperature per decision type (fitted by LBFGS on a calibration split)."""
        t = self.temps.get(qtype, self.temp)
        if abs(t - 1.0) < 1e-6:
            return vec
        w = [max(1e-9, float(x)) ** (1.0 / t) for x in vec]
        z = sum(w)
        return [x / z for x in w]

    def _finish(self, q, keys, opts, mu, lat):
        if q["type"] == "noul":
            p0 = float(mu[0])
            b = self.biases.get("noul", 0.0)
            if b:                                    # temperature cannot move the 0.5 crossing; this can
                p0 = min(max(p0, 1e-9), 1.0 - 1e-9)
                z = max(-40.0, min(40.0, math.log(p0 / (1.0 - p0)) + b))
                p0 = 1.0 / (1.0 + math.exp(-z))
            p = self._scale([p0, 1.0 - p0], "noul")[0]
            return {"noul": round(p, 4), "latency_s": round(lat, 4)}
        co = choice_outputs(mu, allow_abstain=(q["type"] == "choice"))
        full = self._scale([float(x) for x in co.probs] + [float(co.abstain)], q["type"])
        probs, abst = full[:-1], full[-1]
        co = co._replace(probs=torch.tensor(probs), abstain=torch.tensor(abst))
        probs = [float(x) for x in co.probs]
        if not probs:                                   # a question without renderable options
            return {"choice": None, "score": None, "probabilities": {}, "abstain": 1.0, "valid": False,
                    "confidence": 0.0, "latency_s": round(lat, 4)}
        if q["type"] == "score":
            s = sum(probs) or 1.0
            probs = [p / s for p in probs]       # levels are exhaustive: renormalise
            i = max(range(len(probs)), key=lambda j: probs[j])
            return {"score": keys[i], "probabilities": {kk: round(p, 4) for kk, p in zip(keys, probs)},
                    "confidence": round(float(jev_confidence(torch.tensor(probs))), 4), "latency_s": round(lat, 4)}
        i = max(range(len(probs)), key=lambda j: probs[j])
        return {"choice": keys[i], "probabilities": {kk: round(p, 4) for kk, p in zip(keys, probs)},
                "abstain": round(float(co.abstain), 4), "valid": bool(co.valid),
                "confidence": round(float(jev_confidence(torch.tensor(probs + [float(co.abstain)]))), 4),
                "latency_s": round(lat, 4)}

    @torch.no_grad()
    def ask(self, image_path, q, video=None):
        """one question, one forward (the reference path)"""
        if self.branch:
            return self.ask_branch(image_path, video, {"q": q})["q"]
        if os.environ.get("MSO_FAST", "1") != "0":
            return self.ask_packed(image_path, video, {"q": q})["q"]
        keys, opts, enc, spans = self._encode(image_path, video, q)
        L = enc["input_ids"].shape[1]
        self.last_input_tokens = int(L)
        attn = T.build_block_mask(L, spans, self.dev, self.dtype)
        t0 = time.time()
        h = self.model.hidden(enc, attn, [spans], self.align)
        opens, closes = spans
        k = min(len(closes), len(opts))
        mu = self._score(q["type"], h[0], enc["input_ids"][0], opens, closes, k)
        return self._finish(q, keys, opts, mu, time.time() - t0)

    @torch.no_grad()
    def ask_packed(self, image_path, video, questions):
        """all questions about one state in ONE forward. questions: {qid: q} -> {qid: answer}"""
        t0 = time.time()
        qids = list(questions)
        keys_l, opts_l, ids_l, spans_l, pix = self._encode_many(image_path, video, questions, qids)
        ids = [torch.tensor(x, device=self.dev) for x in ids_l]
        # shared state = longest common token prefix of the single-question sequences, cut before
        # anyone's first option marker
        L, m = 0, min(len(x) for x in ids_l)
        while L < m and all(x[L] == ids_l[0][L] for x in ids_l):
            L += 1
        L = min([L] + [sp[0][0] for sp in spans_l if sp[0]])
        base = dict(pix)
        base["input_ids"] = ids[0][None]
        base["attention_mask"] = torch.ones_like(base["input_ids"])
        pos0 = self.model.rope_positions(base, None, False)          # [3, 1, T0], mrope of question 0
        start_pos = pos0[:, 0, L].clone()                             # first text position after the state
        parts, pos_parts, blocks, spans_packed = [ids[0][:L]], [pos0[:, :, :L]], [], []
        cur = L
        for row, (opens, closes) in zip(ids, spans_l):
            suf = row[L:]
            n = int(suf.shape[0])
            parts.append(suf)
            p = start_pos[:, None] + torch.arange(n, device=self.dev)[None, :]
            op = [o - L for o in opens]
            cl = [c - L for c in closes]
            if self.align and op and cl:                              # options share a start position
                st = int(p[0, op[0]])
                for o, c in zip(op, cl):
                    if c >= o:
                        p[:, o:c + 1] = torch.arange(st, st + (c - o + 1), device=self.dev)[None, :]
            pos_parts.append(p[:, None, :])
            spans_packed.append(([cur + o for o in op], [cur + c for c in cl]))
            blocks.append((cur, cur + n))
            cur += n
        enc = {"input_ids": torch.cat(parts)[None], "position_ids": torch.cat(pos_parts, dim=2),
               "attention_mask": build_packed_mask(cur, L, blocks, spans_packed, self.dev, self.dtype)}
        enc.update(pix)
        self.last_input_tokens = int(cur)
        out = self.model.backbone(**enc, output_hidden_states=True, logits_to_keep=1)
        h = out.hidden_states[-1]
        lat = time.time() - t0
        res = {}
        for qid, keys, opts, (opens, closes) in zip(qids, keys_l, opts_l, spans_packed):
            k = min(len(closes), len(opts))
            mu = self._score(questions[qid]["type"], h[0], enc["input_ids"][0], opens, closes, k)
            res[qid] = self._finish(questions[qid], keys, opts, mu, lat / max(1, len(qids)))
            res[qid]["latency_total_s"] = round(lat, 4)
        return res

    @torch.no_grad()
    def ask_branch(self, image_path, video, questions):
        """hybrid backbones: the shared prefix once (its cache kept), then one row per
        (question, option) continuing that cache in a single batched forward (mso/branch.py).
        Exactly order-invariant and exactly equal to a plain forward per option. {qid: q} -> {qid: answer}"""
        t0 = time.time()
        qids = list(questions)
        keys_l, opts_l, ids_l, spans_l, pix = self._encode_many(image_path, video, questions, qids)
        L, m = 0, min(len(x) for x in ids_l)
        while L < m and all(x[L] == ids_l[0][L] for x in ids_l):
            L += 1
        # the prefix stops before the token preceding the first option marker: every row keeps
        # that token (zq is read there)
        L = max(1, min([L] + [sp[0][0] - 1 for sp in spans_l if sp[0]]))
        base = dict(pix)
        base["input_ids"] = torch.tensor(ids_l[0], device=self.dev)[None]
        base["attention_mask"] = torch.ones_like(base["input_ids"])
        penc = BR.prefix_inputs(base, L)
        ppos = BR.prefix_positions(self.model, penc)
        qrows = [BR.rows_from_ids(row, L, sp[0], sp[1], k=len(opts))
                 for row, sp, opts in zip(ids_l, spans_l, opts_l)]
        outs = BR.branch_questions(self.model.backbone, penc, qrows, self.dev, self.open_ids, self.close_ids,
                                   lm_head=self.lm, prefix_pos=ppos, pad_id=self.pad_id)
        lat = time.time() - t0
        self.last_input_tokens = int(L + sum(len(r) for qr in qrows for r in qr))
        res = {}
        for qid, keys, opts, (u, zq, feats) in zip(qids, keys_l, opts_l, outs):
            q = questions[qid]
            k = min(int(u.shape[0]), len(opts))
            if self.ordinal and q["type"] == "score":
                mu = self.model.ord(zq, u[:k])
            else:
                mu = self.model.head(u[:k], zq, self.type_id[q["type"]], (feats[:k] if feats is not None else None))
            res[qid] = self._finish(q, keys, opts, mu, lat / max(1, len(qids)))
            res[qid]["latency_total_s"] = round(lat, 4)
        return res

    def system_one(self, state, questions, packed=True):
        """state: {"images": [path, ...], "video": {n_frames, cols, tile, timestamps, duration}?}
        questions: {id: question} -> {id: answer}.

        The model encodes exactly one image per request. Several stills are tiled into a single numbered panel in
        reading order, so a question may refer to "the second picture"; up to and including v1.0 the extra images
        were accepted and then silently dropped, which made such questions unanswerable. Set MSO_NO_PANELS=1 to
        restore that older behaviour, which is what the published v0.8 numbers were measured under.
        With `video`, images[0] is already the 4x4 frame mosaic and is passed through untouched.
        packed=True answers every question in one forward (state encoded once)."""
        video = state.get("video")
        _ims = state["images"]
        img = panels.compose_path(_ims, PANEL_DIR) if (len(_ims) > 1 and not video) else _ims[0]
        if self.branch:
            return self.ask_branch(img, video, questions)
        if packed and questions:
            return self.ask_packed(img, video, questions)
        return {qid: self.ask(img, q, video) for qid, q in questions.items()}


def build_packed_mask(T_, L, blocks, spans, device, dtype):
    """[1,1,T,T] additive mask: state causal; a question block sees the state + itself (causal);
    options inside a block are mutually invisible; blocks never see each other."""
    ar = torch.arange(T_, device=device)
    m = ar[:, None] >= ar[None, :]
    for (s_, e_) in blocks:
        m[s_:e_, L:s_] = False
    for (opens, closes) in spans:
        bl = [(o, c) for o, c in zip(opens, closes) if c >= o]
        for i, (o1, c1) in enumerate(bl):
            for j, (o2, c2) in enumerate(bl):
                if i != j:
                    m[o1:c1 + 1, o2:c2 + 1] = False
    add = torch.zeros(T_, T_, device=device, dtype=dtype)
    add.masked_fill_(~m, torch.finfo(dtype).min)
    return add[None, None]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--questions", required=True, help="JSON map id -> question")
    ap.add_argument("--tiny", action="store_true")
    a = ap.parse_args()
    m = MSO1(a.ckpt, a.model, tiny=a.tiny)
    out = m.system_one({"images": [a.image]}, json.loads(a.questions))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
