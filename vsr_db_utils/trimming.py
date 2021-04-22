# Python Standard Library
from os import path
import json

# Other dependencies
from obspy import Stream, read, UTCDateTime
from obspy.geodetics.base import locations2degrees
from obspy.taup import TauPyModel

# Local files
from vsr_db_utils.catalog.pha import iterate_PHA_cat
from vsr_db_utils.catalog.gdocs import iterate_days
from vsr_db_utils.catalog import tectonic
from vsr_db_utils.io import MSD_FNAME_FMT, XML_FNAME_FMT, st_to_fname, JSN_FNAME_FMT
from vsr_db_utils.waveform import extract, DB_MSEED_PATH_FMT


WAVES_PATH  = '/opt/rtsystem/wfs'


def get_eID(event):
    return event.resource_id.id.split('/')[-1]


def extract_pha(cat_filepath, stations, pre, pos, outpath, label):
    for i, ev in enumerate(iterate_PHA_cat((cat_filepath))):
        print(i)

        stations_in_event = set([
            pick.waveform_id.station_code for pick in ev.picks
            if pick.waveform_id.station_code in stations
        ])

        if len(stations_in_event) == 0:
            continue

        starttime = min([
            pick.time for pick in ev.picks
            if pick.waveform_id.station_code in stations
        ]) - pre

        endtime = max([
            pick.time for pick in ev.picks
            if pick.waveform_id.station_code in stations
        ]) + pos

        st = extract(WAVES_PATH, starttime, endtime, stations, channels=['HH*'])

        eventid = get_eID(ev)

        msd_outpath = path.join(
            outpath,
            MSD_FNAME_FMT.format(**st_to_fname(label, st))
        )
        xml_outpath = path.join(
            outpath,
            XML_FNAME_FMT.format(**st_to_fname(label, st))
        )

        st.write(msd_outpath, format='MSEED')
        ev.write(xml_outpath, format='QUAKEML')
    return


def extract_gdocs(cat_filepath, stations, pre, pos, outpath, label):
    for datetimes in iterate_days(cat_filepath):
        print(datetimes[0].date)

        st = Stream()
        for station in stations:
            for channel in ['HHE', 'HHN', 'HHZ']:
                filepath = DB_MSEED_PATH_FMT.format(
                    waves_path = WAVES_PATH,
                    year       = datetimes[0].year,
                    julday     = datetimes[0].julday,
                    station    = station,
                    channel    = channel
                )
                if path.isfile(filepath):
                    st += read(filepath)

        for datetime in datetimes:
            _st = st.slice(starttime=datetime-pre, endtime=datetime+pos)
            if len(_st) > 0:
                msd_outpath = path.join(
                    outpath,
                    MSD_FNAME_FMT.format(**st_to_fname(label, _st))
                )
                _st.write(msd_outpath, format='MSEED')
    return


def extract_tectonics(cat_filepath, stations, pre, pos, outpath, label,
                      latitude, longitude):
    model = TauPyModel(model='iasp91')

    for date, df in tectonic.iterate_days(cat_filepath):
        date = UTCDateTime(date)
        st = Stream()
        for station in stations:
            for channel in ['HHE', 'HHN', 'HHZ']:
                filepath = DB_MSEED_PATH_FMT.format(
                    waves_path = WAVES_PATH,
                    year       = date.year,
                    julday     = date.julday,
                    station    = station,
                    channel    = channel
                )
                if path.isfile(filepath):
                    st += read(filepath)

        for i, row in df.iterrows():
            print(row.time)
            source_depth_in_km = row.depth
            if source_depth_in_km < 0:
                source_depth_in_km = 0

            distance_in_degree = locations2degrees(
                row.latitude, row.longitude, latitude, longitude
            )

            arrivals = model.get_travel_times(
                source_depth_in_km = source_depth_in_km,
                distance_in_degree = distance_in_degree,
                phase_list=['p', 's', 'P', 'S', 'Pdiff', 'Sdiff']
            )

            origin_time = UTCDateTime(row.time)

            for arrival in arrivals:
                if arrival.name in ['p', 'P', 'Pdiff']:
                    p = origin_time + arrival.time

            for arrival in arrivals:
                if arrival.name in ['s', 'S', 'Sdiff']:
                    s = origin_time + arrival.time

            starttime = p - pre
            endtime   = s + pos

            _st = st.slice(starttime=starttime, endtime=endtime)
            if len(_st) > 0:
                msd_outpath = path.join(
                    outpath,
                    MSD_FNAME_FMT.format(**st_to_fname(label, _st))
                )
                _st.write(msd_outpath, format='MSEED')

            d = dict(
                longitude=row.longitude,
                latitude=row.latitude,
                depth=row.depth,
                magnitude=row.magnitude,
                time=row.time
            )

            station = ''
            for tr in st:
                if station == tr.stats.station:
                    continue
                station = tr.stats.station
                d[station] = {}
                d[station]['P']  = str(p)

            jsn_outpath = path.join(
                outpath,
                JSN_FNAME_FMT.format(**st_to_fname(label, _st))
            )
            with open(jsn_outpath, 'w') as f:
                json.dump(d, f, indent=4)
