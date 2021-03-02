# Installation

1. Create a `conda` environment with: `pandas` and `obspy`

2. Clone the repository:

    $ git clone https://github.com/lvanderlaat/lakiy_utils.git

3. Install the package in the `conda` environment:

    (env) $ cd lakiy_utils
    (env) $ pip install -e .

# Exporting waveforms for detection training (4 s samples)
## From Google Docs database to txt

Copy the daily records of the Google Docs file in a txt file with format name `%Y-%m-%d.txt`. Clean, format:

    Label_1- %H:%M, %H:%M,
    Label_2- %H:%M, %H:%M,
    ...

## Txt to Swarm csv

    $ txt-to-swarm %Y-%m-%d.txt

## If recent data (in FDSN memory)
### Download daily MSEED file

    $ download-waves %Y-%m-%d_Swarm.csv

### Repick in Swarm

Move the pick to the onset and add an end label.

### Check the file 

    $ check-swarm %Y-%m-%d_Swarm.csv

### Download and write segments

You must have a `csv` file with stations information (`network,station,channel` columns)

    $ download-segments %Y-%m-%d_segments.csv stations.csv outpath


## If not in FDSN memory
### Download daily MSEED files

    $ download-retro year julday stations.csv outpath

### Repick in Swarm

Move the pick to the onset and add an end label.
 
### Check the file 

    $ check-swarm %Y-%m-%d_Swarm.csv

### Trim segments

    trim-segments %Y-%m-%d_segments.csv path/to/mseed path/to/out

## Statistics of the database

    $ db-stats path/to/wfs

# Exporting waveforms for classification (complete event)

## Volcano-tectonic VT events
### Get catalog from Antelope

`db2TOMODD` extracts a `PHA` (`hypoDD` format) catalog from the Antelope database:

    db2TOMODD database output [julianstartdate julianenddate] [latmin latmax lonmin lonmax][Mmin][Nass] [EIDadd]

Example:

    db2TOMODD ../locate/vulca lakiy-VT 2014-001 2021-001  9.955  10.066 -83.809 -83.682 2 0

### Extract waves and catalog

Use the `PHA` catalog to extract waveforms (`.msd`) and event information (`xml`).

    (env) $ VT-extract PHA_FILE STATIONS.CSV OUTPUT

### Add TC.CVTR waveforms

For events occured before CVTR inclusion we add the correspondant waveforms:

    (env) $ waves-add-CVTR -i path/to/wfs_in -o path/to/wfs_out -w path/to/raw

### Pick coda

Copy the folder containing the extracted data to your computer.

Once the coda is picked, we copy the files to a new folder to discriminate picked events.

    (env) $ VT-pick -i path/to/wfs_in -o path/to/wfs_out -e eventid
    
### Convert to Lakiy format


