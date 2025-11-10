import bpy
from bpy.types import Node, Menu


class MozLightmapNode(Node):
    """MOZ_lightmap settings node"""
    bl_idname = 'moz_lightmap.node'
    bl_label = 'MOZ_lightmap settings'
    bl_icon = 'LIGHT'
    bl_width_min = 216.3
    bl_width_max = 330.0

    intensity: bpy.props.FloatProperty(
        name="Intensity", soft_min=0, soft_max=1, default=1)

    def init(self, context):
        lightmap = self.inputs.new('NodeSocketColor', "Lightmap")
        lightmap.hide_value = True

        self.width = 216.3

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ShaderNodeTree'

    def draw_buttons(self, context, layout):
        layout.prop(self, "intensity")

    def draw_label(self):
        return "MOZ_lightmap"


class NODE_MT_category_hubs(Menu):
    bl_idname = "NODE_MT_category_hubs"
    bl_label = "Hubs"

    def draw(self, context):
        layout = self.layout
        layout.operator("node.add_node", text="MOZ_lightmap").type = 'moz_lightmap.node'

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'space_data') and
                context.space_data.tree_type == 'ShaderNodeTree')


def draw_hubs_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("NODE_MT_category_hubs")


def register():
    bpy.utils.register_class(MozLightmapNode)
    bpy.utils.register_class(NODE_MT_category_hubs)
    bpy.types.NODE_MT_shader_node_add_all.append(draw_hubs_menu)


def unregister():
    bpy.types.NODE_MT_shader_node_add_all.remove(draw_hubs_menu)
    bpy.utils.unregister_class(NODE_MT_category_hubs)
    bpy.utils.unregister_class(MozLightmapNode)
