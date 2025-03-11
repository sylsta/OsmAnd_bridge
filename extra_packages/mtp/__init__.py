# mtp/__init__.py

"""Access MPT devices like Smartphones under Windows and Linux.
Some file access methods like reading/writing files, listing directories
and creating/deleting directories are implemented.

Version: 1.2.0

Modules needed by this package:

For Windows
    - comtypes
For Linux:
    libmtp must be installed

Operating systems:

- Windows 10 and above
- Linux

Implemented modules:

- 'win_access': Provide several methods to access the file system on MTP devices under Windows.
- 'linux_access': Provide several methods to access the file system on MTP devices under Linux.
- 'dialog': Provides a class to get a directory selection dialog for MTP devices.
"""
