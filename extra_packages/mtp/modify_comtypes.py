"""
A module to modify the from comtypes generated modules.
They contain some wrong function calls. These calls are corrected by this function

As comtypes isn't able to reload the with GetModule created files, we have to
quit the programm if we changed the files. When the programm starts the next time
comtypes findes the modified files and loads them.

Author:  Heribert Füchtenhans

Version: 2024.12.10

"""

import os


def modify_generated_files(gen_dir: str) -> None:
    """Modifies the from comtypes generated files because some call are incorrect"""
    filename = os.path.join(gen_dir, "_1F001332_1A57_4934_BE31_AFFC99F4EE0A_0_1_0.py")
    with open(filename, encoding="utf-8") as inp:
        content = inp.read()
    content_changed = False
    for entry in (
        (
            "IEnumPortableDeviceObjectIDs._methods_",
            "'Next',",
            "(['out'], POINTER(WSTRING), 'pObjIDs')",
            "(['in', 'out'], POINTER(WSTRING), 'pObjIDs')",
        ),
        (
            "IPortableDeviceContent._methods_",
            "'CreateObjectWithPropertiesAndData'",
            "(['out'], POINTER(POINTER(IStream)), 'ppData')",
            "(['in', 'out'], POINTER(POINTER(IStream)), 'ppData')",
        ),
        (
            "IPortableDeviceResources._methods_",
            "'GetStream'",
            "(['out'], POINTER(POINTER(IStream)), 'ppStream')",
            "(['in', 'out'], POINTER(POINTER(IStream)), 'ppStream')",
        ),
        (
            "tag_inner_PROPVARIANT._fields_ =",
            "('__MIDL",
            "('__MIDL____MIDL_itf_PortableDeviceApi_0001_00000001', __MIDL___MIDL_itf_"
            "PortableDeviceApi_0001_0000_0001)",
            "('data', __MIDL___MIDL_itf_PortableDeviceApi_0001_0000_0001)",
        ),
    ):
        pos = content.find(entry[0])
        pos = content.find(entry[1], pos)
        pos1 = content.find(entry[2], pos, pos + 300)
        if pos1 > 0:
            content = content[:pos1] + content[pos1:].replace(entry[2], entry[3], 1)
            content_changed = True
        # else:
        #     print(
        #         f"WARNING: Could not find '{entry[0]}' / '{entry[1]}' / '{entry[2]}', "
        #         "maybe it's already replaced."
        #     )
    # Save all back when changed
    if content_changed:
        print("changed")
        with open(filename, "w", encoding="utf-8") as outp:
            outp.write(content)
        print("Sorry, but comtypes isn't able to reload the just modified files.\n" "So please restart the program.")
        quit()  # pylint: disable=consider-using-sys-exit
