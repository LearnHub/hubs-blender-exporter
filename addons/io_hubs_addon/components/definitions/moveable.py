from bpy.props import BoolProperty
from ..hubs_component import HubsComponent
from ..types import Category, PanelType, NodeType
from .networked import migrate_networked


class Moveable(HubsComponent):
    _definition = {
        'name': 'moveable',
        'display_name': 'Moveable',
        'category': Category.OBJECT,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'deps': ['networked'],
        'icon': 'VIEW_PAN',
        'version': (1, 0, 1)
    }

    def migrate(self, migration_type, panel_type, instance_version, host, migration_report, ob=None):
        migration_occurred = False
        if instance_version < (1, 0, 1):
            migration_occurred = True
            migrate_networked(host)

        return migration_occurred
