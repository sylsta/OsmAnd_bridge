def decode_short_code(shortcode: str) -> list:
    """
    From a shortcode string, returns a list whith XY coordinates and zoom level
    Inspired by http://www.salesianer.de/util/shortcode.js
    Thanks H. v. Hatzfeld http://www.salesianer.de/hatzfeld/

    :param shortcode: a string which represents a pair of geographical coordinates and a zoom level
    :type shortcode:
    :return: Y coordinates, X coordinates, zoom level
    :rtype: real, real, int
    """

    char_array = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_~"
    i = 0
    x = 0
    y = 0
    z = -8
    for i in range(len(shortcode)):
        digit = char_array.find(shortcode[i])
        if digit == -1:
            break
        x <<= 3
        y <<= 3

        for j in range(2, -1, -1):
            # x |= ((digit & (1 << (j+j+1))) == 0 ? 0 : (1 << j))
            if (digit & (1 << (j + j + 1))) == 0:
                x |= 0
            else:
                x |= (1 << j)
            # y |= ((digit & (1 << (j + j))) == 0 ? 0: (1 << j));
            if (digit & (1 << (j + j))) == 0:
                y |= 0
            else:
                y |= (1 << j)
        z += 3;
    x = x * math.pow(2, 2 - 3 * i) * 90 - 180
    y = y * math.pow(2, 2 - 3 * i) * 45 - 90

    if i < len(shortcode) and char_array.find(shortcode[i]) == "-":
        z -= 2
        if i + 1 < len(shortcode) and char_array.find(shortcode[i + 1]) == "-":
            z += 1

    return [y, x, z]
