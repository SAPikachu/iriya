from ctypes import (
    windll, WinError, c_wchar_p, c_ushort,
)

__all__ = ["FontContext"]

CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateFont = windll.gdi32.CreateFontW
SelectObject = windll.gdi32.SelectObject
GetGlyphIndices = windll.gdi32.GetGlyphIndicesW
DeleteObject = windll.gdi32.DeleteObject
DeleteDC = windll.gdi32.DeleteDC


def error_checker(error_value=0):
    def _check(result, func, args):
        if result == error_value:
            raise WinError()

        return result

    return _check


CreateCompatibleDC.errcheck = error_checker()
CreateCompatibleDC.restype = int
CreateFont.errcheck = error_checker()
CreateFont.restype = int
SelectObject.errcheck = error_checker(-1)
SelectObject.restype = int
GetGlyphIndices.errcheck = error_checker(-1)
GetGlyphIndices.restype = int

FW_NORMAL = 400
FW_BOLD = 700

DEFAULT_CHARSET = 1

OUT_DEFAULT_PRECIS = 0
CLIP_DEFAULT_PRECIS = 0
DEFAULT_QUALITY = 0
DEFAULT_PITCH_AND_FAMILY = 0

GGI_MARK_NONEXISTING_GLYPHS = 1


class FontContext:
    def __init__(self, name, bold=False, italics=False):
        self.dc = self.font = self.old_font = None
        self.dc = CreateCompatibleDC(None)
        self.font = CreateFont(
            0, 0, 0, 0, FW_BOLD if bold else FW_NORMAL, bool(italics),
            False, False, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
            CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH_AND_FAMILY,
            c_wchar_p(name)
        )
        self.old_font = SelectObject(self.dc, self.font)

    def __del__(self):
        try:
            if self.old_font and SelectObject:
                SelectObject(self.dc, self.old_font)
        except OSError:
            pass

        if self.font and DeleteObject:
            DeleteObject(self.font)

        if self.dc and DeleteDC:
            DeleteDC(self.dc)

    def check(self, str):
        if not str:
            return []

        out_buffer = (c_ushort * (len(str) + 1))()
        GetGlyphIndices(
            self.dc, c_wchar_p(str), len(str), out_buffer,
            GGI_MARK_NONEXISTING_GLYPHS,
        )
        return [str[i] for i in range(len(str))
                if out_buffer[i] == 0xffff]
