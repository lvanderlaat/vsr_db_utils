# Other dependencies
from matplotlib import mlab
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
from obspy import read
from scipy import stats


rcParams['keymap.home'] = 'r'
rcParams['keymap.zoom'] = 'd'
rcParams['keymap.quit'] = 'f'


def spectrogram(tr, ax, get_v=True, nfft=256, mult=8, per_lap=.9,
                ylim=(0.1, 25), dbscale=True, cmap='jet', std_factor=1.7):

    nlap = int(nfft * float(per_lap))

    Sxx, f, t = mlab.specgram(tr.data, Fs=tr.stats.sampling_rate, NFFT=nfft,
                              noverlap=nlap, pad_to=mult * nfft)

     # calculate half bin width
    halfbin_time = (t[1] - t[0]) / 2.0
    halfbin_freq = (f[1] - f[0]) / 2.0
    f = np.concatenate((f, [f[-1] + 2 * halfbin_freq]))
    t = np.concatenate((t, [t[-1] + 2 * halfbin_time]))
    # center bin
    t -= halfbin_time
    f -= halfbin_freq
    if get_v:
        data = np.log(Sxx.flatten())
        data = data[np.isfinite(data)]
        hist, bin_edges = np.histogram(data, bins=100)
        idx = np.argmax(hist)
        mode = (bin_edges[idx] + bin_edges[idx+1])/2
        vmin = mode-std_factor*data.std()
        vmax = mode+std_factor*data.std()
    else:
        vmin = None
        vmax = None

    if dbscale:
        specgram = ax.pcolormesh(t, f, np.log(Sxx), cmap=cmap, vmin=vmin,
                                  vmax=vmax)
    else:
        specgram = ax.pcolormesh(t, f, (Sxx), cmap=cmap, vmin=vmin, vmax=vmax)

    ax.set_ylim(ylim)
    return


def pick(tr, freqmin=1, freqmax=25, p=None):
    tr_spectrogram = tr.copy()
    tr.detrend()
    tr.filter('bandpass', freqmin=freqmin, freqmax=freqmax)

    plt.style.use('dark_background')
    time = np.arange(0, tr.stats.npts/tr.stats.sampling_rate, tr.stats.delta)

    # To avoid: 
    # ValueError: x and y must have same first dimension, but have shapes ...
    if len(time) > len(tr.data):
        time = time[:-1]

    fig = plt.figure(figsize=(13, 6.8))

    fig.suptitle(
        (
            f'{tr.stats.station}-{tr.stats.channel}\n'
            'Shortcut-keys:    '
            f'{rcParams["keymap.zoom"][0]}: enable zoom    '
            f'{rcParams["keymap.home"][0]}: reset zoom    '
            f'{rcParams["keymap.quit"][0]}: next\n'
            'Mouse:'
            'Left-click: zoom    '
            'Right-click: pick\n'
        )
    )

    fig.subplots_adjust(left=.05, bottom=.07, right=.97, top=0.90, wspace=0,
                        hspace=.07)

    _ax1 = fig.add_subplot(211)

    ax1 = fig.add_subplot(211, zorder=2)
    ax1.plot(time, tr.data, c=(0, 1, 0), linewidth=0.7)
    ax1.set_xlim(time.min(), time.max())
    ax1.set_ylabel('Amplitude [m/s]')
    ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, 0), useMathText=True)
    label = str(tr.stats['starttime'])[:-8].replace('T',' ')+ ' UTC'
    ax1.text(.75, .9, label, horizontalalignment='center',
             verticalalignment='center', transform=ax1.transAxes, fontsize=10)
    ax1.axis("off")

    # Re-scale with zoom
    _ax1.set_navigate(False)
    _ax1.set_xlim(ax1.get_xlim())
    _ax1.set_ylim(ax1.get_ylim())


    ax2 = fig.add_subplot(212, sharex=ax1)
    spectrogram(tr, ax2)
    ax2.set_ylabel('Frequency [Hz]')
    ax2.set_xlabel('Time [s]')

    global times
    times = []
    def _pick(event):
        if event.button == 3:
            for ax in [ax1, ax2]:
                ax.axvline(x=event.xdata, linewidth=2, c='r')
            t = tr.stats.starttime + event.xdata
            times.append(t)

    def on_lims_change(axes):
        try:
            xmin, xmax = ax1.get_xlim()
            _ax1.set_xlim(xmin, xmax)
            y = tr.data[np.where((time >= xmin) & (time <= xmax))]

            margin = (y.max() - y.min()) * 0.1
            _ax1.set_ylim(y.min()-margin, y.max()+margin)
            ax1.set_ylim(y.min()-margin, y.max()+margin)
        except:
            return

    ax1.callbacks.connect('xlim_changed', on_lims_change)
    ax1.callbacks.connect('ylim_changed', on_lims_change)

    if p is not None:
        for ax in [ax1, ax2]:
            ax.axvline(x=p.time-tr.stats.starttime, linewidth=2, c='r')

    fig.canvas.mpl_connect('button_press_event', _pick)
    plt.show()
    return times
