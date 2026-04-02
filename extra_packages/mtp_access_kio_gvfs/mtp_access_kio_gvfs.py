"""
mtp_access_kio_gvfs.py
======================
A cross-backend Python module for accessing MTP (Media Transfer Protocol) devices
on Linux, supporting both KDE (KIO/kiod5) and GNOME (gvfs) environments.

Backends:
    - KIO  : KDE Plasma, files accessed via ``kioclient5`` CLI
    - gvfs : GNOME/GTK, files mounted under /run/user/.../gvfsd/

Usage example::

    from mtp_access_kio_gvfs import MTPClient

    client = MTPClient()
    devices = client.list_devices()

    # Copy files/tracks/rec  →  /tmp/osmand/tracks/rec/<gpx files>
    client.copy_from_device_to_exact(
        devices[0],
        'Espace de stockage interne partagé/Android/data/net.osmand.plus/files/tracks/rec',
        '/tmp/osmand/tracks/rec'
    )
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
        path: KIO URI such as ``mtp:/Smini/DCIM/``.

    Returns:
        List of entry names.
    """
    result = subprocess.run(['kioclient5', 'ls', path], capture_output=True, text=True)
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() not in ('.', '..')
    ]


def _kio_is_dir(kio_path: str) -> bool:
    """Determine whether a KIO MTP path is a directory.

    Uses ``kioclient5 stat`` and checks FILE_TYPE:
    - ``0040000`` (octal) = directory
    - ``0100000`` (octal) = regular file

    Args:
        kio_path: KIO URI without trailing slash.

    Returns:
        ``True`` if directory, ``False`` if file or on error.
    """
    result = subprocess.run(
        ['kioclient5', 'stat', kio_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        if 'FILE_TYPE' in line:
            # directory: octal 0040000 → decimal 16384
            # regular file: octal 0100000 → decimal 32768
            parts = line.split()
            if len(parts) >= 2:
                try:
                    file_type = int(parts[-1], 8)  # parse as octal
                    return file_type == 0o040000
                except ValueError:
                    pass
    return False


def _kio_copy_into(src_kio: str, dst_local: Path) -> None:
    """Recursively copy the *contents* of a KIO directory into a local directory.

    Each child of ``src_kio`` is copied directly inside ``dst_local``:
    - files    → ``dst_local/<filename>``
    - dirs     → recurse into ``dst_local/<dirname>/``

    Args:
        src_kio:   KIO URI of the source directory.
        dst_local: Local directory that receives the contents.
    """
    dst_local.mkdir(parents=True, exist_ok=True)
    entries = _kio_ls(src_kio + '/')

    for entry in entries:
        child_kio = f"{src_kio}/{entry}"
        child_local = dst_local / entry

        if _kio_is_dir(child_kio):
            _kio_copy_into(child_kio, child_local)
        else:
            print(f"  Copying {child_kio} -> {child_local}")
            subprocess.run(
                ['kioclient5', 'copy', child_kio, str(child_local)],
                check=True
            )


def _kio_upload_recursive(src_local: Path, dst_kio: str) -> None:
    """Recursively upload a local file or directory to a KIO MTP path.

    Args:
        src_local: Local path to copy.
        dst_kio:   Destination KIO URI.
    """
    if src_local.is_file():
        print(f"  Uploading {src_local} -> {dst_kio}")
        subprocess.run(['kioclient5', 'copy', str(src_local), dst_kio], check=True)
    elif src_local.is_dir():
        for child in src_local.iterdir():
            _kio_upload_recursive(child, f"{dst_kio}/{child.name}")


# ---------------------------------------------------------------------------
# gvfs helpers
# ---------------------------------------------------------------------------

def _gvfs_base() -> Path:
    """Return the gvfs mount root for the current user."""
    return Path(f"/run/user/{os.getuid()}/gvfsd/")


def _gvfs_mtp_mounts() -> list[Path]:
    """Find all mounted MTP devices under gvfsd."""
    return [Path(p) for p in glob.glob(str(_gvfs_base() / "mtp*"))]


# ---------------------------------------------------------------------------
# Main client class
# ---------------------------------------------------------------------------

class MTPClient:
    """Unified MTP client supporting KIO (KDE) and gvfs (GNOME) backends.

    Device identifier meaning by backend:

    - **KIO**  : short device name from ``kioclient5 ls mtp:/``  (e.g. ``'Smini'``)
    - **gvfs** : full mount-point path under ``/run/user/.../gvfsd/``

    Raises:
        RuntimeError: if no MTP backend is detected.
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
        """Return connected MTP device identifiers.

        Returns:
            List of device names (KIO) or mount-point paths (gvfs).
        """
        if self.backend == 'kio':
            return _kio_ls('mtp:/')
        return [str(p) for p in _gvfs_mtp_mounts()]

    def list_root_folders(self) -> dict[str, list[str]]:
        """Return root-level folders for every connected device.

        Returns:
            Dict mapping device identifier → list of folder names.
        """
        return {dev: self.list_folder(dev, '') for dev in self.list_devices()}

    def list_folder(self, device: str, path: str) -> list[str]:
        """List the contents of a folder on an MTP device.

        Args:
            device: Device identifier.
            path:   Relative path on the device (empty string for root).

        Returns:
            List of entry names, or ``[]`` if the path does not exist.
        """
        if self.backend == 'kio':
            kio_path = f"mtp:/{device}/{path}" if path else f"mtp:/{device}"
            return _kio_ls(kio_path)

        full_path = Path(device) / path if path else Path(device)
        try:
            return os.listdir(full_path)
        except (PermissionError, FileNotFoundError) as exc:
            print(f"[MTPClient] Cannot list {full_path}: {exc}")
            return []

    # ------------------------------------------------------------------
    # Copy: device → host
    # ------------------------------------------------------------------

    def copy_from_device(self, device: str, src_path: str, dst_local: str) -> None:
        """Copy a file or directory from the device into a local directory.

        The result lands at ``dst_local/<basename of src_path>``.
        Use :meth:`copy_from_device_to_exact` for full path control.

        Args:
            device:    Device identifier.
            src_path:  Relative path on the device.
            dst_local: Local parent directory.

        Example::

            client.copy_from_device('Smini', 'DCIM', '/tmp/photos')
            # → /tmp/photos/DCIM/<files>
        """
        dst_exact = str(Path(dst_local) / Path(src_path).name)
        self.copy_from_device_to_exact(device, src_path, dst_exact)

    def copy_from_device_to_exact(self, device: str, src_path: str,
                                   dst_exact: str) -> None:
        """Copy a file or directory from the device to an exact local path.

        - Directory: contents are placed *inside* ``dst_exact``
          (``dst_exact`` itself is created if needed).
        - File: ``dst_exact`` is the resulting file path.

        Args:
            device:    Device identifier.
            src_path:  Relative path on the device.
            dst_exact: Exact local destination path.

        Example::

            client.copy_from_device_to_exact(
                'Smini',
                'Espace de stockage interne partagé/…/files/tracks/rec',
                '/tmp/osmand/tracks/rec'
            )
            # → /tmp/osmand/tracks/rec/2026-01-31.gpx  etc.
        """
        dst = Path(dst_exact)

        if self.backend == 'kio':
            kio_src = f"mtp:/{device}/{src_path}"
            if _kio_is_dir(kio_src):
                # Copy contents of kio_src directly into dst
                _kio_copy_into(kio_src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Copying {kio_src} -> {dst}")
                subprocess.run(
                    ['kioclient5', 'copy', kio_src, str(dst)],
                    check=True
                )

        else:  # gvfs
            src = Path(device) / src_path
            if src.is_dir():
                shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))

    # ------------------------------------------------------------------
    # Copy: host → device
    # ------------------------------------------------------------------

    def copy_to_device(self, src_local: str, device: str, dst_path: str) -> None:
        """Copy a file or directory from the host to the MTP device.

        Args:
            src_local: Local source path.
            device:    Device identifier.
            dst_path:  Relative destination path on the device.

        Example::

            client.copy_to_device('/tmp/report.pdf', 'Smini', 'Documents/report.pdf')
        """
        src = Path(src_local)
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src_local}")

        if self.backend == 'kio':
            _kio_upload_recursive(src, f"mtp:/{device}/{dst_path}")
        else:
            dst = Path(device) / dst_path
            if src.is_dir():
                shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    client = MTPClient()

    print("\n=== Connected MTP devices ===")
    for dev in client.list_devices():
        print(f"  {dev}")

    print("\n=== Root folders per device ===")
    for dev, folders in client.list_root_folders().items():
        print(f"  {dev}: {folders}")
