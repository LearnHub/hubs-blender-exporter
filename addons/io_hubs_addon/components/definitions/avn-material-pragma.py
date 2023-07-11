from bpy.props import FloatProperty, EnumProperty, FloatVectorProperty, PointerProperty, BoolProperty, IntProperty
from ..hubs_component import HubsComponent
from ..types import Category, PanelType, NodeType


COMPRESSION_MODES = [
    ("none", "None", "Use original image file"),
    ("etc1s", "ETC1S", "ETC1S (~1 bit-per-pixel)"),
    ("uastc", "UASTC", "UASTC (~8 bits-per-pixel)")
]

class AvnMaterialPragma(HubsComponent):
    _definition = {
        'name': 'avn-material-pragma',
        'display_name': 'AVN Material Pragma',
        'category': Category.MEDIA,
        'node_type': NodeType.MATERIAL,
        'panel_type': [PanelType.MATERIAL],
        'icon': 'MODIFIER_DATA',
        'version': (1, 0, 0)
    }

    keepPbr: BoolProperty(
        name="Keep PBR",
        description="Keep the PBR settings rather than force the material to be unlit",
        default=False
    )

    keepMetallicRoughnessMap: BoolProperty(
        name="Keep Metallic Roughness Map",
        description="Keep the metallic roughness map (requires 'Keep PBR' to also be true)",
        default=False
    )

    keepNormalMap: BoolProperty(
        name="Keep Normal Map",
        description="Keep the normal map (requires 'Keep PBR' to also be true)",
        default=False
    )

    keepOcclusionMap: BoolProperty(
        name="Keep Occlusion Map",
        description="Keep the occlusion map (requires 'Keep PBR' to also be true)",
        default=False
    )

    keepEmissiveMap: BoolProperty(
        name="Keep Emmisive Map",
        description="Keep the emmisive map (requires 'Keep PBR' to also be true)",
        default=False
    )

    maxImageSize: IntProperty(
        name="Max Image Size", 
        description="Texture images larger than this will be downscaled", 
        subtype="UNSIGNED", 
        default=2048,
        min=1,
        max=8192
    )

    compressionMode: EnumProperty(
        name="Compression Mode",
        description="Compression mode to use for base and roughness maps",
        items=COMPRESSION_MODES,
        default="etc1s"
    )

    compressionModeNormalMap: EnumProperty(
        name="Compression Mode (Normal Maps)",
        description="Compression mode to use for normal maps",
        items=COMPRESSION_MODES,
        default="uastc"
    )
