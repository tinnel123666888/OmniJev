"""Multi-image states, made visible to the model.

The whole stack encodes exactly one image per record: the trainer takes `state["images"][0]` and so does
`MSOInfer.system_one`. Every record that carries more than one image therefore had its extra images silently
dropped while its prompt still said "the first picture ... the second picture", which makes those questions
unanswerable rather than merely hard. That covers the teach-pendant families (scene + wrist camera), RoboArena
(start frame + now + wrist), Mario (two consecutive frames) and JAT.

The video path already solved this by tiling frames into one mosaic before encoding. This does the same for a list
of stills: the panels are laid out in reading order, separated by a thin border, and each one carries a small
numeral so "the second picture" has something to point at. One image goes through untouched, so single-image
records and requests are bit-for-bit unaffected.
"""
import hashlib
import os
import tempfile

# MSO_NO_PANELS=1 restores the old behaviour (encode only the first image). It exists so the same weights can be
# scored both ways, which is the only way to attribute a change to this fix rather than to the model.
PANELS_OFF = os.environ.get("MSO_NO_PANELS", "").strip().lower() in ("1", "true", "yes", "on")
_BORDER = 6
_LABEL = 22


def _grid(n):
    return (1, 1) if n <= 1 else (2, 1) if n == 2 else (2, 2) if n <= 4 else (3, (n + 2) // 3)


def compose(paths, max_side=448):
    """tile the images into a single PIL image, in reading order, each panel numbered"""
    from PIL import Image, ImageDraw
    ims = []
    for p in paths:
        im = Image.open(p)
        im = im.convert("RGB")
        if max(im.size) > max_side:
            im.thumbnail((max_side, max_side))
        ims.append(im)
    cols, rows = _grid(len(ims))
    cw = max(i.width for i in ims)
    ch = max(i.height for i in ims)
    W = cols * cw + (cols + 1) * _BORDER
    H = rows * (ch + _LABEL) + (rows + 1) * _BORDER
    canvas = Image.new("RGB", (W, H), (32, 32, 32))
    draw = ImageDraw.Draw(canvas)
    for k, im in enumerate(ims):
        c, r = k % cols, k // cols
        x = _BORDER + c * (cw + _BORDER)
        y = _BORDER + r * (ch + _LABEL + _BORDER)
        draw.text((x + 2, y + 4), "%d" % (k + 1), fill=(255, 255, 255))
        canvas.paste(im, (x + (cw - im.width) // 2, y + _LABEL + (ch - im.height) // 2))
    return canvas


def compose_path(paths, cache_dir, max_side=448):
    """same, written to `cache_dir` and reused on later epochs; returns a path to a single image.
    A single path is returned unchanged, so nothing is copied or re-encoded for the common case."""
    if not paths:
        return None
    if len(paths) == 1 or PANELS_OFF:
        return paths[0]
    stamps = [(str(p), os.stat(p).st_size, os.stat(p).st_mtime_ns) for p in paths]
    key = hashlib.sha1((repr(stamps) + "|%d" % max_side).encode()).hexdigest()[:20]
    out = os.path.join(cache_dir, key + ".jpg")
    if os.path.exists(out):
        return out
    os.makedirs(cache_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=key + ".", suffix=".part", dir=cache_dir)
    os.close(fd)
    try:
        compose(paths, max_side).save(tmp, format="JPEG", quality=88)   # the .part name carries no format for PIL
        os.replace(tmp, out)
        return out
    except Exception:
        # Reject incomplete states instead of answering a different question.
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
