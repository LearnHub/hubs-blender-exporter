from bpy.props import FloatProperty, EnumProperty, FloatVectorProperty, PointerProperty, BoolProperty, IntProperty
from ..hubs_component import HubsComponent
from ..types import Category, PanelType, NodeType


COMPRESSION_MODES = [
    ("none", "None", "Use original image file"),
    ("etc1s", "ETC1S", "ETC1S (~1 bit-per-pixel)"),
    ("uastc", "UASTC", "UASTC (~8 bits-per-pixel)")
]


class AvnScenePragma(HubsComponent):
    _definition = {
        'name': 'avn-scene-pragma',
        'display_name': 'AVN Scene Pragma',
        'category': Category.SCENE,
        'node_type': NodeType.SCENE,
        'panel_type': [PanelType.SCENE],
        'icon': 'MODIFIER_DATA',
        'version': (1, 0, 0)
    }

    scaleLightmap: BoolProperty(
        name="Scale Lightmaps",
        description="Scale the lightmaps in the scene to maximize dynamic range",
        default=True
    )

    padLightmap: BoolProperty(
        name="Pad Lightmaps",
        description="Fill in the transparent pixels around the texture islands in the lightmap",
        default=True
    )

    maxImageSizeEnvironment: IntProperty(
        name="Max Image Size (Environment)",
        description="Environment images larger than this will be downscaled",
        subtype="UNSIGNED",
        default=512,
        min=1,
        max=8192
    )

    maxImageSizeBackground: IntProperty(
        name="Max Image Size (Background)",
        description="Background images larger than this will be downscaled",
        subtype="UNSIGNED",
        default=4096,
        min=1,
        max=8192
    )

    maxImageSizeLightmap: IntProperty(
        name="Max Image Size (Lightmaps)",
        description="Lightmaps images larger than this will be downscaled",
        subtype="UNSIGNED",
        default=4096,
        min=1,
        max=8192
    )

    compressionModeLightmap: EnumProperty(
        name="Compression Mode (Lightmaps)",
        description="Compression mode to use for lightmap textures",
        items=COMPRESSION_MODES,
        default="uastc"
    )

    compressionModeBackground: EnumProperty(
        name="Compression Mode (Background)",
        description="Compression mode to use for background textures",
        items=COMPRESSION_MODES,
        default="uastc"
    )
