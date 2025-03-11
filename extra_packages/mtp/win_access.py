"""
A module to access Mobile Devices from Windows via USB connection.

Author:  Heribert Füchtenhans

Version: 2025.3.10

Implements access to basic functions of the Windows WPD API
Yes I know, there are a lot of pylint disable and type ignors :-)
For examples please look into the tests directory.

Requirements:
OS:
    Windows 10
    Windows 11
Python: 
    comtypes

The module contains the following functions:

- 'get_portable_devices' Get all attached portable devices.
- 'get_content_from_device_path' - Get the content of a path.
- 'walk' - Iterates ower all files in a tree.
- 'makedirs' - Creates the directories on the MTP device if they don't exist.

The module contains the following classes:

- 'PortableDeviceContent' - Class for one file, directory or storage
- 'PortableDevice' - Class for one portable device found connected

All functions through IOError when a communication fails.

Examples:
    >>> import mtp.win_access
    >>> mtp.win_access.get_portable_devices()
    [<PortableDevice: ('HSG1316', 'HSG1316')>]
"""

import ctypes
import datetime
import io
import os
import os.path
import sys
from typing import Any, IO, Callable, Generator, List, Optional, Tuple
import contextlib
import comtypes  # type: ignore # pylint: disable=import-error
import comtypes.client  # type: ignore # pylint: disable=import-error
import comtypes.automation  # type: ignore # pylint: disable=import-error

gen_dir = os.path.join(os.path.dirname(__file__), "comtype_gen_win_wpd")
comtypes.client.gen_dir = gen_dir
# The following lines are only neccessary if a new typelib file must be created
# if not os.path.exists(gen_dir) and not hasattr(sys, "frozen"):
#     os.makedirs(gen_dir)
#     comtypes.client.GetModule("portabledeviceapi.dll")
#     comtypes.client.GetModule("portabledevicetypes.dll")
#     from . import modify_comtypes
#     modify_comtypes.modify_generated_files(comtypes.client.gen_dir)  # type: ignore

from . comtype_gen_win_wpd import PortableDeviceApiLib as port  # pylint: disable=all # type: ignore
from . comtype_gen_win_wpd import PortableDeviceTypesLib as types  # pylint: disable=all # type: ignore


# ComType Verweise anlegen
WPD_RESOURCE_DEFAULT = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_RESOURCE_DEFAULT.contents.fmtid = comtypes.GUID("{E81E79BE-34F0-41BF-B53F-F1A06AE87842}")
WPD_RESOURCE_DEFAULT.contents.pid = 0

# ---------
WPD_OBJECT_NAME = comtypes.pointer(port._tagpropertykey())  # pylint: disable=no-member, protected-access # type: ignore
WPD_OBJECT_NAME.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_NAME.contents.pid = 4

# ---------
WPD_STORAGE_CAPACITY = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_STORAGE_CAPACITY.contents.fmtid = comtypes.GUID("{01A3057A-74D6-4E80-BEA7-DC4C212CE50A}")
WPD_STORAGE_CAPACITY.contents.pid = 4

# ---------
WPD_STORAGE_FREE_SPACE_IN_BYTES = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_STORAGE_FREE_SPACE_IN_BYTES.contents.fmtid = comtypes.GUID("{01A3057A-74D6-4E80-BEA7-DC4C212CE50A}")
WPD_STORAGE_FREE_SPACE_IN_BYTES.contents.pid = 5

# ---------
WPD_DEVICE_SERIAL_NUMBER = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_DEVICE_SERIAL_NUMBER.contents.fmtid = comtypes.GUID("{26D4979A-E643-4626-9E2B-736DC0C92FDC}")
WPD_DEVICE_SERIAL_NUMBER.contents.pid = 9
#  0x26D4979A, 0xE643, 0x4626, 0x9E, 0x2B, 0x73, 0x6D, 0xC0, 0xC9, 0x2F, 0xDC ,  9

# ---------
WPD_OBJECT_PARENT_ID = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_OBJECT_PARENT_ID.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_PARENT_ID.contents.pid = 3

# ---------
WPD_OBJECT_CONTENT_TYPE = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_OBJECT_CONTENT_TYPE.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_CONTENT_TYPE.contents.pid = 7


# ---------
WPD_OBJECT_SIZE = comtypes.pointer(port._tagpropertykey())  # pylint: disable=no-member, protected-access # type: ignore
WPD_OBJECT_SIZE.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_SIZE.contents.pid = 11

# ---------
WPD_OBJECT_ORIGINAL_FILE_NAME = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_OBJECT_ORIGINAL_FILE_NAME.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_ORIGINAL_FILE_NAME.contents.pid = 12

# ---------
WPD_OBJECT_DATE_CREATED = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_OBJECT_DATE_CREATED.contents.fmtid = comtypes.GUID("{ef6b490d-5cd8-437a-affc-da8b60ee4a3c}")
WPD_OBJECT_DATE_CREATED.contents.pid = 18

# ---------
WPD_OBJECT_DATE_MODIFIED = comtypes.pointer(
    port._tagpropertykey()  # pylint: disable=no-member, protected-access # type: ignore
)
WPD_OBJECT_DATE_MODIFIED.contents.fmtid = comtypes.GUID("{EF6B490D-5CD8-437A-AFFC-DA8B60EE4A3C}")
WPD_OBJECT_DATE_MODIFIED.contents.pid = 19

# ----------
WPD_CONTENT_TYPE_FOLDER_GUID = comtypes.GUID("{27E2E392-A111-48E0-AB0C-E17705A05F85}")


# Constants for the type entries returned bei PortableDeviceContent.get_properties
WPD_CONTENT_TYPE_UNDEFINED = -1
WPD_CONTENT_TYPE_STORAGE = 0
WPD_CONTENT_TYPE_DIRECTORY = 1
WPD_CONTENT_TYPE_FILE = 2
WPD_CONTENT_TYPE_DEVICE = 3

# Constants for delete
WPD_DELETE_NO_RECURSION = 0
WPD_DELETE_WITH_RECURSION = 1

# Module variables
DEVICE_MANAGER: Optional[Any] = None


# -------------------------------------------------------------------------------------------------
class PortableDeviceContent:  # pylint: disable=too-many-instance-attributes
    """Class for one file, directory or storage with it's properties.
    This class is only internaly created, use it only to read the properties

    Args:
        object_id: MTP object id.
        content: interface to IPortableDeviceContent.
        properties: The interface that is required to get or set properties on an object on
                    the device.

    Public methods:
        get_properties
        get_children
        get_child
        get_path
        create_content
        upload_file
        download_file
        remove

    Public attributes:
        name: Name of the MTP device
        fullname: The full path name
        date_created: The file date
        size: The size of the file in bytes
        content_type: Type of the entry. One of the WPD_CONTENT_TYPE_ constants

    Exceptions:
        IOError: If something went wrong
    """

    # class variable
    _properties_to_read: Optional[types.PortableDeviceKeyCollection] = None  # pylint: disable=no-member # type: ignore

    _CoTaskMemFree = ctypes.windll.ole32.CoTaskMemFree # type: ignore
    _CoTaskMemFree.restype = None
    _CoTaskMemFree.argtypes = [ctypes.c_void_p]

    def __init__(
        self,
        object_id: Any,
        content: "PortableDeviceContent",
        properties: Optional[Any] = None,
        parent_path: str = "",
    ) -> None:
        """ """

        self._object_id = object_id
        self._content: "PortableDeviceContent" = content
        self._parent_path = parent_path
        self.name: str = ""
        self._plain_name: str = ""
        self.content_type: int = WPD_CONTENT_TYPE_UNDEFINED
        self.full_filename: str = ""
        self.size: int = -1
        self.date_created: datetime.datetime = datetime.datetime(1970, 1, 1)
        self._capacity: int = -1
        self._free_capacity: int = -1
        self._serialnumber: str = ""
        self._properties = properties or content.properties()  # type: ignore
        if PortableDeviceContent._properties_to_read is None:
            # We havn't set the roperties wie will read, so do it now
            PortableDeviceContent._properties_to_read = comtypes.client.CreateObject(
                types.PortableDeviceKeyCollection,  # pylint: disable=no-member, protected-access # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,  # pylint: disable=no-member, protected-access
                interface=port.IPortableDeviceKeyCollection,  # pylint: disable=no-member, protected-access # type: ignore
            )
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_NAME)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_ORIGINAL_FILE_NAME)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_CONTENT_TYPE)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_SIZE)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_DATE_MODIFIED)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_OBJECT_DATE_CREATED)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_STORAGE_CAPACITY)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_STORAGE_FREE_SPACE_IN_BYTES)  # type: ignore
            PortableDeviceContent._properties_to_read.Add(WPD_DEVICE_SERIAL_NUMBER)  # type: ignore
        self.get_properties()

    def get_properties(
        self,
    ) -> Tuple[str, int, int, datetime.datetime, int, int, str]:
        """Get the properties of this content.

        Returns:
            name: The name for this content, normaly the file or directory name
            content_type: One of the content type values that descripe the type of the content
                        WPD_CONTENT_TYPE_UNDEFINED, WPD_CONTENT_TYPE_STORAGE,
                        WPD_CONTENT_TYPE_DIRECTORY, WPD_CONTENT_TYPE_FILE, WPD_CONTENT_TYPE_DEVICE
            size: The size of the file or 0 if content ist not a file
            date_created: The reation date of the file or directory
            capacity: The capacity of the storage, only valid if content_type is
                        WPD_CONTENT_TYPE_STORAGE
            free_capacity: The free capacity of the storage, only valid if content_type is
                        WPD_CONTENT_TYPE_STORAGE
            serialnumber: The serial number of the device, only valid if content_type is
                        WPD_CONTENT_TYPE_DEVICE

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> cont.get_properties()
            ('HSG1316', 0, -1, datetime.datetime(1970, 1, 1, 0, 0), -1, -1, 'DQVSSCM799999999')
        """
        if self._plain_name:
            return (
                self.name,
                self.content_type,
                self.size,
                self.date_created,
                self._capacity,
                self._free_capacity,
                self._serialnumber,
            )
        if self._object_id is None:
            return (
                "",
                WPD_CONTENT_TYPE_UNDEFINED,
                -1,
                self.date_created,
                self._capacity,
                self._free_capacity,
                self._serialnumber,
            )
        propvalues = self._properties.GetValues(  # type: ignore
            self._object_id, PortableDeviceContent._properties_to_read
        )
        self.content_type = WPD_CONTENT_TYPE_UNDEFINED
        try:
            self._plain_name = str(propvalues.GetStringValue(WPD_OBJECT_NAME))  # type: ignore
        except comtypes.COMError:
            self.content_type = WPD_CONTENT_TYPE_DIRECTORY
            self.name = self._plain_name = ""
        try:
            self.name = self._plain_name = str(propvalues.GetStringValue(WPD_OBJECT_ORIGINAL_FILE_NAME))  # type: ignore
        except comtypes.COMError:
            self.name = self._plain_name
        content_id = str(propvalues.GetGuidValue(WPD_OBJECT_CONTENT_TYPE))  # type: ignore
        if content_id in {
            "{23F05BBC-15DE-4C2A-A55B-A9AF5CE412EF}",
            "{99ED0160-17FF-4C44-9D98-1D7A6F941921}",
        }:
            # It's a storage
            try:
                self._capacity = int(propvalues.GetUnsignedLargeIntegerValue(WPD_STORAGE_CAPACITY))  # type: ignore
            except comtypes.COMError:
                self._capacity = -1
            try:
                self._free_capacity = int(
                    propvalues.GetUnsignedLargeIntegerValue(WPD_STORAGE_FREE_SPACE_IN_BYTES)  # type: ignore
                )
            except comtypes.COMError:
                self._free_capacity = -1
            with contextlib.suppress(comtypes.COMError):
                self._serialnumber = str(propvalues.GetStringValue(WPD_DEVICE_SERIAL_NUMBER))  # type: ignore
            self.content_type = WPD_CONTENT_TYPE_STORAGE
        elif content_id == "{27E2E392-A111-48E0-AB0C-E17705A05F85}":
            # It's a directory
            self.content_type = WPD_CONTENT_TYPE_DIRECTORY
        else:
            # it's not a folder or storage
            self.content_type = WPD_CONTENT_TYPE_FILE
            self.size = int(propvalues.GetUnsignedLargeIntegerValue(WPD_OBJECT_SIZE))  # type: ignore
            filetime = int(propvalues.GetValue(WPD_OBJECT_DATE_MODIFIED).data.date)  # type: ignore
            days_since_1970 = filetime - (datetime.datetime(1970, 1, 1) - datetime.datetime(1899, 12, 30)).days
            hours = (filetime - int(filetime)) * 24
            minutes = (hours - int(hours)) * 60
            seconds = (minutes - int(minutes)) * 60
            milliseconds = round((seconds - int(seconds)) * 1000)
            self.date_created = datetime.datetime(1970, 1, 1) + datetime.timedelta(
                days=days_since_1970,
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
                milliseconds=milliseconds,
            )
        propvalues.Clear()  # type: ignore
        self.full_filename = os.path.join(self._parent_path, self._plain_name)
        return (
            self.name,
            self.content_type,
            self.size,
            self.date_created,
            self._capacity,
            self._free_capacity,
            self._serialnumber,
        )

    def get_children(self) -> Generator["PortableDeviceContent", None, None]:
        """Get the child items of a folder.

        Returns:
            A Generator of PortableDeviceContent instances each representing a child entry.

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> str(cont.get_children()[0])[:58]
            "<PortableDeviceContent s10001: ('Interner Speicher', 0, -1"
        """
        try:
            enumobject_ids = self._content.EnumObjects(  # type: ignore
                ctypes.c_ulong(0),
                self._object_id,
                ctypes.POINTER(port.IPortableDeviceValues)(),  # pylint: disable=no-member # type: ignore
            )
            while True:
                num_objects = ctypes.c_ulong(16)  # block size, so to speak
                object_id_array = (ctypes.c_wchar_p * num_objects.value)()
                num_fetched = ctypes.pointer(ctypes.c_ulong(0))
                # be sure to change the IEnumPortableDeviceobject_ids 'Next'
                # function in the generated code to have object_ids as inout
                enumobject_ids.Next(  # type: ignore
                    num_objects,
                    ctypes.cast(object_id_array, ctypes.POINTER(ctypes.c_wchar_p)),
                    num_fetched,
                )
                if num_fetched.contents.value == 0:
                    break
                for index in range(num_fetched.contents.value):
                    curobject_id = object_id_array[index]
                    value = PortableDeviceContent(curobject_id, self._content, self._properties, self.full_filename)  # type: ignore
                    # Free memory
                    address = ctypes.addressof(object_id_array) + ctypes.sizeof(ctypes.c_wchar_p) * index
                    ptr = ctypes.pointer(ctypes.c_wchar_p.from_address(address))
                    ctypes.windll.ole32.CoTaskMemFree(ptr.contents) # type: ignore
                    yield value
        except comtypes.COMError as err:
            raise IOError(f"Error getting child item from '{self.full_filename}': {err.args[1]}")

    def get_child(self, name: str) -> Optional["PortableDeviceContent"]:
        """Returns a PortableDeviceContent for one child whos name is known.
        The search is case sensitive.

        Args:
            name: The name of the file or directory to search

        Returns:
            The PortableDeviceContent instance of the child or None if the child could not be
            found.

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> str(cont.get_child("Interner Speicher"))[:58]
            "<PortableDeviceContent s10001: ('Interner Speicher', 0, -1"
        """
        matches = [c for c in self.get_children() if c.name == name]
        return matches[0] if matches else None

    def get_path(self, path: str) -> Optional["PortableDeviceContent"]:
        """Returns a PortableDeviceContent for a child whos path in the tree is known

        Args:
            path: The pathname to the child. Each path entry must be separated by the
                    os.path.sep character.

        Returns:
            The PortableDeviceContent instance of the child or None if the child could not be
            found.

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> str(cont.get_path("Interner Speicher\\Android\\data"))[:41]
            "<PortableDeviceContent oE: ('data', 1, -1"
        """
        cur: Optional["PortableDeviceContent"] = self
        for part in path.split(os.path.sep):
            if not cur:
                return None
            cur = cur.get_child(part)
        return cur

    def __repr__(self) -> str:
        """ """
        return f"<PortableDeviceContent {self._object_id}: {self.get_properties()}>"

    def create_content(self, dirname: str) -> None:
        """Creates an empty directory content in this content.

        Args:
            dirname: Name of the directory that shall be created

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> mycont = cont.get_path("Interner Speicher\\Music\\MyMusic")
            >>> if mycont: _ = mycont.remove()
            >>> cont = cont.get_path("Interner Speicher\\Music")
            >>> cont.create_content("MyMusic")
        """
        try:
            object_properties = comtypes.client.CreateObject(
                types.PortableDeviceValues,  # pylint: disable=no-member # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,
                interface=port.IPortableDeviceValues,  # pylint: disable=no-member # type: ignore
            )
            object_properties.SetStringValue(WPD_OBJECT_PARENT_ID, self._object_id)  # type: ignore
            object_properties.SetStringValue(WPD_OBJECT_NAME, dirname)  # type: ignore
            object_properties.SetStringValue(WPD_OBJECT_ORIGINAL_FILE_NAME, dirname)  # type: ignore
            object_properties.SetGuidValue(WPD_OBJECT_CONTENT_TYPE, WPD_CONTENT_TYPE_FOLDER_GUID)  # type: ignore
            self._content.CreateObjectWithPropertiesOnly(  # type: ignore
                object_properties, ctypes.POINTER(ctypes.c_wchar_p)()
            )
        except comtypes.COMError as err:
            raise IOError(f"Error creating directory '{dirname}': {err.args[1]}")

    def upload_stream(self, filename: str, inputstream: io.FileIO, stream_len: int) -> None:
        """Upload a steam to a file on the MTP device.
        For an easier usage use upload_file

        Args:
            filename: Name of the new file on the MTP device
            inputstream: open python file
            stream_len: length of the file to upload

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> mycont = cont.get_path("Interner Speicher\\Music\\Test.mp3")
            >>> if mycont: _ = mycont.remove()
            >>> cont = cont.get_path("Interner Speicher\\Music")
            >>> name = '..\\..\\Tests\\OnFire.mp3'
            >>> size = os.path.getsize(name)
            >>> inp = open(name, "rb")
            >>> cont.upload_stream("Test.mp3", inp, size)
            >>> inp.close()
        """
        try:
            object_properties = comtypes.client.CreateObject(
                types.PortableDeviceValues,  # pylint: disable=no-member # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,
                interface=port.IPortableDeviceValues,  # pylint: disable=no-member # type: ignore
            )
            object_properties.SetStringValue(WPD_OBJECT_PARENT_ID, self._object_id)  # type: ignore
            object_properties.SetUnsignedLargeIntegerValue(WPD_OBJECT_SIZE, stream_len)  # type: ignore
            object_properties.SetStringValue(WPD_OBJECT_ORIGINAL_FILE_NAME, filename)  # type: ignore
            object_properties.SetStringValue(WPD_OBJECT_NAME, filename)  # type: ignore
            optimal_transfer_size_bytes = ctypes.pointer(ctypes.c_ulong(0))
            p_filestream = ctypes.POINTER(port.IStream)()  # pylint: disable=no-member # type: ignore
            # be sure to change the IPortableDeviceContent
            # 'CreateObjectWithPropertiesAndData' function in the generated code to
            # have IStream ppData as 'in','out'
            filestream, _, _ = self._content.CreateObjectWithPropertiesAndData(  # type: ignore
                object_properties,
                p_filestream,
                optimal_transfer_size_bytes,
                ctypes.POINTER(ctypes.c_wchar_p)(),
            )
            # filestream = filestream.value
            blocksize = optimal_transfer_size_bytes.contents.value
            # cur_written = 0
            # while True:
            #     to_read = stream_len - cur_written
            #     block = inputstream.read(to_read if to_read < blocksize else blocksize)
            #     if len(block) <= 0:
            #         break
            #     string_buf = ctypes.create_string_buffer(block)
            #     written = filestream.RemoteWrite(
            #         ctypes.cast(string_buf, ctypes.POINTER(ctypes.c_ubyte)),
            #         len(block),
            #     )
            #     cur_written += written
            #     if cur_written >= stream_len:
            #         break
            while True:
                block = inputstream.read(blocksize)
                if len(block) <= 0:
                    break
                string_buf = ctypes.create_string_buffer(block)
                filestream.RemoteWrite(  # type: ignore
                    ctypes.cast(string_buf, ctypes.POINTER(ctypes.c_ubyte)),
                    len(block),
                )
            stgc_default = 0
            filestream.Commit(stgc_default)  # type: ignore
        except comtypes.COMError as err:
            raise IOError(f"Error storing stream '{filename}': {err.args[1]}")

    def upload_file(self, filename: str, inputfilename: str) -> None:
        """Upload of a file to MTP device.

        Args:
            filename: Name of the new file on the MTP device
            inputfilename: Name of the file that shall be uploaded

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> mycont = cont.get_path("Interner Speicher\\Music\\Test.mp3")
            >>> if mycont: _ = mycont.remove()
            >>> cont = cont.get_path("Interner Speicher\\Music")
            >>> name = '..\\..\\Tests\\OnFire.mp3'
            >>> cont.upload_file("Test.mp3", name)
        """
        try:
            length = os.path.getsize(inputfilename)
            # with open(inputfilename, "rb") as input_stream:
            with io.FileIO(inputfilename, "r") as input_stream:
                self.upload_stream(filename, input_stream, length)
        except comtypes.COMError as err:
            raise IOError(f"Error storing file '{filename}': {err.args[1]}")

    def download_stream(self, outputstream: IO[bytes]) -> None:
        """Download a file from MTP device.
        The used ProtableDeviceContent instance must be a file!
        For easier usage use download_file

        Args:
            outputstream: Open python file for writing

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> cont = cont.get_path("Interner Speicher\\Ringtones\\hangouts_incoming_call.ogg")
            >>> name = '..\\..\\Tests\\hangouts_incoming_call.ogg'
            >>> outp = open(name, "wb")
            >>> cont.download_stream(outp)
            >>> outp.close()
        """
        try:
            resources = self._content.Transfer()  # type: ignore
            stgm_read = ctypes.c_uint(0)
            optimal_transfer_size_bytes = ctypes.pointer(ctypes.c_ulong(0))
            p_filestream = ctypes.POINTER(port.IStream)()  # pylint: disable=no-member # type: ignore
            optimal_transfer_size_bytes, q_filestream = resources.GetStream(  # type: ignore
                self._object_id,
                WPD_RESOURCE_DEFAULT,
                stgm_read,
                optimal_transfer_size_bytes,
                p_filestream,
            )
            blocksize = int(optimal_transfer_size_bytes.contents.value)  # type: ignore
            filestream = q_filestream.value  # type: ignore
            #            buf = (ctypes.c_ubyte * blocksize)()
            # make sure all RemoteRead parameters are in
            while True:
                buf, length = filestream.RemoteRead(blocksize)  # type: ignore
                if length == 0:
                    break
                outputstream.write(bytearray(buf[:length]))  # type: ignore
        except comtypes.COMError as err:
            raise IOError(f"Error getting file': {err.args[1]}")

    def download_file(self, outputfilename: str) -> None:
        """Download of a file from MTP device
        The used ProtableDeviceContent instance must be a file!

        Args:
            outputfilename: Name of the file the MTP file shall be written to. Any existing
                            content will be replaced.

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> cont = cont.get_path("Interner Speicher\\Ringtones\\hangouts_incoming_call.ogg")
            >>> name = '..\\..\\Tests\\hangouts_incoming_call.ogg'
            >>> cont.download_file(name)
        """
        try:
            # with open(outputfilename, "wb") as output_stream:
            with io.FileIO(outputfilename, "w") as output_stream:
                self.download_stream(output_stream)
        except comtypes.COMError as err:
            raise IOError(f"Error getting file '{outputfilename}': {err.args[1]}")

    def remove(self) -> None:
        """Deletes the current directory or file.

        Return:
            0 on OK, else a windows errorcode

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> cont = dev[0].get_content()
            >>> mycont = cont.get_path("Interner Speicher\\Music\\Test.mp3")
            >>> if mycont: _ = mycont.remove()
            >>> cont = cont.get_path("Interner Speicher\\Music")
            >>> name = '..\\..\\Tests\\OnFire.mp3'
            >>> cont.upload_file("Test.mp3", name)
            >>> cont = dev[0].get_content()
            >>> mycont = cont.get_path("Interner Speicher\\Music\\Test.mp3")
            >>> mycont.remove()
            0
        """
        try:
            objects_to_delete = comtypes.client.CreateObject(
                types.PortableDevicePropVariantCollection,  # pylint: disable=no-member, protected-access # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,  # pylint: disable=no-member, protected-access
                interface=port.IPortableDevicePropVariantCollection,  # pylint: disable=no-member, protected-access # type: ignore
            )
            pvar = port.tag_inner_PROPVARIANT()  # pylint: disable=no-member # type: ignore
            pvar.vt = comtypes.automation.VT_LPWSTR
            pvar.data.pwszVal = ctypes.c_wchar_p(self._object_id)
            objects_to_delete.Add(pvar)  # type: ignore
            errors = comtypes.client.CreateObject(
                types.PortableDevicePropVariantCollection,  # pylint: disable=no-member, protected-access # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,  # pylint: disable=no-member, protected-access
                interface=port.IPortableDevicePropVariantCollection,  # pylint: disable=no-member, protected-access # type: ignore
            )
            self._content.Delete(WPD_DELETE_WITH_RECURSION, objects_to_delete, errors)  # type: ignore
            count = ctypes.c_ulong()
            errors.GetCount(ctypes.pointer(count))  # type: ignore
            for i in range(count.value):
                index = ctypes.c_ulong(i)
                pvar = port.tag_inner_PROPVARIANT()  # pylint: disable=no-member # type: ignore
                errors.GetAt(index, ctypes.pointer(pvar))  # type: ignore
                # if pvar.data.uintVal != 0:
                #     return pvar.data.uintVal
        except comtypes.COMError as err:
            raise IOError(f"Error deleting file '{self.full_filename}': {err.args[1]}")


# -------------------------------------------------------------------------------------------------


class PortableDevice:
    """Class with the infos for a connected portable device.
    The instanzes of this class will be created internaly. User should not instanciate them manually
    until you know what you do.

    Public methods:
        get_description
        get_content

    Public attributes:

    Exceptions:
        IOError: If something went wrong
    """

    def __init__(self, p_id: str) -> None:
        """Init the class.

        Args:
            p_id: ID of the found device
        """
        self._p_id = p_id
        self._desc = ""
        self._name = ""
        self._device = None

    def get_description(self) -> Tuple[str, str]:
        """Get the name and the description of the device. If no description is available
        name and description will be identical.

        Returns:
            A tuple with of name, description

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> dev[0].get_description()
            ('HSG1316', 'HSG1316')
        """
        if self._name:
            return self._name, self._desc
        if DEVICE_MANAGER is None:
            return "", ""
        name_len = ctypes.pointer(ctypes.c_ulong(0))
        DEVICE_MANAGER.GetDeviceDescription(self._p_id, ctypes.POINTER(ctypes.c_ushort)(), name_len)
        name = ctypes.create_unicode_buffer(name_len.contents.value)
        DEVICE_MANAGER.GetDeviceDescription(
            self._p_id,
            ctypes.cast(name, ctypes.POINTER(ctypes.c_ushort)),
            name_len,
        )
        self._desc = name.value
        try:
            DEVICE_MANAGER.GetDeviceFriendlyName(self._p_id, ctypes.POINTER(ctypes.c_ushort)(), name_len)
            name = ctypes.create_unicode_buffer(name_len.contents.value)
            DEVICE_MANAGER.GetDeviceFriendlyName(
                self._p_id,
                ctypes.cast(name, ctypes.POINTER(ctypes.c_ushort)),
                name_len,
            )
            self._name = name.value
        except comtypes.COMError:
            self._name = self._desc
            try:
                propvalues = self._get_device().Content().properties().GetValues("DEVICE", None)
                self._name = propvalues.GetStringValue(WPD_OBJECT_NAME)
            except comtypes.COMError:
                self._name = self._desc
        # WPD_DEVICE_SERIAL_NUMBER
        return self._name, self._desc

    def _get_device(self) -> Any:
        """Open a device"""
        if self._device:
            return self._device
        client_information = comtypes.client.CreateObject(
            types.PortableDeviceValues,  # pylint: disable=no-member  # type: ignore
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDeviceValues,  # pylint: disable=no-member  # type: ignore
        )
        self._device = comtypes.client.CreateObject(
            port.PortableDevice,  # pylint: disable=no-member  # type: ignore
            clsctx=comtypes.CLSCTX_INPROC_SERVER,
            interface=port.IPortableDevice,  # pylint: disable=no-member  # type: ignore
        )
        if self._device is not None:  # type: ignore
            self._device.Open(self._p_id, client_information)  # type: ignore
        return self._device

    def get_device_path(self) -> str:
        """Returns the full path to the directory"""
        return self._name

    def get_content(self) -> List[PortableDeviceContent]:
        """Get the content of a device.

        Returns:
            An instance of PortableDeviceContent

        Examples:
            >>> import mtp.win_access
            >>> dev = mtp.win_access.get_portable_devices()
            >>> str(dev[0].get_content())[:33]
            '<PortableDeviceContent c_wchar_p('
        """
        return [
            PortableDeviceContent(ctypes.c_wchar_p("DEVICE"), self._get_device().Content(), None),
        ]

    def __repr__(self) -> str:
        return f"<PortableDevice: {self.get_description()}>"


# -------------------------------------------------------------------------------------------------
# Globale functions


def get_portable_devices() -> list[PortableDevice]:
    """Get all attached portable devices.

    Returns:
        A list of PortableDevice one for each found MTP device. The list is empty if no device
            was found.

    Exceptions:
        IOError: If something went wrong

    Examples:
        >>> import mtp.win_access
        >>> mtp.win_access.get_portable_devices()
        [<PortableDevice: ('HSG1316', 'HSG1316')>]
    """
    global DEVICE_MANAGER  # pylint: disable=global-statement

    try:
        if DEVICE_MANAGER is None:
            comtypes.CoInitialize()
            DEVICE_MANAGER = comtypes.client.CreateObject(  # type: ignore
                port.PortableDeviceManager,  # pylint: disable=no-member  # type: ignore
                clsctx=comtypes.CLSCTX_INPROC_SERVER,
                interface=port.IPortableDeviceManager,  # pylint: disable=no-member  # type: ignore
            )
        pnp_device_id_count = ctypes.pointer(ctypes.c_ulong(0))
        DEVICE_MANAGER.GetDevices(ctypes.POINTER(ctypes.c_wchar_p)(), pnp_device_id_count)
        if pnp_device_id_count.contents.value == 0:
            return []
        pnp_device_ids = (ctypes.c_wchar_p * pnp_device_id_count.contents.value)()
        DEVICE_MANAGER.GetDevices(  # pylint: disable=no-member  # type: ignore
            ctypes.cast(pnp_device_ids, ctypes.POINTER(ctypes.c_wchar_p)),
            pnp_device_id_count,
        )
        return [PortableDevice(cur_id) for cur_id in pnp_device_ids if cur_id is not None]
    except comtypes.COMError as err:
        raise IOError(f"Error getting list of devices: {err.args[1]}")


def get_content_from_device_path(dev: PortableDevice, path: str) -> Optional[PortableDeviceContent]:
    """Get the content of a path.

    Args:
        dev: The instance of PortableDevice where the path is searched
        path: The pathname of the file or directory

    Returns:
        An instance of PortableDeviceContent if the path is an existing file or directory
            else None is returned.

    Exceptions:
        IOError: If something went wrong

    Examples:
        >>> import mtp.win_access
        >>> dev = mtp.win_access.get_portable_devices()
        >>> n = "HSG1316\\Interner Speicher\\Ringtones"
        >>> w =mtp.win_access.get_content_from_device_path(dev[0], n)
        >>> str(w)[:46]
        "<PortableDeviceContent o3: ('Ringtones', 1, -1"
    """
    try:
        path = path.replace("\\", os.path.sep).replace("/", os.path.sep)
        path_parts = path.split(os.path.sep)
        if path_parts[0] == dev.get_description()[0]:
            return (
                dev.get_content()[0].get_path(os.path.sep.join(path_parts[1:]))
                if len(path_parts) > 1
                else dev.get_content()[0]
            )
        return None
    except comtypes.COMError as err:
        raise IOError(f"Error reading directory '{path}': {err.args[1]}")


def walk(
    dev: PortableDevice,
    path: str,
    callback: Optional[Callable[[str], bool]] = None,
    error_callback: Optional[Callable[[str], bool]] = None,
) -> Generator[
    tuple[str, list[PortableDeviceContent], list[PortableDeviceContent]],
    None,
    None,
]:
    """Iterates ower all files in a tree just like os.walk

    Args:
        dev: Portable device to iterate in
        path: path from witch to iterate
        callback: when given, a function that takes one argument (the selected file) and returns
                a boolean. If the returned value is false, walk will cancel an return empty
                list.
                the callback is usefull to show for example a progress because reading thousands
                of file from one MTP directory lasts very long.
        error_callback: when given, a function that takes one argument (the errormessage) and returns
                a boolean. If the returned value is false, walk will cancel and return empty
                list.

    Returns:
        A tuple with this content:
            A string with the root directory
            A list of PortableDeviceContent for the directories  in the directory
            A list of PortableDeviceContent for the files in the directory

    Exceptions:
        IOError: If something went wrong

    Examples:
        >>> import mtp.win_access
        >>> dev = mtp.win_access.get_portable_devices()
        >>> n = "HSG1316\\Interner Speicher\\Ringtones"
        >>> for r, d, f in mtp.win_access.walk(dev[0], n):
        ...     for f1 in f:
        ...             print(f1.name)
        ...
        hangouts_message.ogg
        hangouts_incoming_call.ogg
    """
    if not (cont := get_content_from_device_path(dev, path)):
        return
    cont.full_filename = path
    walk_cont: list[PortableDeviceContent] = [cont]
    while walk_cont:
        cont = walk_cont[0]
        del walk_cont[0]
        directories: list[PortableDeviceContent] = []
        files: list[PortableDeviceContent] = []
        try:
            for child in cont.get_children():
                (_, contenttype, _, _, _, _, _) = child.get_properties()
                if contenttype in [
                    WPD_CONTENT_TYPE_STORAGE,
                    WPD_CONTENT_TYPE_DIRECTORY,
                ]:
                    # child.full_filename = os.path.join(cont.full_filename, name)
                    directories.append(child)
                elif contenttype == WPD_CONTENT_TYPE_FILE:
                    # child.full_filename = os.path.join(cont.full_filename, name)
                    files.append(child)
                if callback and not callback(child.full_filename):
                    directories = []
                    files = []
                    return
            yield cont.full_filename, sorted(directories, key=lambda ent: ent.full_filename), sorted(
                files, key=lambda ent: ent.full_filename
            )
        except Exception as err:
            if error_callback is not None:
                if not error_callback(str(err)):
                    directories = []
                    files = []
                    return
        walk_cont.extend(directories)


def makedirs(dev: PortableDevice, path: str) -> Optional[PortableDeviceContent]:
    """Creates the directories in path on the MTP device if they don't exist.

    Args:
        dev: Portable device to create the dirs on
        path: pathname of the dir to create. Any directoriues in path that don't exist
            will e created automatically.
    Exceptions:
        IOError: If something went wrong

    Examples:
        >>> import mtp.win_access
        >>> dev = mtp.win_access.get_portable_devices()
        >>> n = "HSG1316\\Interner Speicher\\Music\\MyMusic\\Test1"
        >>> str(mtp.win_access.makedirs(dev[0], n))[:22]
        '<PortableDeviceContent'
    """
    try:
        path_int = ""
        content: Optional[PortableDeviceContent] = dev.get_content()[0]
        path = path.replace("\\", os.path.sep).replace("/", os.path.sep)
        for dirname in path.split(os.path.sep):
            if dirname == "":
                continue
            path_int = os.path.join(path_int, dirname)
            ziel_content = get_content_from_device_path(dev, path_int)
            if not ziel_content:
                if not content:
                    return None
                content.create_content(dirname)
                ziel_content = get_content_from_device_path(dev, path_int)
            content = ziel_content
        return content
    except comtypes.COMError as err:
        raise IOError(f"Error creating directory '{path}': {err.args[1]}")
