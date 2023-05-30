import argparse
import filecmp
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

from griddle import griddy
from noiftimer import time_it
from pathier import Pathier
from printbuddies import Spinner


def get_pairs(path: Pathier, recursive: bool = False) -> list[tuple[Pathier, Pathier]]:
    """Return a list of tuples where each tuple is a unique pair of files in `path` to be compared.
    If `recursive` is `True`, additional files to be compared will be pulled from subdirectories of `path`"""
    files = list(path.rglob("*.*")) if recursive else list(path.glob("*.*"))
    return list(combinations(files, 2))


def compare_files(files: tuple[Pathier, Pathier]) -> bool:
    """Compare two files, return `True` if they are the same."""
    return filecmp.cmp(files[0], files[1], False)


def get_matches(pairs: list[tuple[Pathier, Pathier]]) -> list[tuple[Pathier, Pathier]]:
    """Return a list of file pairs where each file in a pair is determined to be the same."""
    return [pair for pair in pairs if compare_files(pair)]


def combine_matches(matches: list[tuple[Pathier, Pathier]]) -> list[list[Pathier]]:
    """Consolidate equivalent files based on if `a == b` and `b == c`, then also `a == c`.

    i.e. (each tuple in `matches` represents two files determined to be equivalent)
    >>> matches = [(file1, file2), (file2, file3), (file4, file5), (file6, file1)]
    >>> combine_matches(matches)
    >>> [[file1, file2, file3, file6], [file4, file5]]"""
    combined_matches = []
    while len(matches) > 0:
        this_match = matches.pop()
        combined_match = list(this_match)
        poppers = []
        for match in matches:
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


# Wrapping these two steps in one function for threading in dupechecker()
def process_files(pairs: list[tuple[Pathier, Pathier]]) -> list[list[Pathier]]:
    return combine_matches(get_matches(pairs))


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=""" Glob files to compare recursively. """,
    )

    parser.add_argument(
        "-d",
        "--delete_dupes",
        action="store_true",
        help=""" After finding duplicates, delete all but one copy.
        For each set of duplicates, the tool will ask you to enter the number corresponding to the copy you want to keep.
        Pressing 'enter' without entering a number will skip that set without deleting anything.""",
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


def delete_wizard(matches: list[list[Pathier]]):
    """Ask which file to keep for each set."""
    print("Enter the corresponding number of the file to keep.")
    print(
        "Press 'Enter' without giving a number to skip deleting any files for the given set."
    )
    for match in matches:
        map_ = {str(i): file for i, file in enumerate(match, 1)}
        prompt = " | ".join(f"({i})<->{file}" for i, file in map_.items())
        keeper = input(prompt + " ")
        if keeper:
            [map_[num].delete() for num in map_ if num != keeper]


@time_it()
def dupechecker(args: argparse.Namespace | None = None):
    if not args:
        args = get_args()
    pairs = get_pairs(args.path, args.recursive)
    print(f"Comparing {len(pairs)} pairs of files for duplicates...")
    s = [
        ch.rjust(i + j)
        for i in range(1, 25, 3)
        for j, ch in enumerate(["/", "-", "\\"])
    ]
    s += s[::-1]
    with Spinner(s) as spinner:
        with ThreadPoolExecutor() as exc:
            thread = exc.submit(process_files, pairs)
            while not thread.done():
                spinner.display()
                time.sleep(0.025)
            matches = thread.result()
    if matches:
        print(f"Found {len(matches)} duplicate files:")
        print(griddy(matches))
        if args.delete_dupes:
            delete_wizard(matches)
    else:
        print("No duplicates detected.")


if __name__ == "__main__":
    dupechecker(get_args())
