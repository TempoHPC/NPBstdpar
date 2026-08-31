#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from statistics import mean, stdev

KEYS = ['total', 'rhs', 'xsolve', 'ysolve', 'zsolve']
LINE = re.compile(r'^\s*(total|rhs|xsolve|ysolve|zsolve)\s*:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)', re.I)


def comma(value):
    return f'{value:.6f}'.replace('.', ',')


def read_texts(argv):
    if len(argv) > 1:
        return [Path(name).read_text() for name in argv[1:]]
    return [sys.stdin.read()]


def main(argv):
    data = {key: [] for key in KEYS}
    for text in read_texts(argv):
        for line in text.splitlines():
            match = LINE.match(line)
            if match:
                data[match.group(1).lower()].append(float(match.group(2)))

    out = ['Metric;count;mean;stdev']
    for key in KEYS:
        vals = data[key]
        if not vals:
            out.append(f'{key};0;N/A;N/A')
        elif len(vals) == 1:
            out.append(f'{key};1;{comma(vals[0])};0,000000')
        else:
            out.append(f'{key};{len(vals)};{comma(mean(vals))};{comma(stdev(vals))}')

    text = '\n'.join(out) + '\n'
    Path('summary.txt').write_text(text)
    sys.stdout.write(text)


if __name__ == '__main__':
    main(sys.argv)
