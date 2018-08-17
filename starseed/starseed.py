import os
import re

from PIL import Image, ImageColor


blocktypes = {}
with open(os.path.join(os.path.dirname(__file__), 'blocktypes.csv'), 'r') as bfile:
    for btype in bfile.readlines():
        bid, name, colour = (s.strip() for s in btype.split(','))
        blocktypes[int(bid)] = ImageColor.getrgb(colour)


def generate_map(save):
    subgrids = {}
    blocks = {}

    for line in save.split(b'\x06'):
        s = re.match(rb'''
            (.)SUBGRID:
            (?P<x>[\d]+),
            (?P<y>[\d]+)
            (.)(?P<count>.)(.)
            ''', line, re.VERBOSE)
        g = re.match(rb'''
            ([^\d]?)
            (?P<type>[\d]+),
            (?P<x>[\d]+),
            (?P<y>[\d]+),
            (?P<info>[\d]+),
            ([-\w]+)\|([-\w]+)\|([-\w]+)\|([-\w]+)\|([-\w]+)
            ''', line, re.VERBOSE)
        m = re.match(rb'''
            (.)
            (?P<name>[A-Z]+)
            (.+)
            ''', line, re.VERBOSE)

        if s:
            gx, gy = int(s.group('x')), int(s.group('y'))
            subgrids[gx, gy] = ((ord(s.group('count')) - 1) / 2,
                                ord(s.group(1)),
                                ord(s.group(4)),
                                ord(s.group(6))
                                )

        elif g:
            bx, by = int(g.group('x')), int(g.group('y'))
            blocks[bx, by] = (int(g.group('type')),
                            int(g.group('info')),
                            ord(g.group(1)) if g.group(1) else 0,
                            int(g.group(6)),
                            g.group(7) != 'false'
                            )

        elif m:
            print(m.group('name').decode('utf-8'), ord(m.group(1)), [i for i in m.group(3)])

        else:
            print([i for i in line])

    for (gx, gy), subgrid in sorted(subgrids.items()):
        print('SUBGRID', (gx, gy), subgrid)

    for (bx, by), block in sorted(blocks.items()):
        print((bx, by), block)

    # w = max(x for x, _ in blocks.keys()) + 1
    # h = max(y for _, y in blocks.keys()) + 1
    w, h = 160, 160

    # ogx, ogy = 5, 9
    ox, oy = 80, 144
    scale = 5

    img = Image.new('RGB', (w, h), (255, 255, 255))
    pix = img.load()

    for y in range(h):
        # print(str(y).rjust(3), end='')
        for x in range(w):
            # print(str(blocks[x, y][2]).rjust(4) if (x, y) in blocks else '    ', end='')
            if (x, y) in blocks:
                pix[(x + ox) % w, (y + oy) % w] = blocktypes[blocks[x, y][0]]
        # print()

    return img.resize((w * scale, h * scale))


if __name__ == '__main__':
    with open('star.save', 'rb') as sfile:
        save = sfile.read()

    img = generate_map(save)

    img.save('starseed-map.png')
