"""Fake maya.api.OpenMayaUI over the stub Scene (D-027).

Models the M3dView/MImage surface the _mcp_visual module uses:
active3dView + portWidth/portHeight + getRendererName +
readColorBuffer + MImage create/convert/flip/writeToFile.
"""

from __future__ import annotations

from . import runtime
from .fakeqt import png_bytes


class MImage:
    kByte = 1
    kFloat = 5

    def __init__(self):
        self.width = 0
        self.height = 0
        self.channels = 4
        self.format = self.kByte
        self.flipped = False
        self._filled = False

    def create(self, width, height, channels=4, format=kByte):
        self.width = int(width)
        self.height = int(height)
        self.channels = int(channels)
        self.format = format

    def convertPixelFormat(self, format):
        self.format = format

    def verticalFlip(self):
        self.flipped = not self.flipped

    def writeToFile(self, path, outputType="png"):
        if not self._filled and self.width == 0:
            raise RuntimeError("MImage has no image data")
        with open(path, "wb") as fh:
            fh.write(png_bytes(self.width, self.height))
        return True


class _ViewWidget:
    def __init__(self, w, h):
        self._w, self._h = w, h

    def width(self):
        return self._w

    def height(self):
        return self._h


class M3dView:
    kViewport2Renderer = "vp2Renderer"

    def __init__(self, scene):
        self._scene = scene

    @classmethod
    def active3dView(cls):
        if runtime.scene is None:
            raise RuntimeError("maya stub not installed")
        return cls(runtime.scene)

    def getRendererName(self):
        return self.kViewport2Renderer

    def portWidth(self):
        return self._scene.viewport_size[0]

    def portHeight(self):
        return self._scene.viewport_size[1]

    def readColorBuffer(self, img, *_a):
        # Empty image: real VP1 path sizes it to the viewport.
        if img.width == 0 or img.height == 0:
            img.create(*self._scene.viewport_size, img.channels, img.format)
        img._filled = True
        return True

    def widget(self):
        return _ViewWidget(*self._scene.viewport_size)
