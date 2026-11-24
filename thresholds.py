"""Select an alert threshold on validation data and evaluate it on held-out data."""
import argparse
import csv
import math
from pathlib import Path


def load_rows(path):
    splits = {"validation": [], "test": []}
    seen = set()
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["id", "split", "score", "label"]:
            raise ValueError("Expected header: id,split,score,label")
        for row in reader:
            name, split, label = row["id"], row["split"], row["label"]
            if not name or name in seen or split not in splits or label not in ("0", "1") or None in row:
                raise ValueError(f"Invalid or duplicate row at line {reader.line_num}")
            try:
                score = float(row["score"] or "")
            except ValueError:
                raise ValueError(f"Invalid score for {name}") from None
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError(f"Score outside [0, 1] for {name}")
            seen.add(name)
            splits[split].append((score, int(label)))
    if any({label for _, label in rows} != {0, 1} for rows in splits.values()):
        raise ValueError("Include both classes in each split.")
    return splits


def measure(rows, threshold, miss_cost):
    tp = fp = tn = fn = 0
    for score, label in rows:
        if score >= threshold:
            tp += label
            fp += 1 - label
        else:
            tn += 1 - label
            fn += label
    return dict(tp=tp, fp=fp, tn=tn, fn=fn, cost=miss_cost * fn + fp)


def choose(validation, miss_cost):
    candidates = {score for score, _ in validation} | {math.inf}
    # A higher threshold wins when two policies have the same validation cost.
    return min(candidates, key=lambda t: (measure(validation, t, miss_cost)["cost"], -t))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--miss-cost", type=int, default=4,
                        help="Cost of one missed risk relative to one false alarm")
    args = parser.parse_args()
    if args.miss_cost < 1:
        parser.error("miss-cost must be a positive integer")
    try:
        splits = load_rows(args.csv_file)
    except (ValueError, OSError, csv.Error) as error:
        parser.exit(2, f"Input error: {error}\n")
    threshold = choose(splits["validation"], args.miss_cost)
    display = "never alert" if math.isinf(threshold) else f"score >= {threshold:g}"
    print(f"Selected on validation: {display}")
    for split, rows in splits.items():
        m = measure(rows, threshold, args.miss_cost)
        print(f"{split:10} TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']} cost={m['cost']}")


if __name__ == "__main__":
    main()
