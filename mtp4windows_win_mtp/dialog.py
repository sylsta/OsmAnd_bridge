"""
A module with wpd relevant dialogs for tkinter

Author:  Heribert Füchtenhans

Version: 1.0.1

OS:      Windows

Requirements:
OS: Windows 10
Python: 
    tkinter
    mtp_access

The module contains the following classes:

- 'AskDirectory' - Class to select a directory on an MTP device

Examples:
    >>> from win_mtp import mtp_dialog
    >>> root = tkinter.Tk()
    >>> root.title("mtp_dialogs")
    >>> adir = mtp_dialog.AskDirectory(root, "Test ask_directory", ("Alls well", "Don't do it"))
"""


import contextlib
import tkinter
import tkinter.simpledialog
from tkinter import ttk
from typing import Any, Optional

from . import access

SMARTPHONE_ICON = """\
R0lGODdhDgAUAOeCAA0UJSgnJyoqKTExMRA4eABFoj08PT09PAZNsT5KZ05NTExPWyVYuwxg1AFj
4gBl6CtdwFhYWQBn7FBZehZj3ABq8ihhzgxn8ABr9QBs+F1dXQBt+QJt+QBu+wBv/Stl1gFv+xVq
7g9s9hxp62FhYDllyR1s6hFv9i5w7Uxswjdy6lVutz9y5hWE6gyG+xuE+3R0dXR2gXl6e3t7e3t/
lWCD4D2P8omJiTua+YKMrpGRkYuXxZiYmIab2Z6hrpihxaKiopez56+wtoa556yyzbOzs7Kzt7K0
u7S2wMDBw8DE1rzN8L7O7r7P7cvO2s/Pz8LS7tLS0sjU79PT09XV1dXW3tfX19vb29vb3tjc49rf
6Nbh9d/g4dji9eHh4eLi4trj9Nzk9Nzl9d3l9eXl5ebm5ufn5+Pp9uvr6+vv+O/v7/Ly8vDz+vPz
8/T09PT2+/b29vX2/PX3+/X3/PX3/ff39/j4+Pf5/Pn5+fr5+vn6/Pr6+vr7/Pz8/Pz8/f39/f39
/v7+/v//////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////ywAAAAADgAUAAAI0gADCRwY
yM8dPQQTCpwTpskZQAoHyhkDJUiahIIyCqLTZQkTKRAFrrlihcqULFvEgAnDR2CdGwEGaIggQ8sb
NnFCrolRAAEDCCu4/PkTMpAdGhI6gADBAovCPj4evMDhQkWViEgc2BjSAoWTPwqPUBjRo0YIJWAT
CvmQ4YKICkT6KDRiwYNdDD/2YExSwq6HDTvyYHySgsMJEw1y4FF4ZQKBBAsAwLCjsAwJBQcMCOCx
OCEcIDN0FImiRm7CP2vMkPHyBQ2ctAP71HHTBs4e2AIDAgA7
"""

# ------------------------------------------------------------------------------------------------


class AskDirectory(
    tkinter.simpledialog.Dialog
):  # pylint: disable=too-many-instance-attributes
    """Select a wpd device and directory.

    Public methods:

    Public attributes:
        answer: The MTP path to the selected directory
        wpd_device: The PortableDevice that was selected

    Exceptions:
        comtypes.COMError: exceptions if something went wrong
    """

    def __init__(
        self,
        parent: tkinter.Tk,
        title: str,
        buttons: tuple[str, str] = ("OK", "Cancel"),
    ) -> None:
        """Initializes the class and shows the directory dialog.

        Args:
            parent: The tkinter parent
            title: The windows title
            buttons: A tuple with the text for the OK and cancel button to chnage them
                     for other languages.
        """
        self._parent = parent
        self._dialog_title = title
        self._tree: ttk.Treeview
        self._smartphone_icon = tkinter.PhotoImage(data=SMARTPHONE_ICON)
        self._devicelist: dict[str, access.PortableDevice] = {}
        self._buttons = buttons
        # external variables
        self.answer = ""
        self.wpd_device: Optional[access.PortableDevice] = None
        tkinter.simpledialog.Dialog.__init__(self, parent, title=title)

    def buttonbox(self) -> None:
        """Create own buttons"""
        box = ttk.Frame(self)
        box.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        but = ttk.Button(box, text=self._buttons[1], command=self.cancel)
        but.pack(side=tkinter.RIGHT, padx=5, pady=5)
        but = ttk.Button(
            box, text=self._buttons[0], command=self._on_ok, default=tkinter.ACTIVE
        )
        but.pack(side=tkinter.RIGHT, padx=5, pady=5)
        but.focus_set()
        but.bind("<Return>", self.ok)

    def body(self, _: Any) -> None:
        """Create body"""
        box = ttk.Frame(self)
        box.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self._tree = ttk.Treeview(box, height=20, show="tree")
        self._tree.column("#0", width=500)
        self._tree.bind("<<TreeviewSelect>>", self._on_treeselect)
        # adding data, get devices
        for dev in access.get_portable_devices():
            if device_desc := dev.get_description():
                name = device_desc[0]
                self._devicelist[name] = dev
                self._tree.insert(
                    "",
                    tkinter.END,
                    text=name,
                    iid=name,
                    open=False,
                    image=self._smartphone_icon,
                    tags=[name],
                )
                self._start_process_directory(dev, name, name)
        # place the Treeview widget on the root window
        self._tree.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def _start_process_directory(
        self, dev: access.PortableDevice, name: str, devicename: str
    ) -> None:
        """Start reading directories"""
        self.config(cursor="wait")
        self._parent.after(500, self._process_directory, dev, name, devicename)

    def _process_directory(
        self, dev: access.PortableDevice, name: str, devicename: str, depth: int = 3
    ) -> None:
        """Insert directory listing until depth is 0"""
        if depth == 0:
            return
        selection = name
        cont = access.get_content_from_device_path(
            self._devicelist[devicename], selection
        )
        if not cont:  # no children
            return
        for child in cont.get_children():
            contenttype = child.content_type
            if contenttype not in (
                access.WPD_CONTENT_TYPE_STORAGE,
                access.WPD_CONTENT_TYPE_DIRECTORY,
            ):
                continue
            cont_name = child.name
            fullpath = f"{selection}/{cont_name}" if cont_name else selection
            with contextlib.suppress(tkinter.TclError):
                self._tree.insert(
                    selection,
                    tkinter.END,
                    text=cont_name,
                    iid=fullpath,
                    open=False,
                    tags=[devicename],
                )
            self._process_directory(dev, fullpath, devicename, depth - 1)
        if depth == 3:
            # When depth is 3, we are in the top level of calls
            self.config(cursor="")

    def _on_treeselect(self, _: Any) -> None:
        """Will be called on very selection"""
        selection = self._tree.focus()
        devicename = self._tree.item(selection, "tags")[0]
        self._start_process_directory(
            self._devicelist[devicename], selection, devicename
        )
        self._tree.item(selection, open=True)

    def _on_ok(self) -> None:
        """OK Button"""
        self.withdraw()
        self.update_idletasks()
        self.answer = self._tree.focus()
        if self.answer == "":
            self.cancel()
        else:
            devicename = self._tree.item(self.answer, "tags")[0]
            self.wpd_device = self._devicelist[devicename]
            try:
                self.apply()
            finally:
                self.cancel()
