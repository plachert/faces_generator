import pathlib

import fake_faces_generator.download as download


def test_successful_download(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    download.run(tmpdir, 3)
    jpg_files = list(tmpdir.glob("*.jpg"))
    pkl_files = list(tmpdir.glob("*.pkl"))
    assert len(jpg_files) == 3
    assert len(pkl_files) == 1
    assert pkl_files[0].name == "seen_images.pkl"
