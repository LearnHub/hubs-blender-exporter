from bpy.props import BoolProperty
from ..hubs_component import HubsComponent
from ..types import Category, PanelType, NodeType


class Moveable(HubsComponent):
    _definition = {
        'name': 'moveable',
        'display_name': 'Moveable',
        'category': Category.OBJECT,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'icon': 'VIEW_PAN',
        'version': (1, 0, 0)
    }
