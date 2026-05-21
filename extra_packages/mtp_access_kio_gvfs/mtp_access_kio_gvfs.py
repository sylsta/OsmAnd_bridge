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
import shutil
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------

def detect_backend() -> str | None:
    """Detect which MTP backend is running on the system.

    Checks KIO (kiod5) first, then gvfs. For gvfs, the daemon
    ``gvfsd-mtp`` may be running even when no device is yet mounted in the
    filesystem — :func:`_gvfs_mtp_mounts` handles mounting automatically.

    Returns:
        ``'kio'``, ``'gvfs'``, or ``None`` if no backend is found.
    """
    # KIO: kiod5 process owns the MTP device
    result = subprocess.run(['pgrep', '-a', 'kiod5'], capture_output=True, text=True)
    if result.stdout.strip():
        return 'kio'

    # gvfs: gvfsd-mtp daemon running, or device already visible in gvfsd dir
    result = subprocess.run(['pgrep', '-a', 'gvfsd-mtp'], capture_output=True, text=True)
    if result.stdout.strip():
        return 'gvfs'

    # gvfs fallback: daemon not running but mounts may already exist
    # (can happen when gvfsd-mtp exited after mounting)
    if _gvfs_mtp_mounts():
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
# gio helpers (gvfs without filesystem mount — GDaemonMount via D-Bus)
# ---------------------------------------------------------------------------

def _gio_ls(uri: str) -> list[str]:
    """List entries at a gvfs URI using ``gio list``.

    Works even when the device is not mounted as a FUSE filesystem (i.e.
    accessible via ``mtp://...`` URIs through D-Bus only).

    Args:
        uri: gvfs URI such as ``mtp://SAMSUNG_.../Stockage interne/``.

    Returns:
        List of entry names, filtering out empty lines.
    """
    result = subprocess.run(['gio', 'list', uri],
                            capture_output=True, text=True)
    return [line.strip() for line in result.stdout.splitlines()
            if line.strip()]


def _gio_is_dir(uri: str) -> bool:
    """Return True if a gvfs URI points to a directory.

    Uses ``gio info`` and checks ``standard::type``:
    - type 2 = G_FILE_TYPE_DIRECTORY
    - type 1 = G_FILE_TYPE_REGULAR

    Args:
        uri: gvfs URI to test.

    Returns:
        ``True`` if directory, ``False`` otherwise.
    """
    result = subprocess.run(['gio', 'info', uri],
                            capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'standard::type:' in line:
            try:
                return int(line.split(':')[-1].strip()) == 2
            except ValueError:
                pass
    return False


def _gio_copy_into(src_uri: str, dst_local: Path) -> None:
    """Recursively copy the *contents* of a gvfs URI directory into a local path.

    Each child of ``src_uri`` is placed directly inside ``dst_local``:
    - files → ``dst_local/<filename>``
    - dirs  → recurse into ``dst_local/<dirname>/``

    Args:
        src_uri:   gvfs URI of the source directory.
        dst_local: Local directory that receives the contents.
    """
    dst_local.mkdir(parents=True, exist_ok=True)
    entries = _gio_ls(src_uri.rstrip('/') + '/')

    for entry in entries:
        # URI-encode spaces and special chars minimally (gvfs handles most)
        child_uri = src_uri.rstrip('/') + '/' + entry
        child_local = dst_local / entry

        if _gio_is_dir(child_uri):
            _gio_copy_into(child_uri, child_local)
        else:
            print(f"  Copying {child_uri} -> {child_local}")
            subprocess.run(
                ['gio', 'copy', child_uri, str(child_local)],
                check=True
            )


def _gio_upload_recursive(src_local: Path, dst_uri: str) -> None:
    """Recursively upload a local file or directory to a gvfs URI.

    Args:
        src_local: Local path to upload.
        dst_uri:   Destination gvfs URI.
    """
    if src_local.is_file():
        print(f"  Uploading {src_local} -> {dst_uri}")
        subprocess.run(['gio', 'copy', str(src_local), dst_uri], check=True)
    elif src_local.is_dir():
        for child in src_local.iterdir():
            _gio_upload_recursive(child, dst_uri.rstrip('/') + '/' + child.name)


# ---------------------------------------------------------------------------
# gvfs helpers
# ---------------------------------------------------------------------------

def _gvfs_try_mount_devices() -> None:
    """Attempt to mount all unmounted MTP devices visible to gvfs.

    Uses ``gio mount -l`` to find MTP volumes that are detected but not yet
    mounted, then mounts each one via ``udevadm`` + ``gio mount``.
    This is needed because gvfs-detected devices only appear in the gvfsd
    directory after an explicit mount.
    """
    try:
        # Find MTP devices via udevadm (works regardless of desktop environment)
        result = subprocess.run(['udevadm', 'info', '--export-db'],
                                capture_output=True, text=True)
        current_block: list[str] = []
        for line in result.stdout.splitlines() + ['']:
            if line == '':
                block = chr(10).join(current_block)
                if 'ID_MTP_DEVICE=1' in block and 'DEVTYPE=usb_device' in block:
                    props: dict[str, str] = {}
                    for line_block in current_block:
                        if line_block.startswith('E: '):
                            k, _, v = line_block[3:].partition('=')
                            props[k] = v
                    bus = props.get('BUSNUM', '').zfill(3)
                    dev = props.get('DEVNUM', '').zfill(3)
                    if bus and dev:
                        uri = f'mtp://[usb:{bus},{dev}]/'
                        subprocess.run(['gio', 'mount', uri],
                                       capture_output=True, text=True)
                current_block = []
            else:
                current_block.append(line)
    except Exception:
        pass


def _gvfs_is_listable(path: Path) -> bool:
    """Return True if *path* can actually be listed without error.

    ``exists()`` / ``is_dir()`` raise OSError errno 107 (ENOTCONN) on stale
    FUSE/gvfs mounts. Only ``os.listdir()`` tells us whether the path is
    truly usable.

    Args:
        path: Path to test.

    Returns:
        ``True`` only if ``os.listdir(path)`` succeeds.
    """
    try:
        os.listdir(path)
        return True
    except OSError:
        return False


def _gvfs_all_bases() -> list[Path]:
    """Return all listable gvfs mount directories for the current user.

    Different desktop environments use different directory names:
    - GNOME / Ubuntu : ``/run/user/<uid>/gvfs/``
    - XFCE / others  : ``/run/user/<uid>/gvfsd/``
    - Some systems   : both may exist

    All variants that are actually listable are returned (not just the first).

    Returns:
        List of listable :class:`pathlib.Path` directories (may be empty).
    """
    uid = os.getuid()
    result = []
    for name in ('gvfs', 'gvfsd'):
        p = Path(f"/run/user/{uid}/{name}/")
        if _gvfs_is_listable(p):
            result.append(p)
    return result


def _gvfs_base() -> Path | None:
    """Return the first listable gvfs mount root (for backward compat).

    Returns:
        A :class:`pathlib.Path` or ``None`` if none is usable.
    """
    bases = _gvfs_all_bases()
    return bases[0] if bases else None


def _gvfs_list_mtp_uris() -> list[str]:
    """Return MTP URIs of all devices detected or mounted by gvfs.

    Parses ``gio mount -l`` output looking for:
    - ``Mount(N): name -> mtp://...``  (already mounted)
    - ``Volume(N): name / Type: GProxyVolumeMonitorMTP`` (detected, not mounted)

    For unmounted volumes, :func:`_gvfs_mount_all_mtp` must be called first.
    This function is the authoritative source because ``gvfsd/mtp*`` only
    appears after FUSE mount, which may never happen for GDaemonMount devices.

    Returns:
        List of unique ``mtp://...`` URI strings.
    """
    try:
        result = subprocess.run(['gio', 'mount', '-l'],
                                capture_output=True, text=True)
        uris: list[str] = []
        for line in result.stdout.splitlines():
            stripped = line.strip()
            # Any line with "-> mtp://" contains a mounted MTP URI
            if '->' in stripped and 'mtp://' in stripped:
                uri = 'mtp://' + stripped.split('mtp://')[1].strip()
                if uri not in uris:
                    uris.append(uri)
        return uris
    except Exception:
        return []


def _gvfs_get_display_name(uri: str) -> str:
    """Return the display name of a gvfs MTP device from its URI.

    Uses ``gio info`` to read ``standard::display-name``.
    The output line looks like::

        standard::display-name: SylTab

    so we split on ``standard::display-name:`` and take the right part.

    Args:
        uri: gvfs MTP URI (e.g. ``mtp://SAMSUNG_.../``).

    Returns:
        Display name (e.g. ``'SylTab'``) or the raw URI if not found.
    """
    try:
        result = subprocess.run(['gio', 'info', uri],
                                capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if 'standard::display-name:' in line:
                # Line format: "  standard::display-name: SylTab"
                # Split on the key including its colon to get only the value.
                return line.split('standard::display-name:')[1].strip()
    except Exception:
        pass
    return uri


def _gvfs_mount_all_mtp() -> None:
    """Mount all MTP devices detected by gvfs but not yet mounted.

    Strategy 1: use ``gio mount -l`` to find already-known URIs and mount them.
    Strategy 2: use ``udevadm`` to find MTP USB devices by BUSNUM/DEVNUM
                and build ``mtp://[usb:BUS,DEV]/`` URIs directly.

    Both strategies call ``gio mount <uri>`` which is idempotent (safe to
    call on already-mounted devices).
    """
    uris: set[str] = set()

    # Strategy 1: URIs from gio mount -l (already-known volumes)
    try:
        result = subprocess.run(['gio', 'mount', '-l'],
                                capture_output=True, text=True)
        in_mtp = False
        for line in result.stdout.splitlines():
            s = line.strip()
            if 'GProxyVolumeMonitorMTP' in s:
                in_mtp = True
            elif in_mtp:
                # Mounted volumes show "Mount(N): name -> mtp://..."
                if '->' in s and 'mtp://' in s:
                    uri = 'mtp://' + s.split('mtp://')[1].strip()
                    uris.add(uri)
                    in_mtp = False
                elif s == '' or s.startswith('Drive') or s.startswith('Volume'):
                    in_mtp = False
    except Exception:
        pass

    # Strategy 2: USB bus/device numbers from udevadm
    try:
        result = subprocess.run(['udevadm', 'info', '--export-db'],
                                capture_output=True, text=True)
        block: list[str] = []
        for line in result.stdout.splitlines() + ['']:
            if line == '':
                text = chr(10).join(block)
                if 'ID_MTP_DEVICE=1' in text and 'DEVTYPE=usb_device' in text:
                    props: dict[str, str] = {}
                    for bl in block:
                        if bl.startswith('E: '):
                            k, _, v = bl[3:].partition('=')
                            props[k] = v
                    bus = props.get('BUSNUM', '').zfill(3)
                    dev = props.get('DEVNUM', '').zfill(3)
                    if bus and dev:
                        uris.add(f'mtp://[usb:{bus},{dev}]/')
                block = []
            else:
                block.append(line)
    except Exception:
        pass

    # Mount all found URIs
    for uri in uris:
        try:
            subprocess.run(['gio', 'mount', uri],
                           capture_output=True, text=True, timeout=10)
        except Exception:
            pass


def _gvfs_scan_mtp_in_bases(bases: list[Path]) -> list[Path]:
    """Scan a list of gvfs base directories for MTP mount points.

    MTP mount points can be named:
    - ``mtp:host=SAMSUNG_...``      (GNOME, unencoded)
    - ``mtp:host%3DSAMSUNG_...``    (URL-encoded variant)
    - ``mtp:[usb:003,022]``         (USB bus/device format)

    All entries whose name starts with ``mtp`` and that are listable
    are returned.

    Args:
        bases: List of candidate gvfs base directories.

    Returns:
        List of listable MTP mount :class:`pathlib.Path` objects.
    """
    mounts: list[Path] = []
    for base in bases:
        try:
            for entry in base.iterdir():
                if entry.name.startswith('mtp') and _gvfs_is_listable(entry):
                    mounts.append(entry)
        except OSError:
            pass
    return mounts


def _gvfs_mtp_mounts() -> list[Path]:
    """Return paths to all MTP devices currently mounted in any gvfs directory.

    Scans all known gvfs base directories (``gvfs``, ``gvfsd``). If nothing
    is found, attempts to trigger mounting via :func:`_gvfs_mount_all_mtp`
    and rescans.

    Returns:
        List of :class:`pathlib.Path` objects, one per mounted MTP device.
    """
    bases = _gvfs_all_bases()
    mounts = _gvfs_scan_mtp_in_bases(bases)
    if mounts:
        return mounts

    # Nothing found — try to trigger mounting and rescan
    _gvfs_mount_all_mtp()
    bases = _gvfs_all_bases()
    return _gvfs_scan_mtp_in_bases(bases)


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

        For KIO : short device names (e.g. ``'Smini'``).
        For gvfs: ``mtp://...`` URIs as reported by ``gio mount -l``.
                  These work whether the device is mounted as a FUSE
                  filesystem or only as a GDaemonMount (D-Bus only).

        Returns:
            List of device identifiers.
        """
        if self.backend == 'kio':
            return _kio_ls('mtp:/')
        # gvfs strategy:
        # 1. Prefer FUSE filesystem mounts (gvfs/ or gvfsd/) — direct path access,
        #    works on GNOME Ubuntu (gvfs/mtp:host=...) and XFCE (gvfsd/mtp:...)
        # 2. Fall back to mtp:// URIs via gio — works when device is a GDaemonMount
        #    (D-Bus only, no FUSE mount), seen on some GNOME/Wayland setups
        mounts = _gvfs_mtp_mounts()
        if mounts:
            return [str(p) for p in mounts]
        return _gvfs_list_mtp_uris()

    def get_display_name(self, device: str) -> str:
        """Return a human-readable name for a device identifier.

        For KIO              : the device name is already human-readable.
        For gvfs (URI)       : reads ``standard::display-name`` via ``gio info``.
        For gvfs (FUSE path) : reads display name via ``gio info`` on the
                               equivalent ``mtp://`` URI, extracted from the
                               path name (e.g. ``mtp:host=SAMSUNG_...``
                               → ``mtp://SAMSUNG_.../``).

        Args:
            device: Device identifier as returned by :meth:`list_devices`.

        Returns:
            Display name string, falling back to the basename of the path.
        """
        if self.backend == 'kio':
            return device
        if device.startswith('mtp://'):
            return _gvfs_get_display_name(device)
        # FUSE path: extract device name from directory name
        # e.g. /run/user/1000/gvfs/mtp:host=SAMSUNG_SAMSUNG_Android_R5GYB0ALMGV
        # → try gio info on the equivalent URI first
        dir_name = Path(device).name  # e.g. "mtp:host=SAMSUNG_..."
        if dir_name.startswith('mtp:host='):
            host = dir_name[len('mtp:host='):]
            uri = f'mtp://{host}/'
            name = _gvfs_get_display_name(uri)
            if name != uri:
                return name
        # Final fallback: use the host part of the directory name
        for prefix in ('mtp:host=', 'mtp:host%3D'):
            if dir_name.startswith(prefix):
                return dir_name[len(prefix):]
        return Path(device).name

    def list_root_folders(self) -> dict[str, list[str]]:
        """Return root-level folders for every connected device.

        Returns:
            Dict mapping device identifier → list of folder names.
        """
        return {dev: self.list_folder(dev, '') for dev in self.list_devices()}

    def list_folder(self, device: str, path: str) -> list[str]:
        """List the contents of a folder on an MTP device.

        Args:
            device: Device identifier. For gvfs this is a ``mtp://`` URI.
            path:   Relative path on the device (empty string for root).

        Returns:
            List of entry names, or ``[]`` if the path does not exist.
        """
        if self.backend == 'kio':
            kio_path = f"mtp:/{device}/{path}" if path else f"mtp:/{device}"
            return _kio_ls(kio_path)

        # gvfs: use filesystem access for FUSE mounts, gio for GDaemonMount URIs
        if device.startswith('mtp://'):
            # GDaemonMount (D-Bus) — use gio
            uri = device.rstrip('/')
            if path:
                uri = uri + '/' + path
            return _gio_ls(uri + '/')
        # FUSE mount — direct filesystem access
        full_path = Path(device) / path if path else Path(device)
        try:
            return os.listdir(full_path)
        except OSError as exc:
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

    def copy_from_device_to_exact(self, device: str, src_path: str, dst_exact: str) -> None:
        """Copy a file or directory from the device to an exact local path.

        - Directory: contents are placed *inside* ``dst_exact``
          (``dst_exact`` itself is created if needed).
        - File: ``dst_exact`` is the resulting file path.

        Args:
            device:    Device identifier. For gvfs: ``mtp://`` URI.
            src_path:  Relative path on the device.
            dst_exact: Exact local destination path.

        Example::

            client.copy_from_device_to_exact(
                'mtp://SAMSUNG_SAMSUNG_Android_R5GYB0ALMGV/',
                'Stockage interne/Android/data/net.osmand.plus/files/tracks/rec',
                '/tmp/osmand/tracks/rec'
            )
            # → /tmp/osmand/tracks/rec/2026-01-31.gpx  etc.
        """
        dst = Path(dst_exact)

        if self.backend == 'kio':
            kio_src = f"mtp:/{device}/{src_path}"
            if _kio_is_dir(kio_src):
                _kio_copy_into(kio_src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                print(f"  Copying {kio_src} -> {dst}")
                subprocess.run(
                    ['kioclient5', 'copy', kio_src, str(dst)],
                    check=True
                )

        else:  # gvfs
            if device.startswith('mtp://'):
                # GDaemonMount (D-Bus only) — use gio
                uri = device.rstrip('/') + '/' + src_path
                if _gio_is_dir(uri):
                    _gio_copy_into(uri, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    print(f"  Copying {uri} -> {dst}")
                    subprocess.run(['gio', 'copy', uri, str(dst)], check=True)
            else:
                # FUSE mount — direct filesystem access (faster, more reliable)
                src = Path(device) / src_path
                if src.is_dir():
                    shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    print(f"  Copying {src} -> {dst}")
                    shutil.copy2(str(src), str(dst))

    # ------------------------------------------------------------------
    # Copy: host → device
    # ------------------------------------------------------------------

    def copy_to_device(self, src_local: str, device: str, dst_path: str) -> None:
        """Copy a file or directory from the host to the MTP device.

        Args:
            src_local: Local source path.
            device:    Device identifier. For gvfs: ``mtp://`` URI.
            dst_path:  Relative destination path on the device.

        Example::

            client.copy_to_device('/tmp/report.pdf',
                                  'mtp://SAMSUNG_.../',
                                  'Stockage interne/Documents/report.pdf')
        """
        src = Path(src_local)
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src_local}")

        if self.backend == 'kio':
            _kio_upload_recursive(src, f"mtp:/{device}/{dst_path}")
        else:  # gvfs
            if device.startswith('mtp://'):
                # GDaemonMount — use gio
                dst_uri = device.rstrip('/') + '/' + dst_path
                _gio_upload_recursive(src, dst_uri)
            else:
                # FUSE mount — direct filesystem access
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
