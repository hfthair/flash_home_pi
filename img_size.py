#!/usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################################################################
# copy form imghdr
#############################################################################################################

tests = []

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'

tests.append(test_jpeg)

def test_png(h, f):
    if h.startswith(b'\211PNG\r\n\032\n'):
        return 'png'

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

tests.append(test_tiff)

def test_rgb(h, f):
    """SGI image library"""
    if h.startswith(b'\001\332'):
        return 'rgb'

tests.append(test_rgb)

def test_pbm(h, f):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

tests.append(test_pbm)

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

tests.append(test_pgm)

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

tests.append(test_ppm)

def test_rast(h, f):
    """Sun raster file"""
    if h.startswith(b'\x59\xA6\x6A\x95'):
        return 'rast'

tests.append(test_rast)

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    if h.startswith(b'#define '):
        return 'xbm'

tests.append(test_xbm)

def test_bmp(h, f):
    if h.startswith(b'BM'):
        return 'bmp'

tests.append(test_bmp)

def test_webp(h, f):
    if h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'

tests.append(test_webp)

def test_exr(h, f):
    if h.startswith(b'\x76\x2f\x31\x01'):
        return 'exr'

tests.append(test_exr)


def what(file, h=None):
    f = None
    try:
        if h is None:
            if isinstance(file, str):
                f = open(file, 'rb')
                h = f.read(32)
            else:
                location = file.tell()
                h = file.read(32)
                file.seek(location)
        for tf in tests:
            res = tf(h, f)
            if res:
                return res
    finally:
        if f: f.close()
    return None

###########################################################################
## get_image_size
##########################################################################
import struct
def get_image_size(fname):
    width, height = -1, -1
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return width, height
        imgtype = what(fname)
        if imgtype == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return width, height
            width, height = struct.unpack('>ii', head[16:24])
        elif imgtype == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imgtype == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return width, height
        else:
            return width, height
        return width, height

