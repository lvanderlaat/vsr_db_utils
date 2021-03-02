from obspy.core.util.misc import _seed_id_map
from obspy.io.hypodd.pha import _block2event


def blocks(cat_filepath):
    with open(cat_filepath) as f:
        text = f.read()
    return text.split('#')[1:]


def block2event(block):
    ID_DEFAULT = 'OV.{}..{}'      # network.station.location.channel
    PH2COMP    = {'P': 'HHZ', 'S': 'HHN'}
    return _block2event(block, _seed_id_map(None, None), ID_DEFAULT, PH2COMP)


def iterate_PHA_cat(cat_filepath):
    for block in blocks(cat_filepath):
        yield block2event(block)

