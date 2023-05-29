import difflib
from pathier import Pathier
from itertools import combinations
import argparse
from noiftimer import time_it
from griddle import griddy


def get_comparisons(path: Pathier) -> dict[Pathier, tuple[Pathier, ...]]:
    files = list(path.glob("*.*"))
    files = sorted(files, key=lambda f: f.stem)
    pairs = list(combinations(files, 2))
    comparisons = {}
    for p1, p2 in pairs:
        if p1 not in comparisons:
            comparisons[p1] = [p2]
        else:
            comparisons[p1].append(p2)
    return comparisons


def compare_files(path: Pathier) -> dict[tuple[Pathier, Pathier], float]:
    """Compare binary content of files in `path`.
    Returns a dictionary where each key is a tuple containing the two files that were compared and the value is their similarity in the range [0,1]."""
    comparisons = get_comparisons(path)
    matches = {}
    for comparee in comparisons:
        matcher = difflib.SequenceMatcher()
        matcher.set_seq2(comparee.read_bytes())  # type: ignore
        for file in comparisons[comparee]:
            matcher.set_seq1(file.read_bytes())  # type: ignore
            matches[(comparee, file)] = matcher.real_quick_ratio()
    sorted_keys = sorted(matches.keys(), key=lambda m: matches[m], reverse=True)
    matches = {key: matches[key] for key in sorted_keys}
    return matches


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.0,
        help=""" Only show matches with a ratio above this value. Range should be [0,100].""",
    )

    parser.add_argument(
        "path",
        type=str,
        default=Pathier.cwd(),
        nargs="?",
        help=""" The path to compare files in. """,
    )

    args = parser.parse_args()
    if not args.path == Pathier.cwd():
        args.path = Pathier(args.path)
    args.threshold = args.threshold / 100

    return args


@time_it()
def main(args: argparse.Namespace | None = None):
    if not args:
        args = get_args()
    matches = compare_files(args.path)
    results = [
        (match[0].name, match[1].name, f"{matches[match]*100:.2f}%")
        for match in matches
        if matches[match] >= args.threshold
    ]
    print("Comparison results:")
    print(griddy(results, ["file1", "file2", "percentage"]))


if __name__ == "__main__":
    main(get_args())
