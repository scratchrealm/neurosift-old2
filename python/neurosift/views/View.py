from copy import deepcopy
import os
import shutil
import json
from abc import abstractmethod
from typing import List, Union
import kachery_cloud as kcl
import figurl as fig
import uuid


class View:
    """
    Base class for all views
    """
    def __init__(self, view_type: str, *, view_id: Union[str, None]=None, is_layout: bool=False, height=500) -> None:
        if view_id is None and not is_layout:
            raise Exception('View ID must be specified for non-layout views')
        self.type = view_type
        self.id = view_id
        self.is_layout = is_layout
        self._height = height
        self._selected_unit_ids = []
    def set_id(self, id: str):
        self.id = id
    @abstractmethod
    def to_dict(self) -> dict:
        return {}
    @abstractmethod
    def child_views(self) -> List['View']:
        return []
    @property
    def selected_unit_ids(self):
        return deepcopy(self._selected_unit_ids)
    def get_descendant_views_including_self(self):
        ret: List[View] = [self]
        for ch in self.child_views():
            a = ch.get_descendant_views_including_self()
            for v in a:
                ret.append(v)
        return ret
    def url_dict(self, *, label: str):
        from .Box import Box
        from .LayoutItem import LayoutItem
        if self.is_layout:
            all_views = self.get_descendant_views_including_self()
    
            # check that all views have different IDs
            view_ids_used = []
            for vv in all_views:
                if not vv.is_layout:
                    if vv.id in view_ids_used:
                        raise Exception(f'View ID {vv.id} is used more than once')
                    view_ids_used.append(vv.id)

            # # set the view IDs to make the figure deterministic
            # for i, vv in enumerate(all_views):
            #     vv.set_id(f'{i}')
            data = {
                'type': 'MainLayout',
                'layout': self.to_dict(),
                'views': [
                    {
                        'type': view.type,
                        'viewId': view.id,
                        'dataUri': _upload_data_and_return_uri(view.to_dict())
                    }
                    for view in all_views if not view.is_layout
                ]
            }
            view_url = os.getenv('NEUROSIFT_VIEW_URL', 'https://scratchrealm.github.io/neurosift/v1')
            F = fig.Figure(view_url=view_url, data=data)
            return F.url_dict(label=label)

        # Need to wrap it in a layout
        V = Box(
            direction='horizontal',
            items=[
                LayoutItem(self)
            ]
        )
        assert V.is_layout # avoid infinite recursion
        return V.url_dict(label=label)
    def save_figure(self, figure_id: str):
        # make sure figure_id does not have .. in it
        if '..' in figure_id:
            raise Exception('figure_id cannot contain ..')

        neurosift_dir = os.getenv('NEUROSIFT_DIR', None)
        if neurosift_dir is None:
            raise Exception('NEUROSIFT_DIR environment variable must be set')
        figure_path = f'{neurosift_dir}/figures/{figure_id}'
        if os.path.exists(figure_path):
            shutil.rmtree(figure_path)
        # create directory including parent directories
        os.makedirs(figure_path)

        from .Box import Box
        from .LayoutItem import LayoutItem
        if self.is_layout:
            all_views = self.get_descendant_views_including_self()
    
            # check that all views have different IDs
            view_ids_used = []
            for view in all_views:
                if not view.is_layout:
                    if view.id in view_ids_used:
                        raise Exception(f'View ID {view.id} is used more than once')
                    view_ids_used.append(view.id)
            
            for view in all_views:
                if not view.is_layout:
                    view_data = view.to_dict()
                    with open(f'{figure_path}/{view.id}.json', 'w') as f:
                        json.dump(fig.serialize_data(view_data), f)

            # # set the view IDs to make the figure deterministic
            # for i, vv in enumerate(all_views):
            #     vv.set_id(f'{i}')
            data = {
                'type': 'MainLayout',
                'layout': self.to_dict(),
                'views': [
                    {
                        'type': view.type,
                        'viewId': view.id,
                        'dataUri': f'./{view.id}.json'
                    }
                    for view in all_views if not view.is_layout
                ]
            }
            with open(f'{figure_path}/_main.json', 'w') as f:
                json.dump(data, f)
            return

        # Need to wrap it in a layout
        V = Box(
            direction='horizontal',
            items=[
                LayoutItem(self)
            ]
        )
        assert V.is_layout # avoid infinite recursion
        V.save_figure(figure_id=figure_id)
    def url(self, *, label: str):
        return fig.url_from_url_dict(self.url_dict(label=label))

def _upload_data_and_return_uri(data, *, local: bool=False):
    return kcl.store_json(fig.serialize_data(data), local=local)

def _random_id():
    return str(uuid.uuid4())[-12:]