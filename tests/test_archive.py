import os
import tarfile
import zipfile
import tempfile
import io
import pytest

from arianna_utils.archive import safe_extract


def _create_zip(files):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    with zipfile.ZipFile(tmp.name, 'w') as z:
        for name, data in files.items():
            z.writestr(name, data)
    return tmp


def _create_tar(files):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tar')
    with tarfile.open(tmp.name, 'w') as t:
        for name, data in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            t.addfile(info, io.BytesIO(data.encode()))
    return tmp


def test_safe_extract_zip(tmp_path):
    tmp = _create_zip({'a.txt': 'hello'})
    with zipfile.ZipFile(tmp.name) as z:
        safe_extract(z, tmp_path)
    assert (tmp_path / 'a.txt').read_text() == 'hello'
    os.unlink(tmp.name)


def test_safe_extract_zip_traversal(tmp_path):
    tmp = _create_zip({'../evil.txt': 'bad'})
    with zipfile.ZipFile(tmp.name) as z:
        with pytest.raises(Exception):
            safe_extract(z, tmp_path)
    os.unlink(tmp.name)


def test_safe_extract_tar(tmp_path):
    tmp = _create_tar({'b.txt': 'world'})
    with tarfile.open(tmp.name) as t:
        safe_extract(t, tmp_path)
    assert (tmp_path / 'b.txt').read_text() == 'world'
    os.unlink(tmp.name)


def test_safe_extract_tar_traversal(tmp_path):
    tmp = _create_tar({'../evil.txt': 'bad'})
    with tarfile.open(tmp.name) as t:
        with pytest.raises(Exception):
            safe_extract(t, tmp_path)
    os.unlink(tmp.name)
