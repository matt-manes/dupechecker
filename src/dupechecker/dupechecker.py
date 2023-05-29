import argparse
import filecmp
from itertools import combinations

from griddle import griddy
from noiftimer import time_it
from pathier import Pathier


def get_pairs(path: Pathier, recursive: bool = False) -> list[tuple[Pathier, Pathier]]:
    files = list(path.rglob("*.*")) if recursive else list(path.glob("*.*"))
    return list(combinations(files, 2))


def compare_files(files: tuple[Pathier, Pathier]) -> bool:
    return filecmp.cmp(files[0], files[1], False)


def get_matches(pairs: list[tuple[Pathier, Pathier]]) -> list[tuple[Pathier, Pathier]]:
    return [pair for pair in pairs if compare_files(pair)]


def combine_matches(matches: list[tuple[Pathier, Pathier]]) -> list[list[Pathier]]:
    combined_matches = []
    while len(matches) > 0:
        this_match = matches.pop()
        combined_match = list(this_match)
        poppers = []
        for j, match in enumerate(matches):
            if match[0] in combined_match and match[1] not in combined_match:
                combined_match.append(match[1])
                poppers.append(match)
            elif match[1] in combined_match and match[0] not in combined_match:
                combined_match.append(match[0])
                poppers.append(match)
        combined_matches.append(combined_match)
        for popper in poppers:
            matches.pop(matches.index(popper))
    return combined_matches


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=""" Glob files to compare recursively. """,
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

    return args


@time_it()
def main(args: argparse.Namespace | None = None):
    if not args:
        args = get_args()
    matches = combine_matches(get_matches(get_pairs(args.path, args.recursive)))
    if matches:
        print("Duplicate files:")
        print(griddy(matches))
    else:
        print("No duplicates detected.")


if __name__ == "__main__":
    main(get_args())
