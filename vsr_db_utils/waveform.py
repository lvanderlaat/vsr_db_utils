# Python Standard Library
from datetime import timedelta
from glob import glob
from os import path

# Other dependencies
import numpy as np
from obspy import Stream, read


DB_MSEED_PATH_FMT = (
    '{waves_path}/{year}/{julday:03d}/'
    'i4.{station}.{channel}.{year}{julday:03d}_0+'
)


def extract(waves_path, starttime, endtime, stations, channels=['*']):
    """ Extract waveforms from the database
    This function is useful to extract events in one or several channels
    Parameters
    ----------
    waves_path : str
        Path to waveforms
    starttime : obspy.UTCDateTime
        Start datetime
    endtime : obspy.UTCDateTime
        End datetime
    stations : list of str
        Station codes
    channels : list of str, optional
        Channel codes
    Returns
    -------
    st : obspy.Stream
        Waveforms
    """
    startdate = starttime.datetime
    enddate   = endtime.datetime

    st = Stream()

    for day in range(int((enddate - startdate).days + 1)):
        tt = (startdate + timedelta(day)).timetuple()
        year   = tt.tm_year
        julday = tt.tm_yday

        for station in stations:
            for channel in channels:
                filepath = DB_MSEED_PATH_FMT.format(
                    waves_path=waves_path,
                    year=year,
                    julday=julday,
                    station=station,
                    channel=channel
                )
                if len(glob(filepath)) > 0:
                    st += read(filepath, starttime=starttime, endtime=endtime)
                else:
                    print('{}.{} not found'.format(station, channel))
    return st


def lakiy_header(st):
    return ' '.join([tr.stats.station+'-'+tr.stats.channel[-1] for tr in st])


def _st_to_lakiy(st, label, outpath, header):
    X = np.array([tr.data for tr in st]).T

    t = min(tr.stats.starttime for tr in st)

    fname = (
        f'{t.year}{t.month:02d}{t.day:02d}'
        f'{t.hour:02d}{t.minute:02d}{t.second:02d}.{label}'
    )
    fname = path.join(outpath, fname)

    np.savetxt(fname, X, fmt='%.1f', delimiter=' ', newline='\n',
               header=header, comments='')


def st_to_lakiy(st, label, outpath, mode, window_length=3.99):
    st.sort()
    header = lakiy_header(st)

    if mode == 'detection':
        st.trim(
            max(tr.stats.starttime for tr in st),
            min(tr.stats.endtime for tr in st)
        )
        for _st in st.slide(window_length=window_length, step=window_length):
            _st_to_lakiy(_st, label, outpath, header)
    elif mode == 'classification':
        _st_to_lakiy(st, label, outpath, header)
    return
