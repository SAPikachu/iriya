from ctypes import (
    windll, WinError, c_wchar_p, c_ushort, create_unicode_buffer, sizeof,
)
import logging

__all__ = ["FontContext"]

log = logging.getLogger(__name__)

CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateFont = windll.gdi32.CreateFontW
SelectObject = windll.gdi32.SelectObject
GetGlyphIndices = windll.gdi32.GetGlyphIndicesW
DeleteObject = windll.gdi32.DeleteObject
DeleteDC = windll.gdi32.DeleteDC
GetTextFace = windll.gdi32.GetTextFaceW


def error_checker(error_value=0):
    def _check(result, func, args):
        if result == error_value:
            raise WinError()

        return result

    return _check


CreateCompatibleDC.errcheck = error_checker()
CreateFont.errcheck = error_checker()
SelectObject.errcheck = error_checker(-1)
GetGlyphIndices.errcheck = error_checker(-1)
GetTextFace.errcheck = error_checker()

FW_NORMAL = 400
FW_BOLD = 700

DEFAULT_CHARSET = 1

OUT_DEFAULT_PRECIS = 0
CLIP_DEFAULT_PRECIS = 0
DEFAULT_QUALITY = 0
DEFAULT_PITCH_AND_FAMILY = 0

GGI_MARK_NONEXISTING_GLYPHS = 1


def create_font_simple(name, bold, italics):
    return CreateFont(
        0, 0, 0, 0, FW_BOLD if bold else FW_NORMAL, bool(italics),
        False, False, DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
        CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH_AND_FAMILY,
        c_wchar_p(name)
    )


class FontContext:
    def __init__(self, name, bold=False, italics=False):
        self.dc = self.font = self.old_font = None
        self.dc = CreateCompatibleDC(None)

        name_buffer = create_unicode_buffer(2048)
        fallback_font = create_font_simple(
            name + "-NONEXISTENT-" + str(id(self)), bold, italics,
        )
        try:
            self.old_font = SelectObject(self.dc, fallback_font)
            GetTextFace(self.dc, sizeof(name_buffer) - 1, name_buffer)
        finally:
            SelectObject(self.dc, self.old_font)
            DeleteObject(fallback_font)

        fallback_font_name = name_buffer.value
        log.debug("Name of fallback font: %s", fallback_font_name)

        self.font = create_font_simple(name, bold, italics)
        self.old_font = SelectObject(self.dc, self.font)
        GetTextFace(self.dc, sizeof(name_buffer) - 1, name_buffer)
        log.debug("Name of created font: %s", name_buffer.value)
        if (name_buffer.value == fallback_font_name and
            name.lower() != fallback_font_name.lower()):
            log.warn("Font %s is either not installed or the default font in this system.", name)

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
