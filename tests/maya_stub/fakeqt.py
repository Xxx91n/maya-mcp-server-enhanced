"""Fake PySide6 surface for the _mcp_visual contract tests (D-027).

Honest about *dimensions and byte contracts*, never about pixels:
QImage parses a real PNG IHDR on load, does real KeepAspectRatio fit
math on scaled(), and save() emits deterministic bytes with the
correct format magic (real zlib PNG for PNG, JFIF magic for JPEG).
"""

from __future__ import annotations

import struct
import types
import zlib


def png_bytes(w, h, rgb=(90, 120, 160)):
    """Deterministic, *valid* PNG (zlib-encoded) for the given size."""

    def chunk(tag, data):
        body = tag + data
        return (
            struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", int(w), int(h), 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * int(w)
    raw = row * int(h)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a png")
    return struct.unpack(">II", data[16:24])


def jpeg_bytes(w, h, quality=80):
    """Deterministic JFIF-magic bytes (not a real jpeg; contract layer)."""
    payload = f"FAKEJPEG w={int(w)} h={int(h)} q={int(quality)}"
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + payload.encode()


class QImage:
    """Dimension/byte-contract QImage fake (never asserts pixels)."""

    def __init__(self, *args):
        self._w = 0
        self._h = 0
        self._null = True
        if len(args) == 1 and isinstance(args[0], str):
            with open(args[0], "rb") as fh:
                self._w, self._h = _png_size(fh.read())
            self._null = False
        elif len(args) >= 2:
            self._w, self._h = int(args[0]), int(args[1])
            self._null = False

    def isNull(self):
        return self._null

    def width(self):
        return self._w

    def height(self):
        return self._h

    def scaled(self, w, h, aspectMode=None, transformMode=None):
        """QImage.scaled(w, h, aspectRatioMode, transformMode)."""
        out = QImage()
        if aspectMode == Qt.KeepAspectRatio:
            s = min(w / self._w, h / self._h)
            out._w = max(1, round(self._w * s))
            out._h = max(1, round(self._h * s))
        else:
            out._w, out._h = int(w), int(h)
        out._null = False
        return out

    def save(self, target, fmt=None, quality=-1):
        fmt = (fmt or "PNG").upper()
        if fmt == "PNG":
            data = png_bytes(self._w, self._h)
        else:
            data = jpeg_bytes(self._w, self._h, quality)
        if isinstance(target, str):
            with open(target, "wb") as fh:
                fh.write(data)
            return True
        if hasattr(target, "write"):
            target.write(data)
            return True
        return False


class QBuffer:
    def __init__(self):
        self._buf = bytearray()
        self._open = False

    def open(self, mode):
        self._open = True
        return True

    def write(self, data):
        self._buf.extend(bytes(data))
        return len(data)

    def close(self):
        self._open = False

    def data(self):
        return bytes(self._buf)


class QIODevice:
    class OpenModeFlag:
        WriteOnly = 2

    WriteOnly = 2


class Qt:
    class AspectRatioMode:
        IgnoreAspectRatio = 0
        KeepAspectRatio = 1
        KeepAspectRatioByExpanding = 2

    class TransformationMode:
        FastTransformation = 0
        SmoothTransformation = 1

    IgnoreAspectRatio = 0
    KeepAspectRatio = 1
    SmoothTransformation = 1


def make_pyside6():
    """Build a fake 'PySide6' module exposing QtGui.QImage/QtCore.QBuffer/Qt."""
    mod = types.ModuleType("PySide6")
    qtgui = types.ModuleType("PySide6.QtGui")
    qtcore = types.ModuleType("PySide6.QtCore")
    qtgui.QImage = QImage
    qtcore.QBuffer = QBuffer
    qtcore.QIODevice = QIODevice
    qtcore.Qt = Qt
    mod.QtGui = qtgui
    mod.QtCore = qtcore
    return mod
