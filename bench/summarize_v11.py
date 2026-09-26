"""Recompute the common-family summary from the published aggregate reports."""
import json
from pathlib import Path
from statistics import mean


def summarize(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))["models"]
    common = sorted(set.intersection(*(set(m["reports"]) for m in data.values())))
    rows = []
    for name, model in data.items():
        reports = []
        for family in common:
            raw = model["reports"][family]["data"]
            if model["kind"] == "base":
                metric = raw["arms"]["A1_raw"]["ALL"]
            elif model["kind"] == "mso":
                metric = raw["report"]["ALL"]
            else:
                metric = raw
            reports.append(metric)
        n = sum(r["n"] for r in reports)
        rows.append({"model": name, "families": len(common), "n": n,
                     "macro_acc": mean(r["acc"] for r in reports),
                     "micro_acc": sum(r["acc"] * r["n"] for r in reports) / n,
                     "macro_ece": mean(r["ece"] for r in reports) if all("ece" in r for r in reports) else None})
    return rows


if __name__ == "__main__":
    print(json.dumps(summarize(Path(__file__).resolve().parents[1] / "docs/results_v11.json"), indent=2))
