from __future__ import with_statement
import re
import xml.etree.cElementTree as etree
import pyflam3

_ugr_main_re = re.compile(
        '\s*(.*?)\s*{\s*gradient:\s*title="(.*?)"\s*smooth=(yes|no)\s*(.*?)\}', 
        re.DOTALL)

_ugr_inner_re = re.compile('\s*index=(\d+)\s*color=(\d+)')

def _blend_palette(palette, begin, end):
    if begin == end:
        return

    idx_range = float(end - begin)
    end_idx = end % 256
    begin_idx = begin % 256

    for c_idx in range(3):
        color_range = palette[end_idx][c_idx] - palette[begin_idx][c_idx]
        c = palette[begin_idx][0]
        v = color_range / idx_range

        for interp_idx in range(begin +1, end):
            c += v
            palette[interp_idx % 256] = c

def load_ugr_iter(filename, name=None):
    with open(filename) as  gradient_fd:
        text = gradient_fd.read()

    index_ratio = 255.0 / 399.0

    for match in _ugr_main_re.finditer(text):
        item_name, title, smooth, inner = match.groups()
        if not name or name == item_name:
            palette = pyflam3.Palette()
            palette.name = item_name
            palette.title = title
            palette.smooth = smooth

            #TODO: remove me
            for i in range(256):
                palette[i] = (0,0,0)

            indices = []
            for index, color in _ugr_inner_re.findall(inner):
                # -401 being a legal index is just stupid...
                while index < 0:
                    index += 400

                index = int(index)
                index = int(round(index * index_ratio))
                indices.append(index)
                color = int(color)

                r = (color & 0xFF0000) >> 16
                g = (color & 0xFF00) >> 8
                b = (color & 0xFF)

                palette[index] = (r, g, b)

            for idx in range(len(indices) - 1):
                x, y = indices[idx], indices[idx+1]
                _blend_palette(palette, indices[idx], indices[idx+1])

            if indices[0] != 0:
                _blend_palette(palette, indices[-1], indices[0] + 256)


            yield palette



def load_ugr(filename, name=None):
    return list(load_ugr_iter(filename, name))


if __name__ == '__main__':
    import sys
    filename, name = sys.argv[1:]

    palette = load_ugr(filename, name)[0]

    for idx, (r, g, b) in enumerate(palette):
        print 'idx=%03d r=%06.2f g=%06.2f b=%06.2f' % (idx, r, g, b)

