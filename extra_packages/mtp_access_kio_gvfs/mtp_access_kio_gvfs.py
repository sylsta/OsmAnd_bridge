"""
mtp_access.py
=============
A cross-backend Python module for accessing MTP (Media Transfer Protocol) devices
on Linux, supporting both KDE (KIO/kiod5) and GNOME (gvfs) environments.

The module automatically detects which backend is active and provides a unified
API for listing devices, browsing directories, and copying files/directories
in both directions (device <-> host).

Backends:
    - KIO  : used by KDE Plasma; files are accessed via `kioclient5` CLI
    - gvfs : used by GNOME/GTK environments; files are mounted under /run/user/.../gvfsd/

Usage example::

    from mtp_access import MTPClient

    client = MTPClient()
    print(client.list_devices())

    # List root folders of the first device
    device, folders = list(client.list_root_folders().items())[0]
    print(device, folders)

    # Copy a folder from the device to the host
    client.copy_from_device(device, "DCIM", "/tmp/photos")

    # Copy a file from the host to the device
    client.copy_to_device("/tmp/note.txt", device, "Documents/note.txt")
"""

import os
import glob
import shutil
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

def detect_backend() -> str | None:
    """Detect which MTP backend is running on the system.

    Checks for active processes:
    - ``kiod5``   → KDE KIO backend
    - ``gvfsd-mtp`` → GNOME gvfs backend

    Returns:
        ``'kio'``, ``'gvfs'``, or ``None`` if no backend is found.
    """
    result = subprocess.run(['pgrep', '-a', 'kiod5'], capture_output=True, text=True)
    if result.stdout.strip():
        return 'kio'

    result = subprocess.run(['pgrep', '-a', 'gvfsd-mtp'], capture_output=True, text=True)
    if result.stdout.strip():
        return 'gvfs'

    return None


# ---------------------------------------------------------------------------
# KIO helpers
# ---------------------------------------------------------------------------

def _kio_ls(path: str) -> list[str]:
    """List entries at a KIO MTP path, filtering out '.' and '..'.

    Args:
        path: A KIO URI such as ``mtp:/`` or ``mtp:/Smini/DCIM/``.

    Returns:
        List of entry names (files and directories).
    """
    result = subprocess.run(['kioclient5', 'ls', path], capture_output=True, text=True)
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() not in ('.', '..')
    ]


def _kio_copy(src: str, dst: str) -> None:
    """Copy a single file or directory using kioclient5.

    Args:
        src: Source KIO URI or local path.
        dst: Destination KIO URI or local path.

    Raises:
        subprocess.CalledProcessError: if kioclient5 returns a non-zero exit code.
    """
    subprocess.run(['kioclient5', 'copy', src, dst], check=True)


def _kio_copy_recursive(src_kio: str, dst_local: Path) -> None:
    """Recursively copy a KIO MTP directory to a local destination.

    Walks the KIO tree depth-first, creating local directories as needed
    and copying each file individually via ``kioclient5``.

    Args:
        src_kio: Source KIO URI (e.g. ``mtp:/Smini/DCIM``).
        dst_local: Local :class:`pathlib.Path` where files will be written.
    """
    dst_local.mkdir(parents=True, exist_ok=True)
    entries = _kio_ls(src_kio + '/')

    for entry in entries:
        child_kio = f"{src_kio}/{entry}"
        child_local = dst_local / entry

        # Try listing the child; if it returns results it is a directory
        children = _kio_ls(child_kio + '/')
        if children or _kio_is_dir(child_kio):
            # Recurse into subdirectory
            _kio_copy_recursive(child_kio, child_local)
        else:
            # It is a file: copy it
            print(f"  Copying {child_kio} -> {child_local}")
            _kio_copy(child_kio, str(child_local))


def _kio_is_dir(kio_path: str) -> bool:
    """Heuristic to determine whether a KIO path is a directory.

    Runs ``kioclient5 ls`` and considers the path a directory if the command
    succeeds and produces output (even an empty listing).

    Args:
        kio_path: KIO URI to test.

    Returns:
        ``True`` if the path appears to be a directory, ``False`` otherwise.
    """
    result = subprocess.run(
        ['kioclient5', 'ls', kio_path + '/'],
        capture_output=True, text=True
    )
    # A directory listing returns exit code 0; a file typically returns an error
    return result.returncode == 0


def _kio_upload_recursive(src_local: Path, dst_kio: str) -> None:
    """Recursively copy a local file or directory to a KIO MTP path.

    Args:
        src_local: Local :class:`pathlib.Path` to copy (file or directory).
        dst_kio: Destination KIO URI on the MTP device.
    """
    if src_local.is_file():
        print(f"  Uploading {src_local} -> {dst_kio}")
        _kio_copy(str(src_local), dst_kio)
    elif src_local.is_dir():
        for child in src_local.iterdir():
            child_dst = f"{dst_kio}/{child.name}"
            _kio_upload_recursive(child, child_dst)


# ---------------------------------------------------------------------------
# gvfs helpers
# ---------------------------------------------------------------------------

def _gvfs_base() -> Path:
    """Return the gvfs mount root for the current user.

    Returns:
        Path to ``/run/user/<uid>/gvfsd/``.
    """
    return Path(f"/run/user/{os.getuid()}/gvfsd/")


def _gvfs_mtp_mounts() -> list[Path]:
    """Find all currently mounted MTP devices under gvfsd.

    Returns:
        List of :class:`pathlib.Path` objects, one per mounted MTP device.
    """
    base = _gvfs_base()
    return [Path(p) for p in glob.glob(str(base / "mtp*"))]


# ---------------------------------------------------------------------------
# Main client class
# ---------------------------------------------------------------------------

class MTPClient:
    """Unified MTP client that works with both KIO and gvfs backends.

    Automatically detects the active backend on instantiation. All public
    methods accept a *device* parameter whose meaning depends on the backend:

    - **KIO**  : the device name as shown by ``kioclient5 ls mtp:/``
      (e.g. ``'Smini'``).
    - **gvfs** : the full mount-point path under ``/run/user/.../gvfsd/``
      (e.g. ``'/run/user/1000/gvfsd/mtp:host=...'``).

    Attributes:
        backend (str): ``'kio'`` or ``'gvfs'``.

    Raises:
        RuntimeError: if no MTP backend is detected at instantiation time.

    Example::

        client = MTPClient()
        devices = client.list_devices()
        client.copy_from_device(devices[0], "DCIM", "/tmp/photos")
    """

    def __init__(self):
        self.backend = detect_backend()
        if self.backend is None:
            raise RuntimeError(
                "No MTP backend detected. "
                "Make sure kiod5 (KDE) or gvfsd-mtp (GNOME) is running."
            )
        print(f"[MTPClient] Backend detected: {self.backend}")

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_devices(self) -> list[str]:
        """Return the list of connected MTP devices.

        For KIO, this queries ``mtp:/`` via kioclient5.
        For gvfs, this scans the ``gvfsd/`` directory for ``mtp*`` mounts.

        Returns:
            List of device identifiers (names for KIO, paths for gvfs).
        """
        if self.backend == 'kio':
            return _kio_ls('mtp:/')

        # gvfs: return string paths for consistency
        return [str(p) for p in _gvfs_mtp_mounts()]

    def list_root_folders(self) -> dict[str, list[str]]:
        """Return the root-level folders for every connected MTP device.

        Returns:
            A dict mapping each device identifier to its list of root folders.

        Example::

            {'Smini': ['Internal storage', 'SD card']}
        """
        result = {}
        for device in self.list_devices():
            result[device] = self.list_folder(device, '')
        return result

    def list_folder(self, device: str, path: str) -> list[str]:
        """List the contents of a folder on an MTP device.

        Args:
            device: Device identifier (name for KIO, mount path for gvfs).
            path:   Relative path on the device (empty string for root).

        Returns:
            List of entry names inside the folder.
        """
        if self.backend == 'kio':
            kio_path = f"mtp:/{device}/{path}" if path else f"mtp:/{device}"
            return _kio_ls(kio_path)

        # gvfs: plain filesystem access
        full_path = Path(device) / path if path else Path(device)
        try:
            return os.listdir(full_path)
        except PermissionError as exc:
            print(f"[MTPClient] Permission denied: {full_path} ({exc})")
            return []

    # ------------------------------------------------------------------
    # Copy: device -> host
    # ------------------------------------------------------------------

    def copy_from_device(self, device: str, src_path: str, dst_local: str) -> None:
        """Copy a file or directory from the MTP device to the local host.

        The copy is always recursive: if *src_path* points to a directory,
        the entire tree is replicated under *dst_local*.

        Args:
            device:    Device identifier.
            src_path:  Relative path on the device (e.g. ``'DCIM'`` or
                       ``'Documents/notes.txt'``).
            dst_local: Local destination path (file or directory).

        Example::

            client.copy_from_device('Smini', 'DCIM', '/tmp/photos')
        """
        dst = Path(dst_local)

        if self.backend == 'kio':
            kio_src = f"mtp:/{device}/{src_path}"
            if _kio_is_dir(kio_src):
                # Recursive directory copy
                _kio_copy_recursive(kio_src, dst / Path(src_path).name)
            else:
                # Single file copy
                dst.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Copying {kio_src} -> {dst}")
                _kio_copy(kio_src, str(dst))

        else:  # gvfs
            src = Path(device) / src_path
            if src.is_dir():
                print(f"  Copying directory {src} -> {dst}")
                shutil.copytree(str(src), str(dst / src.name), dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Copying file {src} -> {dst}")
                shutil.copy2(str(src), str(dst))

    # ------------------------------------------------------------------
    # Copy: host -> device
    # ------------------------------------------------------------------

    def copy_to_device(self, src_local: str, device: str, dst_path: str) -> None:
        """Copy a file or directory from the local host to the MTP device.

        The copy is always recursive: if *src_local* is a directory, the
        entire tree is uploaded under *dst_path* on the device.

        Args:
            src_local: Local source path (file or directory).
            device:    Device identifier.
            dst_path:  Relative destination path on the device
                       (e.g. ``'Documents'`` or ``'Music/album'``).

        Example::

            client.copy_to_device('/tmp/report.pdf', 'Smini', 'Documents/report.pdf')
        """
        src = Path(src_local)
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src_local}")

        if self.backend == 'kio':
            kio_dst = f"mtp:/{device}/{dst_path}"
            _kio_upload_recursive(src, kio_dst)

        else:  # gvfs
            dst = Path(device) / dst_path
            if src.is_dir():
                print(f"  Uploading directory {src} -> {dst}")
                shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Uploading file {src} -> {dst}")
                shutil.copy2(str(src), str(dst))


# ---------------------------------------------------------------------------
# Quick self-test when run directly
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    client = MTPClient()

    print("\n=== Connected MTP devices ===")
    devices = client.list_devices()
    for dev in devices:
        print(f"  {dev}")

    print("\n=== Root folders per device ===")
    roots = client.list_root_folders()
    for dev, folders in roots.items():
        print(f"  {dev}: {folders}")
