import pytest
from pathier import Pathier

import dupechecker

root = Pathier(__file__).parent

stems_same = ["afile", "thesamefile"]
stems_diff = ["adifferentfile"]


def test_group_by_size():
    files = list((root / "files").iterdir())
    grouped_files = dupechecker.group_by_size(files)
    grouped_files = sorted(grouped_files, key=lambda group: len(group), reverse=True)
    assert len(grouped_files) == 2
    assert (
        grouped_files[0][0].stem in stems_same
        and grouped_files[0][1].stem in stems_same
    )
    assert grouped_files[1][0].stem in stems_diff


def test_find_dupes():
    files = list((root / "files").iterdir())
    matches = dupechecker.find_dupes(files)
    assert len(files) > 0
    assert len(matches) == 1
    assert len(matches[0]) == 2
    assert matches[0][0].stem in stems_same
    assert matches[0][1].stem in stems_same
