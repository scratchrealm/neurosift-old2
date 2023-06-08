import kachery_cloud as kcl
import numpy as np
import neurosift.spike_sorting.views as ssv


def main():
    raster_plot = create_raster_plot(view_id='raster')
    raster_plot.save_figure('tests/raster_plot')

def create_raster_plot(view_id: str):
    # from rp on 2/1/23
    spikes_npy_uri = 'sha1://e44f638ab42f09d328eda0ab6c511fa5ae288198/spikes.npy'
    spikes = np.load(kcl.load_file(spikes_npy_uri), allow_pickle=True)

    plots: list[ssv.RasterPlotItem] = []
    end_time_sec = 0
    for i, s in enumerate(spikes):
        item = ssv.RasterPlotItem(unit_id=(i + 1), spike_times_sec=s.astype(np.float32))
        end_time_sec = np.float32(np.maximum(end_time_sec, np.max(s)))
        plots.append(item)
    raster_plot = ssv.RasterPlot(
        view_id=view_id,
        start_time_sec=0,
        end_time_sec=end_time_sec,
        plots=plots,
        hide_toolbar=True
    )
    return raster_plot

if __name__ == '__main__':
    main()