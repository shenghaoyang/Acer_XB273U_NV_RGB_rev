# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

from collections.abc import Sequence
from typing import Tuple
import struct
import io

# Magic byte sequence located at the start of the array.
MAGIC_SEQUENCE = b"\x0c\x02\x00"
# Maximum number of controllable LEDs.
LEN_MAX = 90
# LED strip index.
STRIP_INDEX = 0x0F
# Report length in bytes.
REPORT_LENGTH = 0x175
# Offset in the report buffer at which RGB data starts.
RGB_DATA_OFFSET = 13
# Report type for individual LED control.
REPORT_TYPE = 0x2A


def generate_report(rgb: Sequence[Tuple[int, int, int]]) -> bytes:
    """
    Generate a OUT report to control the all LEDs individually.

    :param rgb: tuple of ``(r, g, b)`` values for each LED.
        Accepts a maximum of 90 elements. LEDs for which intensity
        values are unspecified are commanded to turn off.
    """
    out = bytearray(REPORT_LENGTH)
    out[: len(MAGIC_SEQUENCE)] = MAGIC_SEQUENCE
    length = len(rgb)
    if length > LEN_MAX:
        raise ValueError("too many elements")

    out[3] = length
    out[4] = STRIP_INDEX

    for i, idata in enumerate(rgb):
        try:
            struct.pack_into("=3B", out, i * 3 + RGB_DATA_OFFSET, *idata)
        except struct.error:
            raise ValueError("intensity component value out of range ([0, 255])")

    return bytes(out)


def send_report(to: io.RawIOBase, report: bytes):
    """
    Writes a report an opened ``hidraw`` device file.

    Does not flush any buffers if the file was opened in
    buffered mode.

    :param to: opened file.
    :param report: report generated by ``generate_report``.
    """
    out = struct.pack("<B", REPORT_TYPE) + report
    to.write(out)
