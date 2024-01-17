import pathlib
import pickle
import shutil
from unittest.mock import patch

import pytest

import fake_faces_generator.download as download


class SimulatedException(Exception):
    pass


class FailingSet(set):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, element):
        if len(self) < 2:
            super().add(element)
        else:
            raise SimulatedException


@pytest.fixture
def tmpdir_with_cleanup(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    yield tmpdir
    shutil.rmtree(tmpdir)


@patch("fake_faces_generator.download.set")
def test_failing_download(mocked_set, tmpdir_with_cleanup):
    mocked_set.side_effect = lambda: FailingSet()
    try:
        download.run(tmpdir_with_cleanup, 3)
    except SimulatedException:
        pkl_files = list(tmpdir_with_cleanup.glob("*.pkl"))
        assert len(pkl_files) == 1
        assert pkl_files[0].name == "seen_images.pkl"


def test_successful_download(tmpdir_with_cleanup):
    download.run(tmpdir_with_cleanup, 3)
    jpg_files = list(tmpdir_with_cleanup.glob("*.jpg"))
    pkl_files = list(tmpdir_with_cleanup.glob("*.pkl"))
    assert len(jpg_files) == 3
    assert len(pkl_files) == 1
    assert pkl_files[0].name == "seen_images.pkl"


def test_incremental_download(tmpdir_with_cleanup):
    download.run(tmpdir_with_cleanup, 3)
    download.run(tmpdir_with_cleanup, 3)
    jpg_files = list(tmpdir_with_cleanup.glob("*.jpg"))
    assert len(jpg_files) == 6
    with open(tmpdir_with_cleanup / "seen_images.pkl", "rb") as f:
        seen = pickle.load(f)
    assert len(seen) == 6
