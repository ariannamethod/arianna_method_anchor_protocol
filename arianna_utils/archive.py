import os
import zipfile
import tarfile


def _is_within_directory(directory: str, target: str) -> bool:
    """Return True if target is inside directory."""
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    return os.path.commonprefix([abs_directory, abs_target]) == abs_directory


def safe_extract(archive, path: str = ".", members=None, *, numeric_owner: bool = False) -> None:
    """Safely extract ``archive`` to ``path``.

    Supports :class:`zipfile.ZipFile` and :class:`tarfile.TarFile` objects and
    prevents path traversal vulnerabilities by verifying extracted paths.
    """
    if isinstance(archive, zipfile.ZipFile):
        infos = members or archive.infolist()
        for info in infos:
            name = info.filename if isinstance(info, zipfile.ZipInfo) else str(info)
            dest = os.path.join(path, name)
            if not _is_within_directory(path, dest):
                raise Exception("Attempted Path Traversal in Zip File")
        archive.extractall(path, members=members)
    elif isinstance(archive, tarfile.TarFile):
        infos = members or archive.getmembers()
        for info in infos:
            name = info.name if isinstance(info, tarfile.TarInfo) else str(info)
            dest = os.path.join(path, name)
            if not _is_within_directory(path, dest):
                raise Exception("Attempted Path Traversal in Tar File")
        archive.extractall(path, members=members, numeric_owner=numeric_owner)
    else:  # pragma: no cover - unsupported archive types
        raise TypeError(f"Unsupported archive type: {type(archive)}")
