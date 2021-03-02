FNAME_FMT = '{label}.{year}.{julday:03d}.{hour:02d}.{minute:02d}.{second:02d}'

MSD_FNAME_FMT = FNAME_FMT + '.mseed'
JSN_FNAME_FMT = FNAME_FMT + '.json'


def st_to_fname(label, st):
    starttime = min(tr.stats.starttime for tr in st)
    return dict(
        label  = label,
        year   = starttime.year,
        julday = starttime.julday,
        hour   = starttime.hour,
        minute = starttime.minute,
        second = starttime.second
    )
