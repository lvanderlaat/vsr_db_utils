# Python Standard Library

# Other dependencies
from obspy import UTCDateTime

# Local files


def get_blocks(cat_filepath):
    with open(cat_filepath) as f:
        text = f.read()
        return text.split('#')[1:]


def get_datetimes(block):
    date  = block.split('\n')[0]
    times = block.split('\n')[1].split(',')
    return [UTCDateTime(date+time) for time in times]


def iterate_days(cat_filepath):
    for block in get_blocks(cat_filepath):
        yield get_datetimes(block)


if __name__ == '__main__':
    cat_filepath = 'LF.txt'
    iterate_days(cat_filepath)

    for datetimes in iterate_days(cat_filepath):
        print(datetimes)

