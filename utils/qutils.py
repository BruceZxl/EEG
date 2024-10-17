import ctypes
import ctypes.util
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import url2pathname
from loguru import logger


# For Windows accent color.
_dll = None
# Cached MacOS accent color got from commandline.
_mac_color = None
# For alternate way to get MacOS accent color.
_appkit = None
_objc = None
_default_color = 0x22ffffff # almost transparent


def url_to_path(url: str):
    url = urlparse(url)
    assert url.scheme == "file"
    return Path(url2pathname(url.path))


def os_accent_color() -> int:
    if sys.platform in ["win32", "cygwin"]:
        return windows_accent_color()
    elif sys.platform == "darwin":
        return macos_accent_color()
    else:
        return _default_color


def windows_accent_color() -> int:
    global _dll
    if _dll is None:
        _dll = ctypes.WinDLL('dwmapi.dll')
    params = DwmColorizationParams()
    code = _dll[127](ctypes.byref(params))
    if code:
        logger.error(f"Invocation failed: DwmGetColorizationParameters() returned {code} ")
        return _default_color
    return params.ColorizationColor


# The easy way.
def macos_accent_color() -> int:
    global _mac_color
    import subprocess
    if _mac_color is not None:
        color, date = _mac_color
        if (date - datetime.now()).seconds <= 5:
            return color
    process = subprocess.run(
        ['defaults', 'read', '-g', 'AppleAccentColor'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    color = 0x0000dd
    if process.returncode == 0:
        color = {
            "-1": 0xFF2A2A2A,  # graphite
            "0": 0xFFFF0000,   # red
            "1": 0xFFFFA500,   # orange
            "2": 0xFFFFFF00,   # yellow
            "3": 0xFF008000,   # green
            "4": 0xFF0000FF,   # blue
            "5": 0xFF800080,   # purple
            "6": 0xFFFFC0CB    # pink
        }.get(process.stdout.strip(), color)
    _mac_color = (color, datetime.now())
    return color


# The funny way.
def macos_accent_color_2():
    global _appkit, _objc
    if _appkit is None or _objc is None:
        _appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('AppKit'))
        _objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
    pool = call_objc(
        call_objc(b'NSAutoreleasePool', b'alloc'), b'init')
    color = call_objc(
        call_objc(b'NSColor', b'controlAccentColor'),
        b'colorUsingColorSpace:',
        call_objc(b'NSColorSpace', b'genericRGBColorSpace'),
    )
    result = 0
    for key in [b'alpha', b'red', b'green', b'blue']:
        component = call_objc(color, key + b'Component', ret_type=ctypes.c_double)
        result = (result << 8) | int(component * 255)
    call_objc(pool, b'release')
    return result


def call_objc(receiver: any, selector: any, *args: list[str], ret_type: type = None):
    if receiver is None:
        return None
    if isinstance(receiver, bytes):
        _objc.objc_getClass.restype = ctypes.c_void_p
        receiver = _objc.objc_getClass(receiver)
    if isinstance(selector, bytes):
        _objc.sel_registerName.restype = ctypes.c_void_p
        selector = _objc.sel_registerName(selector)
    assert isinstance(selector, int)
    _objc.objc_msgSend.argtypes = [ctypes.c_void_p] * (2 + len(args))
    _objc.objc_msgSend.restype = ret_type or ctypes.c_void_p
    return _objc.objc_msgSend(receiver, selector, *args)


class DwmColorizationParams(ctypes.Structure):
    _fields_ = [
        ("ColorizationColor", ctypes.c_uint),
        ("ColorizationAfterglow", ctypes.c_uint),
        ("ColorizationColorBalance", ctypes.c_uint),
        ("ColorizationAfterglowBalance", ctypes.c_uint),
        ("ColorizationBlurBalance", ctypes.c_uint),
        ("ColorizationGlassReflectionIntensity", ctypes.c_uint),
        ("ColorizationOpaqueBlend", ctypes.c_uint)]
