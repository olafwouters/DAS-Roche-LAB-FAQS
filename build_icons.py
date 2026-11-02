from pathlib import Path
import struct
import zlib

BG = (250, 249, 252)
INK = (41, 39, 51)
OUTER = [(14, 1.14), (25.75, 7.57), (25.75, 20.43), (14, 26.86), (2.25, 20.43), (2.25, 7.57)]
INNER = [(14, 2.86), (24.25, 8.43), (24.25, 19.57), (14, 25.14), (3.75, 19.57), (3.75, 8.43)]

def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

def render(size):
    scale = 4
    width = size * scale
    mask = bytearray(width * width)
    def polygon(points, value):
        points = [(width / 2 + (x - 14) * width * .65 / 28, width / 2 + (y - 14) * width * .65 / 28) for x, y in points]
        for y in range(width):
            scan = y + .5
            xs = []
            for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
                if min(ay, by) <= scan < max(ay, by):
                    xs.append(ax + (scan - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                left = max(0, int(min(xs) + .5))
                right = min(width, int(max(xs) + .5))
                mask[y * width + left:y * width + right] = bytes([value]) * (right - left)
    polygon(OUTER, 255)
    polygon(INNER, 0)
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            total = sum(sum(mask[(y * scale + dy) * width + x * scale:(y * scale + dy) * width + x * scale + scale]) for dy in range(scale))
            alpha = total / (255 * scale * scale)
            raw.extend(round(bg + (ink - bg) * alpha) for bg, ink in zip(BG, INK))
    return bytes([137, 80, 78, 71, 13, 10, 26, 10]) + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')

def main(output=Path('.')):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for size in (180, 192, 512):
        (output / f'webapp-hex-v2-{size}.png').write_bytes(render(size))
    (output / 'webapp-hex-v2-maskable.png').write_bytes((output / 'webapp-hex-v2-512.png').read_bytes())

if __name__ == '__main__':
    main()
