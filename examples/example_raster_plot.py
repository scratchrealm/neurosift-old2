import os
from typing import Optional, Union
from abc import abstractmethod
import json

import kachery_cloud as kcl
import neurosift.spike_sorting.views as ssv
import numpy as np
import zarr

import neurosift as ns


def main():
    create_raster_plot()

class SpikeTrains:
    def __init__(self, *, start_time: Optional[float]=None, end_time: Optional[float]=None):
        self.start_time = start_time
        self.end_time = end_time
        self._spike_trains = []
    def add_spike_train(self, *, unit_id: Union[str, int], spike_times_sec: np.ndarray):
        self._spike_trains.append({
            'unit_id': unit_id,
            'spike_times_sec': spike_times_sec
        })
    def save(self, object_id: str, *, block_size_sec: float=60 * 10):
        if not object_id.endswith('.zarr'):
            raise Exception('Object ID must end with .zarr')
        neurosift_dir = os.getenv('NEUROSIFT_DIR', None)
        if not neurosift_dir:
            raise Exception('NEUROSIFT_DIR environment variable must be set')
        path = os.path.join(neurosift_dir, 'objects', object_id)
        # create parent directories if necessary
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if self.start_time is None:
            start_time = np.min([np.min(st['spike_times_sec']) for st in self._spike_trains])
        else:
            start_time = self.start_time
        
        if self.end_time is None:
            end_time = np.max([np.max(st['spike_times_sec']) for st in self._spike_trains])
        else:
            end_time = self.end_time

        store = zarr.DirectoryStore(path)
        root = zarr.group(store=store, overwrite=True)
        root.attrs['type'] = 'neurosift.SpikeTrains'
        root.attrs['version'] = '1'
        root.attrs['start_time'] = start_time
        root.attrs['end_time'] = end_time
        root.attrs['units'] = [
            {
                'unit_id': st['unit_id'],
                'num_spikes': len(st['spike_times_sec'])
            }
            for st in self._spike_trains
        ]
        root.attrs['total_num_spikes'] = np.sum([len(st['spike_times_sec']) for st in self._spike_trains])

        blocks = []
        t0 = start_time
        while t0 < end_time:
            t1 = t0 + block_size_sec
            blocks.append({
                'start_time': t0,
                'end_time': t1
            })
            t0 = t1

        root.attrs['blocks'] = blocks

        blocks_group = root.create_group('blocks')
        for i, block in enumerate(blocks):
            block_group = blocks_group.create_group(str(i))
            block_group.attrs['start_time'] = block['start_time']
            block_group.attrs['end_time'] = block['end_time']
            spike_trains_for_block = []
            for st in self._spike_trains:
                tt = st['spike_times_sec']
                inds = np.where((tt >= block['start_time']) & (tt < block['end_time']))[0]
                spike_trains_for_block.append({
                    'unit_id': st['unit_id'],
                    'spike_times_sec': tt[inds]
                })
            block_group.attrs['units'] = [
                {
                    'unit_id': st['unit_id'],
                    'num_spikes': len(st['spike_times_sec'])
                }
                for st in spike_trains_for_block
            ]
            block_group.attrs['total_num_spikes'] = np.sum([len(st['spike_times_sec']) for st in spike_trains_for_block])
            all_spikes = np.concatenate([st['spike_times_sec'] for st in spike_trains_for_block])
            block_group.create_dataset('spike_trains', data=all_spikes, chunks=(100000,), dtype=np.float32)
class NeurosiftView:
    def __init__(self, type: str):
        self.type = type
    @abstractmethod
    def to_dict(self) -> dict:
        pass
    def save_figure(self, figure_id: str):
        if not figure_id.endswith('.ns'):
            raise Exception('Figure ID must end with .ns')
        neurosift_dir = os.getenv('NEUROSIFT_DIR', None)
        if not neurosift_dir:
            raise Exception('NEUROSIFT_DIR environment variable must be set')
        path = os.path.join(neurosift_dir, 'figures', figure_id)
        # create parent directories if necessary
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

class RasterPlotView(NeurosiftView):
    def __init__(self, *, spike_trains_id: str):
        self.spike_trains_id = spike_trains_id
        super().__init__('neurosift.RasterPlotView')
    def to_dict(self):
        return {
            'type': self.type,
            'spike_trains_uri': f'$dir/objects/{self.spike_trains_id}'
        }

class LayoutItem:
    """
    A layout item - wraps a view inside a layout
    """
    def __init__(self,
        view: NeurosiftView, *,
        min_size: Union[None, float]=None,
        max_size: Union[None, float]=None,
        stretch: Union[None, float]=None,
        title: Union[None, str]=None,
        collapsible: Union[None, bool]=None
    ) -> None:
        self.view = view
        self.min_size = min_size
        self.max_size = max_size
        self.stretch = stretch
        self.title = title
        self.collapsible = collapsible
    def properties_dict(self):
        ret = {}
        if self.min_size is not None:
            ret['minSize'] = self.min_size
        if self.max_size is not None:
            ret['maxSize'] = self.max_size
        if self.stretch is not None:
            ret['stretch'] = self.stretch
        if self.title is not None:
            ret['title'] = self.title
        if self.collapsible is not None:
            ret['collapsible'] = self.collapsible
        return ret

class BoxLayout(NeurosiftView):
    def __init__(self, *,
        direction: str,
        items: list,
        scrollbar: bool = False,
        show_titles: bool = False
    ):
        self.direction = direction
        self.items = items
        self.scrollbar = scrollbar
        self.show_titles = show_titles
        super().__init__('neurosift.BoxLayout')
    def to_dict(self):
        return {
            'type': self.type,
            'direction': self.direction,
            'scrollbar': self.scrollbar,
            'show_titles': self.show_titles,
            'items': [
                {
                    'view': item.view.to_dict(),
                    'properties': item.properties_dict()
                }
                for item in self.items
            ]
        }

def create_raster_plot():
    # from rp on 2/1/23
    spikes_npy_uri = 'sha1://e44f638ab42f09d328eda0ab6c511fa5ae288198/spikes.npy'
    spikes = np.load(kcl.load_file(spikes_npy_uri), allow_pickle=True)

    spike_trains = SpikeTrains()
    for i, s in enumerate(spikes):
        spike_trains.add_spike_train(
            unit_id=(i + 1),
            spike_times_sec=s.astype(np.float32)
        )
    spike_trains.save('tests/example_spike_trains.zarr')

    raster_plot = RasterPlotView(
        spike_trains_id='tests/example_spike_trains.zarr'
    )
    raster_plot.save_figure('test1/example_raster_plot.ns')

    box_layout = BoxLayout(
        direction='vertical',
        items=[
            LayoutItem(
                view=raster_plot,
                stretch=1
            ),
            LayoutItem(
                view=raster_plot,
                stretch=2
            )
        ]
    )
    box_layout.save_figure('test1/test_box_layout.ns')

if __name__ == '__main__':
    main()