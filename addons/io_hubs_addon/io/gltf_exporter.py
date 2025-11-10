import bpy
from bpy.props import PointerProperty
from ..components.components_registry import get_components_registry
from ..components.utils import get_host_components
import traceback

hubs_config = {
    "gltfExtensionName": "MOZ_hubs_components",
    "gltfExtensionVersion": 4,
}


def get_version_string():
    from .. import (bl_info)
    return str(bl_info['version'][0]) + '.' + str(bl_info['version'][1]) + '.' + str(bl_info['version'][2])


def export_callback(callback_method, export_settings):
    # Note: we loop through copied lists of the potential component hosts
    # to allow the callbacks to change the host names.  This is needed
    # because a name change will cause Blender to update the host lists in
    # mid iteration and so multiple callbacks could be executed for the same
    # component/host.

    for scene in bpy.data.scenes[:]:
        for component in get_host_components(scene):
            component_callback = getattr(component, callback_method)
            try:
                component_callback(export_settings, scene)
            except Exception:
                traceback.print_exc()

    for ob in bpy.data.objects[:]:
        for component in get_host_components(ob):
            component_callback = getattr(component, callback_method)
            try:
                component_callback(export_settings, ob, ob)
            except Exception:
                traceback.print_exc()

        if ob.type == 'ARMATURE':
            for bone in ob.data.bones[:]:
                for component in get_host_components(bone):
                    component_callback = getattr(component, callback_method)
                    try:
                        component_callback(export_settings, bone, ob)
                    except Exception:
                        traceback.print_exc()

    for material in bpy.data.materials[:]:
        for component in get_host_components(material):
            component_callback = getattr(component, callback_method)
            try:
                component_callback(export_settings, material)
            except Exception:
                traceback.print_exc()


def glTF2_pre_export_callback(export_settings):
    from io_scene_gltf2.blender.com.gltf2_blender_extras import BLACK_LIST
    BLACK_LIST.extend(glTF2ExportUserExtension.EXCLUDED_PROPERTIES)
    export_callback("pre_export", export_settings)


def glTF2_post_export_callback(export_settings):
    export_callback("post_export", export_settings)

    from io_scene_gltf2.blender.com.gltf2_blender_extras import BLACK_LIST
    for excluded_prop in glTF2ExportUserExtension.EXCLUDED_PROPERTIES:
        if excluded_prop in BLACK_LIST:
            BLACK_LIST.remove(excluded_prop)


# This class name is specifically looked for by gltf-blender-io and it's hooks are automatically invoked on export


class glTF2ExportUserExtension:

    EXCLUDED_PROPERTIES = []

    @classmethod
    def add_excluded_property(cls, key):
        if key not in glTF2ExportUserExtension.EXCLUDED_PROPERTIES:
            glTF2ExportUserExtension.EXCLUDED_PROPERTIES.append(key)

    @classmethod
    def remove_excluded_property(cls, key):
        if key in glTF2ExportUserExtension.EXCLUDED_PROPERTIES:
            glTF2ExportUserExtension.EXCLUDED_PROPERTIES.remove(key)

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension

        self.Extension = Extension
        self.properties = bpy.context.scene.HubsComponentsExtensionProperties
        self.was_used = False
        self.delayed_gathers = []

    def hubs_gather_gltf_hook(self, gltf2_object, export_settings):
        if not self.properties.enabled or not self.was_used:
            return

        extension_name = hubs_config["gltfExtensionName"]
        gltf2_object.extensions[extension_name] = self.Extension(
            name=extension_name,
            extension={
                "version": hubs_config["gltfExtensionVersion"],
                "exporterVersion": get_version_string()
            },
            required=False
        )

        if gltf2_object.asset.extras is None:
            gltf2_object.asset.extras = {}
        gltf2_object.asset.extras["HUBS_blenderExporterVersion"] = get_version_string(
        )

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):
        self.hubs_gather_gltf_hook(gltf2_plan, export_settings)

    def gather_scene_hook(self, gltf2_object, blender_scene, export_settings):
        if not self.properties.enabled:
            return

        self.add_hubs_components(gltf2_object, blender_scene, export_settings)
        self.call_delayed_gathers()

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if not self.properties.enabled:
            return

        self.add_hubs_components(gltf2_object, blender_object, export_settings)

    def gather_material_hook(self, gltf2_object, blender_material, export_settings):
        if not self.properties.enabled:
            return

        self.add_hubs_components(
            gltf2_object, blender_material, export_settings)

        from .utils import gather_lightmap_texture_info
        if blender_material.node_tree and blender_material.use_nodes:
            lightmap_texture_info = gather_lightmap_texture_info(
                blender_material, export_settings)
            if lightmap_texture_info:
                gltf2_object.extensions["MOZ_lightmap"] = self.Extension(
                    name="MOZ_lightmap",
                    extension=lightmap_texture_info,
                    required=False,
                )

    def gather_material_unlit_hook(self, gltf2_object, blender_material, export_settings):
        self.gather_material_hook(
            gltf2_object, blender_material, export_settings)

    def gather_joint_hook(self, gltf2_object, blender_pose_bone, export_settings):
        if not self.properties.enabled:
            return
        self.add_hubs_components(
            gltf2_object, blender_pose_bone.bone, export_settings)

    def call_delayed_gathers(self):
        for delayed_gather in self.delayed_gathers:
            component_data, component_name, gather = delayed_gather
            component_data[component_name] = gather()
        self.delayed_gathers.clear()

    def add_hubs_components(self, gltf2_object, blender_object, export_settings):
        component_list = blender_object.hubs_component_list

        registered_hubs_components = get_components_registry()

        if component_list.items:
            extension_name = hubs_config["gltfExtensionName"]
            component_data = {}

            for component_item in component_list.items:
                component_name = component_item.name
                if component_name in registered_hubs_components:
                    component_class = registered_hubs_components[component_name]
                    component = getattr(
                        blender_object, component_class.get_id())
                    data = component.gather(export_settings, blender_object)
                    if hasattr(data, "delayed_gather"):
                        self.delayed_gathers.append(
                            (component_data, component_class.gather_name(), data))
                    else:
                        component_data[component_class.gather_name()] = data
                else:
                    print('Could not export unsupported component "%s"' %
                          (component_name))

            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}
            gltf2_object.extensions[extension_name] = self.Extension(
                name=extension_name,
                extension=component_data,
                required=False
            )

            self.was_used = True


class HubsComponentsExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Export Hubs Components",
        description='Include this extension in the exported glTF file',
        default=True
    )


# Blender 4.x uses a new layout panel system instead of Panel classes
def draw_hubs_exporter_panel(context, layout, operator):
    """Draw function for Hubs exporter panel in Blender 4.x+"""
    props = context.scene.HubsComponentsExtensionProperties

    # Use the new layout.panel() method for Blender 4.x
    header, body = layout.panel("hubs_components", default_closed=False)
    header.use_property_split = False
    header.prop(props, 'enabled', text="Hubs Components")

    if body:
        body.use_property_split = True
        body.use_property_decorate = False
        body.active = props.enabled
        box = body.box()
        box.label(text="No options yet")


# called by gltf-blender-io after it has loaded
def register_export_panel():
    """Register the export panel using the appropriate method for the Blender version"""
    if bpy.app.version >= (4, 0, 0):
        # Blender 4.x: Use the new layout panel system
        try:
            import io_scene_gltf2
            io_scene_gltf2.exporter_extension_layout_draw['Hubs Components'] = draw_hubs_exporter_panel
        except Exception as e:
            print(f"Warning: Could not register Hubs export panel for Blender 4.x: {e}")
    else:
        # Blender 3.x: Use the old Panel class system
        class HubsGLTFExportPanel(bpy.types.Panel):
            bl_idname = "HBA_PT_Export_Panel"
            bl_label = "Hubs Export Panel"
            bl_space_type = 'FILE_BROWSER'
            bl_region_type = 'TOOL_PROPS'
            bl_label = "Hubs Components"
            bl_parent_id = "GLTF_PT_export_user_extensions"
            bl_options = {'DEFAULT_CLOSED'}

            @classmethod
            def poll(cls, context):
                sfile = context.space_data
                operator = sfile.active_operator
                return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

            def draw_header(self, context):
                props = bpy.context.scene.HubsComponentsExtensionProperties
                self.layout.prop(props, 'enabled', text="")

            def draw(self, context):
                layout = self.layout
                layout.use_property_split = True
                layout.use_property_decorate = False  # No animation.

                props = bpy.context.scene.HubsComponentsExtensionProperties
                layout.active = props.enabled

                box = layout.box()
                box.label(text="No options yet")

        try:
            bpy.utils.register_class(HubsGLTFExportPanel)
        except Exception:
            pass

    return unregister_export_panel


def unregister_export_panel():
    """Unregister the export panel using the appropriate method for the Blender version"""
    if bpy.app.version >= (4, 0, 0):
        # Blender 4.x: Remove from the layout draw dictionary
        try:
            import io_scene_gltf2
            if 'Hubs Components' in io_scene_gltf2.exporter_extension_layout_draw:
                io_scene_gltf2.exporter_extension_layout_draw.pop('Hubs Components')
        except Exception as e:
            print(f"Warning: Could not unregister Hubs export panel for Blender 4.x: {e}")
    else:
        # Blender 3.x: Unregister the Panel class
        try:
            # Need to get the class from the registry since it was defined in register_export_panel
            panel_class = getattr(bpy.types, "HBA_PT_Export_Panel", None)
            if panel_class:
                bpy.utils.unregister_class(panel_class)
        except Exception:
            pass


def register():
    print("Register GLTF Exporter")
    register_export_panel()
    bpy.utils.register_class(HubsComponentsExtensionProperties)
    bpy.types.Scene.HubsComponentsExtensionProperties = PointerProperty(
        type=HubsComponentsExtensionProperties)
    glTF2ExportUserExtension.add_excluded_property("HubsComponentsExtensionProperties")


def unregister():
    print("Unregister GLTF Exporter")
    unregister_export_panel()
    del bpy.types.Scene.HubsComponentsExtensionProperties
    bpy.utils.unregister_class(HubsComponentsExtensionProperties)
    glTF2ExportUserExtension.remove_excluded_property("HubsComponentsExtensionProperties")
