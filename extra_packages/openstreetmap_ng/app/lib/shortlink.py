# functions to encode and decode short links
# See https://wiki.openstreetmap.org/wiki/Shortlink
# May be usefull later. Putted here since it was hard to find :/
# Taken from https://github.com/openstreetmap-ng/openstreetmap-ng/blob/1d641b53cc6cf2cfe35f4b34c7a04d7fb386a745/app/lib/shortlink.py

import cython

# 64 chars to encode 6 bits
_array = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~'
_array_map = {c: i for i, c in enumerate(_array)}
_array_map['@'] = _array_map['~']  # backwards compatibility


def shortlink_encode(lon: float, lat: float, zoom: int) -> str:
    """
    Encode a coordinate pair and zoom level into a shortlink code.
    """
    x: cython.uint = int(((lon + 180) % 360) * 11930464.711111112)  # (2 ** 32) / 360
    y: cython.uint = int((lat + 90) * 23860929.422222223)  # (2 ** 32) / 180
    c: cython.ulonglong = 0
    i: cython.int

    for i in range(31, -1, -1):
        c = (c << 2) | (((x >> i) & 1) << 1) | ((y >> i) & 1)

    d: cython.int = (zoom + 8) // 3
    r: cython.int = (zoom + 8) % 3

    if r > 0:  # ceil instead of floor
        d += 1

    str_list = ['-'] * (d + r)

    for i in range(d):
        digit: cython.int = (c >> (58 - 6 * i)) & 0x3F
        str_list[i] = _array[digit]

    return ''.join(str_list)


def shortlink_decode(s: str) -> tuple[float, float, int]:
    """
    Decode a shortlink code into a coordinate pair and zoom level.

    Returns a tuple of (lon, lat, z).
    """
    x: cython.uint = 0
    y: cython.uint = 0
    z: cython.int = 0
    z_offset: cython.int = 0

    for c in s:
        t: cython.int = _array_map.get(c, -1)

        if t == -1:
            z_offset -= 1
            continue

        for _ in range(3):
            x = (x << 1) | ((t >> 5) & 1)
            y = (y << 1) | ((t >> 4) & 1)
            t <<= 2

        z += 3

    x <<= 32 - z
    y <<= 32 - z

    return (
        (
            x * 8.381903171539307e-08  # 360 / (2 ** 32)
        )
        - 180,
        (
            y * 4.190951585769653e-08  # 180 / (2 ** 32)
        )
        - 90,
        z - 8 - (z_offset % 3),
    )

# ## Réécriture sans Cython
# # 64 chars to encode 6 bits
# _array = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~'
# _array_map = {c: i for i, c in enumerate(_array)}
# _array_map['@'] = _array_map['~']  # backward compatibility
#
# def shortlink_encode(lon: float, lat: float, zoom: int) -> str:
#     """
#     Encode a coordinate pair and zoom level into a shortlink code.
#     """
#     x = int(((lon + 180) % 360) * 11930464.711111112)  # (2 ** 32) / 360
#     y = int((lat + 90) * 23860929.422222223)            # (2 ** 32) / 180
#     c = 0
#
#     for i in range(31, -1, -1):
#         c = (c << 2) | (((x >> i) & 1) << 1) | ((y >> i) & 1)
#
#     d = (zoom + 8) // 3
#     r = (zoom + 8) % 3
#
#     if r > 0:
#         d += 1
#
#     str_list = ['-'] * (d + r)
#
#     for i in range(d):
#         digit = (c >> (58 - 6 * i)) & 0x3F
#         str_list[i] = _array[digit]
#
#     return ''.join(str_list)
#
# def shortlink_decode(s: str) -> tuple[float, float, int]:
#     """
#     Decode a shortlink code into a coordinate pair and zoom level.
#     Returns a tuple of (lon, lat, zoom).
#     """
#     x = 0
#     y = 0
#     z = 0
#     z_offset = 0
#
#     for c in s:
#         t = _array_map.get(c, -1)
#
#         if t == -1:
#             z_offset -= 1
#             continue
#
#         for _ in range(3):
#             x = (x << 1) | ((t >> 5) & 1)
#             y = (y << 1) | ((t >> 4) & 1)
#             t <<= 2
#
#         z += 3
#
#     x <<= 32 - z
#     y <<= 32 - z
#
#     lon = x * (360.0 / (2 ** 32)) - 180
#     lat = y * (180.0 / (2 ** 32)) - 90
#     zoom = z - 8 - (z_offset % 3)
#
#     return lon, lat, zoom
# def test_shortlink():
#     test_cases = [
#         (0.0, 0.0, 0),
#         (2.3522, 48.8566, 10),   # Paris
#         (77.2090, 28.6139, 12),  # New Delhi
#         (-74.0060, 40.7128, 15), # New York
#         (139.6917, 35.6895, 8),  # Tokyo
#         (151.2093, -33.8688, 5), # Sydney
#         (37.6173, 55.7558, 13),  # Moscow
#     ]
#
#     for lon, lat, zoom in test_cases:
#         encoded = shortlink_encode(lon, lat, zoom)
#         decoded_lon, decoded_lat, decoded_zoom = shortlink_decode(encoded)
#
#         print(f"Original: ({lon:.5f}, {lat:.5f}, {zoom})")
#         print(f"Encoded:  {encoded}")
#         print(f"Decoded: ({decoded_lon:.5f}, {decoded_lat:.5f}, {decoded_zoom})")
#
#         lon_ok = abs(lon - decoded_lon) < 1e-5
#         lat_ok = abs(lat - decoded_lat) < 1e-5
#         zoom_ok = zoom == decoded_zoom
#
#         assert lon_ok and lat_ok and zoom_ok, "Test failed!"
#         print("✅ Test passed.\n")
#
# if __name__ == "__main__":
#     test_shortlink()
