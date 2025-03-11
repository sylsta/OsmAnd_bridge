from enum import IntFlag

from . import _00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from . _00020430_0000_0000_C000_000000000046_0_2_0 import (
    OLE_XPOS_PIXELS, Font, OLE_OPTEXCLUSIVE, Color, DISPPROPERTY,
    IFontEventsDisp, FONTSIZE, OLE_ENABLEDEFAULTBOOL,
    OLE_YSIZE_HIMETRIC, CoClass, IPicture, IFont, FONTITALIC,
    IUnknown, VARIANT_BOOL, _lcid, OLE_XPOS_CONTAINER, dispid,
    IEnumVARIANT, OLE_CANCELBOOL, OLE_YPOS_PIXELS, Monochrome,
    StdFont, FONTNAME, Default, OLE_YSIZE_PIXELS, IDispatch,
    Unchecked, Gray, _check_version, DISPPARAMS, FONTSTRIKETHROUGH,
    Checked, OLE_YPOS_HIMETRIC, HRESULT, typelib_path, OLE_COLOR,
    OLE_XSIZE_CONTAINER, IFontDisp, Picture, COMMETHOD, StdPicture,
    Library, OLE_YPOS_CONTAINER, OLE_XSIZE_HIMETRIC,
    OLE_YSIZE_CONTAINER, OLE_XSIZE_PIXELS, DISPMETHOD, VgaColor,
    OLE_HANDLE, IPictureDisp, BSTR, FontEvents, OLE_XPOS_HIMETRIC,
    EXCEPINFO, FONTBOLD, GUID, FONTUNDERSCORE
)


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


__all__ = [
    'Checked', 'OLE_XPOS_PIXELS', 'Font', 'OLE_OPTEXCLUSIVE',
    'LoadPictureConstants', 'IFontEventsDisp', 'OLE_YPOS_HIMETRIC',
    'typelib_path', 'OLE_COLOR', 'OLE_XSIZE_CONTAINER', 'FONTSIZE',
    'OLE_ENABLEDEFAULTBOOL', 'IFontDisp', 'OLE_YSIZE_HIMETRIC',
    'IPicture', 'IFont', 'FONTITALIC', 'Picture', 'StdPicture',
    'Library', 'Unchecked', 'OLE_XPOS_CONTAINER',
    'OLE_YPOS_CONTAINER', 'OLE_XSIZE_HIMETRIC', 'OLE_YSIZE_CONTAINER',
    'OLE_XSIZE_PIXELS', 'OLE_CANCELBOOL', 'OLE_TRISTATE',
    'OLE_YPOS_PIXELS', 'Monochrome', 'VgaColor', 'OLE_HANDLE',
    'IPictureDisp', 'StdFont', 'FONTNAME', 'Default',
    'OLE_YSIZE_PIXELS', 'FontEvents', 'OLE_XPOS_HIMETRIC', 'FONTBOLD',
    'Color', 'Gray', 'FONTUNDERSCORE', 'FONTSTRIKETHROUGH'
]

