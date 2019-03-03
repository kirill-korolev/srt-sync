import os
import sys
from datetime import datetime, timedelta


def find_blocks(file):
    line = file.readline()

    blocks = []
    block = ""

    while line:

        if line != "\n":
            block += line
        else:
            blocks.append(block)
            block = ""

        line = file.readline()

    return blocks


def parse_time_shift(ts):
    length = len(ts)
    i = 0
    j = length

    if ts[0] == "-" or ts[0] == "+":
        i = 1
    elif not ts[0].isdigit():
        raise ValueError("unknown time shift prefix: {0}".format(ts[0]))

    if ts[length - 1] == "s" or ts[length - 1] == "m":
        j = length - 1
    elif not ts[length - 1].isdigit():
        raise ValueError("unknown time shift suffix: {0}".format(ts[length - 1]))

    secs = int(ts[i: j])

    if ts[0] == "-":
        secs = -secs

    if ts[length - 1] == "m":
        secs *= 60

    return secs


def main():
    MIN_ARG_LEN = 4

    if len(sys.argv) < MIN_ARG_LEN:
        raise RuntimeError("usage: python srt.py input.srt output.srt (+-)Ns")

    _, srt_file_path, output_srt_path, time_shift = sys.argv

    if not os.path.exists(srt_file_path):
        raise RuntimeError("cannot open {0}: file doesn't exist")

    ts = parse_time_shift(time_shift)

    with open(srt_file_path) as srt_file, open(output_srt_path, "w") as output:
        blocks = find_blocks(srt_file)

        for block in blocks:

            lines = block.split(sep="\n")

            if len(lines) < 2:
                raise ValueError("cannot parse that SRT format")

            time_str: str = lines[1]
            times = [list(map(lambda t: t.strip(), time.split(sep=","))) for time in time_str.split(sep="-->")]

            updated = []

            for t_str, ms in times:
                time_s = datetime.strptime(t_str, "%H:%M:%S")

                time_s += timedelta(seconds=ts)
                t_str_new = "{0},{1}".format(datetime.strftime(time_s, "%H:%M:%S"), ms)
                updated.append(t_str_new)

            new_line = "{0} --> {1}".format(*updated)
            new_block = "{0}\n{1}\n{2}\n".format(lines[0], new_line, "\n".join(lines[2:]))

            output.write(new_block)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stdout)