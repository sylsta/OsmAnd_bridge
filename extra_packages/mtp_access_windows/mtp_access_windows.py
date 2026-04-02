"""
mtp_access_windows.py
=====================
MTP device access on Windows using the native Windows Portable Devices (WPD)
COM API via ``comtypes``. No third-party MTP wrapper is required.

This module exposes the same ``MTPClient`` public API as ``mtp_access_kio_gvfs.py``
so that the rest of the plugin can use either backend transparently.

Windows Portable Devices key COM interfaces used:

- ``IPortableDeviceManager``      : enumerate connected devices
- ``IPortableDevice``             : open a device connection
- ``IPortableDeviceContent``      : traverse the object tree
- ``IPortableDeviceProperties``   : read object metadata (name, type, size…)
- ``IPortableDeviceResources``    : read object data (file download)

Object IDs:
    WPD uses opaque string object IDs. The root of every device is
    ``WPD_DEVICE_OBJECT_ID = "DEVICE"``. Children are enumerated via
    ``IPortableDeviceContent.EnumObjects``.

Usage example::

    from mtp_access_windows import MTPClient

    client = MTPClient()
    devices = client.list_devices()          # ['Smini', 'Pixel 9']

    folders = client.list_folder(devices[0], '')        # root folders
    folders = client.list_folder(devices[0], 'Internal storage/DCIM')

    client.copy_from_device_to_exact(
        devices[0],
        'Internal storage/Android/data/net.osmand.plus/files/tracks/rec',
        r'C:\\tmp\\osmand\\tracks\\rec'
    )
"""

import os
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# comtypes / WPD COM setup
# ---------------------------------------------------------------------------
# These imports will raise ImportError on non-Windows or when comtypes is
# absent. The caller (OsmAnd_bridge_import_dialog) guards this with try/except.

import comtypes
import comtypes.client
from comtypes import GUID, HRESULT, IUnknown, COMError
from comtypes.automation import IEnumVARIANT
import ctypes
from ctypes import POINTER, byref, c_ulong, c_wchar_p, c_void_p, wintypes

# ------------------------------------------------------------------
# WPD GUIDs and constants
# ------------------------------------------------------------------

# IPortableDeviceManager  {A1567595-4C2F-4574-A6FA-ECEF917B9A40}
IID_IPortableDeviceManager = GUID("{A1567595-4C2F-4574-A6FA-ECEF917B9A40}")
# IPortableDevice          {625E2DF8-6392-4CF0-9AD1-3CFA5F17775C}
IID_IPortableDevice = GUID("{625E2DF8-6392-4CF0-9AD1-3CFA5F17775C}")
# IPortableDeviceContent   {6A96ED84-7C73-4480-9938-BF5AF477D426}
IID_IPortableDeviceContent = GUID("{6A96ED84-7C73-4480-9938-BF5AF477D426}")
# IPortableDeviceProperties {7F6D695C-03DF-4439-A809-59266BEEE3A6}
IID_IPortableDeviceProperties = GUID("{7F6D695C-03DF-4439-A809-59266BEEE3A6}")
# IPortableDeviceResources  {FD8878AC-D841-4D17-891C-E6829CDB6934}
IID_IPortableDeviceResources = GUID("{FD8878AC-D841-4D17-891C-E6829CDB6934}")
# IPortableDeviceValues     {6848F6F2-3155-4F86-B6F5-263EEAD1EF9E}
IID_IPortableDeviceValues = GUID("{6848F6F2-3155-4F86-B6F5-263EEAD1EF9E}")
# IPortableDeviceKeyCollection {DADA2357-E0AD-492E-98DB-DD61C53BA353}
IID_IPortableDeviceKeyCollection = GUID("{DADA2357-E0AD-492E-98DB-DD61C53BA353}")
# IEnumPortableDeviceObjectIDs {10ECE955-CF41-4728-BFA0-41EEDF1BBF19}
IID_IEnumPortableDeviceObjectIDs = GUID("{10ECE955-CF41-4728-BFA0-41EEDF1BBF19}")
# IStream  (standard)
IID_IStream = GUID("{0000000C-0000-0000-C000-000000000046}")

# CLSID_PortableDeviceManager
CLSID_PortableDeviceManager = GUID("{0AF10CEC-2ECD-4B92-9581-34F6AE0637F3}")
# CLSID_PortableDevice
CLSID_PortableDevice = GUID("{728A21C5-3D9E-48D7-9810-864848F0F404}")
# CLSID_PortableDeviceValues
CLSID_PortableDeviceValues = GUID("{0C15D503-D017-47CE-9016-7B3F978721CC}")
# CLSID_PortableDeviceKeyCollection
CLSID_PortableDeviceKeyCollection = GUID("{DE2D022D-2480-43BE-97F0-D1FA2CF98F4F}")

# WPD root object ID
WPD_DEVICE_OBJECT_ID = "DEVICE"

# WPD property keys (PROPERTYKEY = {fmtid, pid})
# WPD_OBJECT_NAME        {EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C} pid=4
WPD_OBJECT_NAME_FMTID = GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_NAME_PID = 4

# WPD_OBJECT_CONTENT_TYPE {EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C} pid=7
WPD_OBJECT_CONTENT_TYPE_PID = 7

# WPD_CONTENT_TYPE_FOLDER  {27E2E392-A111-48E0-AB0C-E17705A05F85}
WPD_CONTENT_TYPE_FOLDER = GUID("{27E2E392-A111-48E0-AB0C-E17705A05F85}")
# WPD_CONTENT_TYPE_FUNCTIONAL_OBJECT {99ED0160-17FF-4C44-9D98-1D7A6F941921}
WPD_CONTENT_TYPE_FUNCTIONAL_OBJECT = GUID("{99ED0160-17FF-4C44-9D98-1D7A6F941921}")

# WPD_OBJECT_SIZE {EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C} pid=11
WPD_OBJECT_SIZE_PID = 11

# WPD_RESOURCE_DEFAULT {E81E79BE-34F0-41BF-B53F-F1A06AE87842} pid=0
WPD_RESOURCE_DEFAULT_FMTID = GUID("{E81E79BE-34F0-41BF-B53F-F1A06AE87842}")
WPD_RESOURCE_DEFAULT_PID = 0

# STGM constants
STGM_READ = 0x00000000

# Chunk size for file download
_DOWNLOAD_CHUNK = 128 * 1024  # 128 KB


# ---------------------------------------------------------------------------
# Low-level COM helpers
# ---------------------------------------------------------------------------

def _create_portable_device_manager():
    """Instantiate IPortableDeviceManager via COM."""
    return comtypes.client.CreateObject(
        CLSID_PortableDeviceManager,
        interface=comtypes.IUnknown
    ).QueryInterface(comtypes.IUnknown)
    # We use the raw vtable approach below instead of full comtypes interface
    # definition, which would require a large amount of boilerplate.


def _wpd_get_device_ids(mgr_ptr) -> list[str]:
    """Return the list of WPD device ID strings from IPortableDeviceManager."""
    # GetDevices(pPnPDeviceIDs, pcPnPDeviceIDs)
    # First call with NULL to get count
    count = c_ulong(0)
    mgr_ptr.GetDevices(None, byref(count))
    if count.value == 0:
        return []
    # Allocate array of LPWSTR
    DeviceIDs = (c_wchar_p * count.value)()
    mgr_ptr.GetDevices(DeviceIDs, byref(count))
    return [DeviceIDs[i] for i in range(count.value)]


def _wpd_get_friendly_name(mgr_ptr, device_id: str) -> str:
    """Return the friendly name of a WPD device."""
    length = c_ulong(0)
    try:
        mgr_ptr.GetDeviceFriendlyName(device_id, None, byref(length))
        if length.value == 0:
            return device_id
        buf = (ctypes.c_wchar * length.value)()
        mgr_ptr.GetDeviceFriendlyName(device_id, buf, byref(length))
        return buf.value
    except COMError:
        return device_id


# ---------------------------------------------------------------------------
# High-level WPD wrapper
# ---------------------------------------------------------------------------

class _WPDObject:
    """Lightweight descriptor for a WPD object (file or folder)."""

    def __init__(self, object_id: str, name: str, is_folder: bool):
        self.object_id = object_id  # opaque WPD object ID string
        self.name = name            # display name
        self.is_folder = is_folder

    def __repr__(self):
        kind = "dir" if self.is_folder else "file"
        return f"<WPDObject {kind} {self.name!r}>"


class _WPDDevice:
    """Wrapper around an open WPD device connection.

    Provides object-tree traversal and file download using raw COM calls
    via ``comtypes``. No third-party MTP library is used.
    """

    def __init__(self, device_id: str, friendly_name: str):
        self.device_id = device_id
        self.friendly_name = friendly_name
        self._device = None      # IPortableDevice
        self._content = None     # IPortableDeviceContent
        self._properties = None  # IPortableDeviceProperties
        self._open()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def _open(self):
        """Open the device and obtain content/properties interfaces."""
        # Create IPortableDevice
        self._device = comtypes.client.CreateObject(
            CLSID_PortableDevice,
            interface=comtypes.IUnknown
        )
        # Create empty client info (IPortableDeviceValues)
        client_info = comtypes.client.CreateObject(
            CLSID_PortableDeviceValues,
            interface=comtypes.IUnknown
        )
        # Open(pszPnPDeviceID, pClientInfo)
        self._device.Open(self.device_id, client_info)
        # Get IPortableDeviceContent
        content_ptr = POINTER(comtypes.IUnknown)()
        self._device.Content(byref(content_ptr))
        self._content = content_ptr
        # Get IPortableDeviceProperties from content
        props_ptr = POINTER(comtypes.IUnknown)()
        self._content.Properties(byref(props_ptr))
        self._properties = props_ptr

    def close(self):
        """Release the device connection."""
        try:
            if self._device:
                self._device.Close()
        except Exception:
            pass
        self._device = None
        self._content = None
        self._properties = None

    # ------------------------------------------------------------------
    # Object tree traversal
    # ------------------------------------------------------------------

    def _get_object_name(self, object_id: str) -> str:
        """Retrieve the WPD_OBJECT_NAME property of an object."""
        try:
            # Build a key collection for WPD_OBJECT_NAME
            keys = comtypes.client.CreateObject(
                CLSID_PortableDeviceKeyCollection,
                interface=comtypes.IUnknown
            )
            # PROPERTYKEY structure: {fmtid, pid}
            # We use GetValues and read the string variant
            values_ptr = POINTER(comtypes.IUnknown)()
            self._properties.GetValues(object_id, None, byref(values_ptr))
            values = values_ptr

            # GetStringValue(key, pszValue) — use WPD_OBJECT_NAME key
            name_buf = c_wchar_p()
            # Build PROPERTYKEY inline as a structure
            class PROPERTYKEY(ctypes.Structure):
                _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

            pk = PROPERTYKEY()
            pk.fmtid = WPD_OBJECT_NAME_FMTID
            pk.pid = WPD_OBJECT_NAME_PID
            values.GetStringValue(byref(pk), byref(name_buf))
            return name_buf.value or object_id
        except COMError:
            return object_id

    def _is_folder(self, object_id: str) -> bool:
        """Return True if the WPD object is a folder or functional object."""
        try:
            values_ptr = POINTER(comtypes.IUnknown)()
            self._properties.GetValues(object_id, None, byref(values_ptr))
            values = values_ptr

            class PROPERTYKEY(ctypes.Structure):
                _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

            pk = PROPERTYKEY()
            pk.fmtid = WPD_OBJECT_NAME_FMTID
            pk.pid = WPD_OBJECT_CONTENT_TYPE_PID

            guid_val = GUID()
            values.GetGuidValue(byref(pk), byref(guid_val))
            return guid_val in (WPD_CONTENT_TYPE_FOLDER,
                                WPD_CONTENT_TYPE_FUNCTIONAL_OBJECT)
        except COMError:
            return False

    def _list_children(self, parent_id: str) -> list[_WPDObject]:
        """List the direct children of a WPD object."""
        children = []
        try:
            enum_ptr = POINTER(comtypes.IUnknown)()
            self._content.EnumObjects(0, parent_id, None, byref(enum_ptr))
            enum_obj = enum_ptr

            batch = 16
            fetched = c_ulong(0)
            ids_buf = (c_wchar_p * batch)()

            while True:
                try:
                    enum_obj.Next(batch, ids_buf, byref(fetched))
                except COMError:
                    break
                if fetched.value == 0:
                    break
                for i in range(fetched.value):
                    oid = ids_buf[i]
                    name = self._get_object_name(oid)
                    is_dir = self._is_folder(oid)
                    children.append(_WPDObject(oid, name, is_dir))
        except COMError:
            pass
        return children

    def _resolve_path(self, path: str) -> _WPDObject | None:
        """Resolve a slash-separated path to a WPD object, starting from root.

        Args:
            path: Relative path such as ``'Internal storage/DCIM/Camera'``.
                  Empty string resolves to the device root (DEVICE).

        Returns:
            The matching :class:`_WPDObject`, or ``None`` if not found.
        """
        if not path:
            return _WPDObject(WPD_DEVICE_OBJECT_ID, self.friendly_name, True)

        parts = [p for p in path.replace('\\', '/').split('/') if p]
        current_id = WPD_DEVICE_OBJECT_ID

        for part in parts:
            found = None
            for child in self._list_children(current_id):
                if child.name.lower() == part.lower():
                    found = child
                    break
            if found is None:
                return None
            current_id = found.object_id

        return _WPDObject(current_id, parts[-1], self._is_folder(current_id))

    def list_folder(self, path: str) -> list[str]:
        """List the names of children at *path*.

        Args:
            path: Relative path on the device (empty string for root).

        Returns:
            List of child names, or ``[]`` if path not found.
        """
        obj = self._resolve_path(path)
        if obj is None or not obj.is_folder:
            return []
        return [child.name for child in self._list_children(obj.object_id)]

    # ------------------------------------------------------------------
    # File download
    # ------------------------------------------------------------------

    def _download_object(self, object_id: str, dst_file: Path) -> None:
        """Download a single WPD file object to a local path.

        Uses ``IPortableDeviceResources`` and ``IStream`` to stream the
        file content in chunks, avoiding loading the whole file into memory.

        Args:
            object_id: WPD object ID of the file to download.
            dst_file:  Local destination file path.
        """
        resources_ptr = POINTER(comtypes.IUnknown)()
        self._content.Transfer(byref(resources_ptr))
        resources = resources_ptr

        class PROPERTYKEY(ctypes.Structure):
            _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

        pk = PROPERTYKEY()
        pk.fmtid = WPD_RESOURCE_DEFAULT_FMTID
        pk.pid = WPD_RESOURCE_DEFAULT_PID

        optimal_chunk = c_ulong(0)
        stream_ptr = POINTER(comtypes.IUnknown)()
        resources.GetStream(object_id, byref(pk), STGM_READ,
                            byref(optimal_chunk), byref(stream_ptr))
        stream = stream_ptr

        chunk_size = optimal_chunk.value if optimal_chunk.value > 0 else _DOWNLOAD_CHUNK
        buf = (ctypes.c_char * chunk_size)()
        bytes_read = c_ulong(0)

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        with open(dst_file, 'wb') as fh:
            while True:
                try:
                    stream.Read(buf, chunk_size, byref(bytes_read))
                except COMError:
                    break
                if bytes_read.value == 0:
                    break
                fh.write(buf[:bytes_read.value])

    def copy_to_exact(self, src_path: str, dst_exact: Path) -> None:
        """Recursively copy a device path to an exact local destination.

        - If *src_path* is a folder, its contents land directly inside
          *dst_exact* (no extra nesting level).
        - If *src_path* is a file, *dst_exact* is the resulting file path.

        Args:
            src_path:  Relative path on the device.
            dst_exact: Exact local destination path.
        """
        obj = self._resolve_path(src_path)
        if obj is None:
            raise FileNotFoundError(
                f"Path not found on device {self.friendly_name!r}: {src_path!r}"
            )

        if obj.is_folder:
            dst_exact.mkdir(parents=True, exist_ok=True)
            for child in self._list_children(obj.object_id):
                child_dst = dst_exact / child.name
                if child.is_folder:
                    self.copy_to_exact.__func__(
                        self,
                        # rebuild path for recursion via object_id shortcut
                        _OIDPath(child.object_id),
                        child_dst
                    )
                else:
                    print(f"  Downloading {child.name} -> {child_dst}")
                    self._download_object(child.object_id, child_dst)
        else:
            print(f"  Downloading {obj.name} -> {dst_exact}")
            self._download_object(obj.object_id, dst_exact)

    def _copy_subtree_by_id(self, object_id: str, dst: Path) -> None:
        """Recursively copy a subtree identified by WPD object ID.

        This internal method avoids re-resolving the path for each recursive
        call, which would be O(depth²). It works directly with object IDs.

        Args:
            object_id: WPD object ID of the source (file or folder).
            dst:       Exact local destination path.
        """
        is_dir = self._is_folder(object_id)
        if is_dir:
            dst.mkdir(parents=True, exist_ok=True)
            for child in self._list_children(object_id):
                self._copy_subtree_by_id(child.object_id, dst / child.name)
        else:
            print(f"  Downloading -> {dst}")
            self._download_object(object_id, dst)

    def copy_subtree(self, src_path: str, dst_exact: Path) -> None:
        """Public entry point: resolve path then copy subtree efficiently.

        Args:
            src_path:  Relative path on the device.
            dst_exact: Exact local destination.
        """
        obj = self._resolve_path(src_path)
        if obj is None:
            raise FileNotFoundError(
                f"Path not found on device {self.friendly_name!r}: {src_path!r}"
            )
        if obj.is_folder:
            dst_exact.mkdir(parents=True, exist_ok=True)
            for child in self._list_children(obj.object_id):
                self._copy_subtree_by_id(child.object_id, dst_exact / child.name)
        else:
            self._download_object(obj.object_id, dst_exact)


# ---------------------------------------------------------------------------
# Device manager
# ---------------------------------------------------------------------------

def _get_wpd_devices() -> list[tuple[str, str]]:
    """Return list of (device_id, friendly_name) for all connected WPD devices."""
    mgr = comtypes.client.CreateObject(
        CLSID_PortableDeviceManager,
        interface=comtypes.IUnknown
    )

    # GetDevices: first call to get count
    count = c_ulong(0)
    mgr.GetDevices(None, byref(count))
    if count.value == 0:
        return []

    device_ids_arr = (c_wchar_p * count.value)()
    mgr.GetDevices(device_ids_arr, byref(count))

    result = []
    for i in range(count.value):
        dev_id = device_ids_arr[i]
        # GetDeviceFriendlyName: first call to get length
        length = c_ulong(0)
        try:
            mgr.GetDeviceFriendlyName(dev_id, None, byref(length))
            if length.value > 0:
                buf = (ctypes.c_wchar * length.value)()
                mgr.GetDeviceFriendlyName(dev_id, buf, byref(length))
                name = buf.value
            else:
                name = dev_id
        except COMError:
            name = dev_id
        result.append((dev_id, name))
    return result


# ---------------------------------------------------------------------------
# Public MTPClient — same API as mtp_access_kio_gvfs.MTPClient
# ---------------------------------------------------------------------------

class MTPClient:
    """MTP client for Windows using the native WPD COM API.

    Exposes the same public interface as ``mtp_access_kio_gvfs.MTPClient``
    so that calling code is platform-agnostic.

    Device identifiers returned by :meth:`list_devices` are the WPD
    friendly names (e.g. ``'Smini'``, ``'Pixel 9'``). Internally the
    class maps names to WPD device IDs.

    Raises:
        ImportError: if ``comtypes`` is not installed.
        RuntimeError: if no WPD devices are found at instantiation.
    """

    def __init__(self):
        self.backend = 'wpd'
        # Map friendly_name → (device_id, _WPDDevice | None)
        self._registry: dict[str, tuple[str, _WPDDevice | None]] = {}
        raw = _get_wpd_devices()
        for dev_id, name in raw:
            self._registry[name] = (dev_id, None)
        if not self._registry:
            raise RuntimeError(
                "No WPD/MTP devices found. "
                "Make sure the device is connected and unlocked."
            )
        print(f"[MTPClient/WPD] {len(self._registry)} device(s) found: "
              f"{list(self._registry)}")

    def _get_device(self, friendly_name: str) -> _WPDDevice:
        """Return an open _WPDDevice for *friendly_name*, opening it if needed."""
        if friendly_name not in self._registry:
            raise KeyError(f"Unknown device: {friendly_name!r}")
        dev_id, wpd = self._registry[friendly_name]
        if wpd is None:
            wpd = _WPDDevice(dev_id, friendly_name)
            self._registry[friendly_name] = (dev_id, wpd)
        return wpd

    def close_all(self):
        """Close all open device connections."""
        for name, (dev_id, wpd) in self._registry.items():
            if wpd is not None:
                wpd.close()
                self._registry[name] = (dev_id, None)

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_devices(self) -> list[str]:
        """Return friendly names of connected WPD/MTP devices.

        Returns:
            List of device friendly names (e.g. ``['Smini']``).
        """
        return list(self._registry.keys())

    def list_root_folders(self) -> dict[str, list[str]]:
        """Return root-level folders for every connected device.

        Returns:
            Dict mapping device name → list of root folder names.
        """
        return {name: self.list_folder(name, '') for name in self._registry}

    def list_folder(self, device: str, path: str) -> list[str]:
        """List the contents of a folder on a WPD device.

        Args:
            device: Device friendly name.
            path:   Relative path on the device (empty string for root).

        Returns:
            List of child names, or ``[]`` if path not found.
        """
        return self._get_device(device).list_folder(path)

    # ------------------------------------------------------------------
    # Copy: device → host
    # ------------------------------------------------------------------

    def copy_from_device(self, device: str, src_path: str,
                          dst_local: str) -> None:
        """Copy a file or folder from the device into a local directory.

        The result lands at ``dst_local/<basename of src_path>``.
        Use :meth:`copy_from_device_to_exact` for full path control.

        Args:
            device:    Device friendly name.
            src_path:  Relative path on the device.
            dst_local: Local parent directory.

        Example::

            client.copy_from_device('Smini', 'DCIM', r'C:\\tmp\\photos')
            # result: C:\\tmp\\photos\\DCIM\\<files>
        """
        dst_exact = str(Path(dst_local) / Path(src_path).name)
        self.copy_from_device_to_exact(device, src_path, dst_exact)

    def copy_from_device_to_exact(self, device: str, src_path: str,
                                   dst_exact: str) -> None:
        """Copy a file or folder from the device to an exact local path.

        - Folder: contents land directly inside *dst_exact*.
        - File:   *dst_exact* is the resulting file path.

        Args:
            device:    Device friendly name.
            src_path:  Relative path on the device.
            dst_exact: Exact local destination path.

        Example::

            client.copy_from_device_to_exact(
                'Smini',
                'Internal storage/Android/data/net.osmand.plus/files/tracks/rec',
                r'C:\\tmp\\osmand\\tracks\\rec'
            )
            # result: C:\\tmp\\osmand\\tracks\\rec\\2026-01-31.gpx  etc.
        """
        self._get_device(device).copy_subtree(src_path, Path(dst_exact))

    # ------------------------------------------------------------------
    # Copy: host → device
    # ------------------------------------------------------------------

    def copy_to_device(self, src_local: str, device: str,
                        dst_path: str) -> None:
        """Copy a local file or directory to the MTP device.

        Uses ``IPortableDeviceContent.CreateObjectWithPropertiesAndData``
        to upload files. Directories are created recursively.

        Args:
            src_local: Local source path.
            device:    Device friendly name.
            dst_path:  Relative destination path on the device.

        Note:
            Upload support requires the device to allow object creation via
            WPD. Most Android phones in MTP mode support this.
        """
        src = Path(src_local)
        if not src.exists():
            raise FileNotFoundError(f"Source not found: {src_local}")
        wpd = self._get_device(device)
        self._upload_recursive(wpd, src, dst_path)

    def _upload_recursive(self, wpd: _WPDDevice, src: Path,
                           dst_path: str) -> None:
        """Recursively upload *src* to *dst_path* on the device.

        Args:
            wpd:      Open _WPDDevice instance.
            src:      Local file or directory.
            dst_path: Destination path on the device.
        """
        if src.is_file():
            self._upload_file(wpd, src, dst_path)
        elif src.is_dir():
            # Ensure the destination folder exists on the device
            self._ensure_folder(wpd, dst_path)
            for child in src.iterdir():
                child_dst = dst_path.rstrip('/\\') + '/' + child.name
                self._upload_recursive(wpd, child, child_dst)

    def _ensure_folder(self, wpd: _WPDDevice, path: str) -> str:
        """Create *path* on the device if it does not exist.

        Returns the WPD object ID of the (possibly newly created) folder.
        """
        obj = wpd._resolve_path(path)
        if obj is not None:
            return obj.object_id
        # Create the folder via IPortableDeviceContent.CreateObjectWithPropertiesOnly
        parts = path.replace('\\', '/').rstrip('/').rsplit('/', 1)
        parent_path = parts[0] if len(parts) > 1 else ''
        folder_name = parts[-1]
        parent_id = self._ensure_folder(wpd, parent_path)

        props = comtypes.client.CreateObject(
            CLSID_PortableDeviceValues, interface=comtypes.IUnknown)

        class PROPERTYKEY(ctypes.Structure):
            _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

        # WPD_OBJECT_PARENT_ID
        pk_parent = PROPERTYKEY()
        pk_parent.fmtid = GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
        pk_parent.pid = 3
        props.SetStringValue(byref(pk_parent), parent_id)

        # WPD_OBJECT_NAME
        pk_name = PROPERTYKEY()
        pk_name.fmtid = WPD_OBJECT_NAME_FMTID
        pk_name.pid = WPD_OBJECT_NAME_PID
        props.SetStringValue(byref(pk_name), folder_name)

        # WPD_OBJECT_CONTENT_TYPE = WPD_CONTENT_TYPE_FOLDER
        pk_ct = PROPERTYKEY()
        pk_ct.fmtid = WPD_OBJECT_NAME_FMTID
        pk_ct.pid = WPD_OBJECT_CONTENT_TYPE_PID
        props.SetGuidValue(byref(pk_ct), byref(WPD_CONTENT_TYPE_FOLDER))

        new_id_buf = c_wchar_p()
        wpd._content.CreateObjectWithPropertiesOnly(
            props, byref(new_id_buf))
        return new_id_buf.value

    def _upload_file(self, wpd: _WPDDevice, src: Path, dst_path: str) -> None:
        """Upload a single local file to the device.

        Args:
            wpd:      Open _WPDDevice instance.
            src:      Local file to upload.
            dst_path: Destination path on the device (including filename).
        """
        parts = dst_path.replace('\\', '/').rstrip('/').rsplit('/', 1)
        parent_path = parts[0] if len(parts) > 1 else ''
        file_name = parts[-1]
        parent_id = self._ensure_folder(wpd, parent_path)

        file_size = src.stat().st_size

        props = comtypes.client.CreateObject(
            CLSID_PortableDeviceValues, interface=comtypes.IUnknown)

        class PROPERTYKEY(ctypes.Structure):
            _fields_ = [("fmtid", GUID), ("pid", c_ulong)]

        pk_parent = PROPERTYKEY()
        pk_parent.fmtid = GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
        pk_parent.pid = 3
        props.SetStringValue(byref(pk_parent), parent_id)

        pk_name = PROPERTYKEY()
        pk_name.fmtid = WPD_OBJECT_NAME_FMTID
        pk_name.pid = WPD_OBJECT_NAME_PID
        props.SetStringValue(byref(pk_name), file_name)

        pk_size = PROPERTYKEY()
        pk_size.fmtid = WPD_OBJECT_NAME_FMTID
        pk_size.pid = WPD_OBJECT_SIZE_PID
        props.SetUnsignedLargeIntegerValue(byref(pk_size), file_size)

        optimal_chunk = c_ulong(0)
        stream_ptr = POINTER(comtypes.IUnknown)()
        wpd._content.CreateObjectWithPropertiesAndData(
            props, byref(stream_ptr), byref(optimal_chunk), None)
        stream = stream_ptr

        chunk_size = optimal_chunk.value if optimal_chunk.value > 0 else _DOWNLOAD_CHUNK
        written = c_ulong(0)
        with open(src, 'rb') as fh:
            while True:
                data = fh.read(chunk_size)
                if not data:
                    break
                buf = (ctypes.c_char * len(data))(*data)
                stream.Write(buf, len(data), byref(written))
        stream.Commit(0)
        print(f"  Uploaded {src} -> {dst_path}")


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    client = MTPClient()

    print("\n=== Connected WPD/MTP devices ===")
    for dev in client.list_devices():
        print(f"  {dev}")

    print("\n=== Root folders per device ===")
    for dev, folders in client.list_root_folders().items():
        print(f"  {dev}: {folders}")
