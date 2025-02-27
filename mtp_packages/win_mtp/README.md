# win_mtp

Accessing the filesystem of MTP devices (Smartphones, MP3-Player, etc.) on Windows with python.

In the win_mtp directory there are two modules.
- access.py
- dialog.py

For detailed description see (https://heribert17.github.io/win_mtp/)

Tested with:
* Python 3.10 and above
* comptypes 1.2.0
* Windows 10


## access.py
This modules implements the access to the Windows WPD functions to read and write MTP devices like smartphones, tablets. etc.

## dialog.py
Dialog.py implements a directory searcher in tkinter that shows the attached MTP devices and there directories.


# Changelog
* 1.0.1
    * Fixed crash when during walk a directory is deleted.
    * Fixed full_filename for files was not set.
* 1.0.2
    * Fixed a bug when an MTP device doesn't have a userfriendly name
