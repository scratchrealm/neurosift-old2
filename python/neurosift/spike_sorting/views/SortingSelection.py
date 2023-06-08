from typing import List
from .View import View


# The sorting_id parameter can be any string.
# It should uniquely point to a sorting so that the saved curation can be associated with that sorting

class SortingSelection(View):
    """
    Sorting selection control view
    """
    def __init__(self, **kwargs) -> None:
        super().__init__('SortingSelection', **kwargs)
    def to_dict(self) -> dict:
        ret = {
            'type': self.type
        }
        return ret
    def child_views(self) -> List[View]:
        return []
