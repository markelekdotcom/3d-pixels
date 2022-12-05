"""


 ______   __  __   __   __
/\  == \ /\ \/\ \ /\ "-.\ \
\ \  __< \ \ \_\ \\ \ \-.  \
 \ \_\ \_\\ \_____\\ \_\\"\_\
  \/_/ /_/ \/_____/ \/_/ \/_/
 ______  __   ______   ______   ______ 
/\  ___\/\ \ /\  == \ /\  ___\ /\__  _\
\ \  __\\ \ \\ \  __< \ \___  \\/_/\ \/
 \ \_\   \ \_\\ \_\ \_\\/\_____\  \ \_\
  \/_/    \/_/ \/_/ /_/ \/_____/   \/_/


"""
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022, Mark Elek, David Elek


import bpy
import contextlib
from bpy.props import EnumProperty, BoolProperty, FloatProperty, FloatVectorProperty
from bpy.types import Panel
from bpy.app.handlers import persistent

BASIC_INSTANCE_KW = "_BI"
EXTRA_INSTANCE_KW = "_EI"
EXTRA_GLASS_KW = "_EG"
EXTRA_PLANE_KW = "_EP"
FRAME_KW = "_FR"
FLOOR_KW = "_FL"


class BASE_PANEL:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Project Settings"


class VIEW3D_PT_viewport_optimization_settings(BASE_PANEL, Panel):
    bl_label = "Viewport Optimization"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        scene = context.scene
        layout = self.layout
        if scene.use_instances_only or scene.use_frustum_culling or scene.cycles.use_fast_gi:
            layout.label(text="", icon='MODIFIER_ON')
        else:
            layout.label(text="", icon='MODIFIER_OFF')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            # Frustum Culling settings box
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.label(text="Frustum Culling Settings:")
            row = box.row()
            row.prop(scene, 'use_frustum_culling',
                     text="Frustum Culling", toggle=True)
            row = box.row()
            row.prop_search(scene, "culling_camera",
                            bpy.data, "cameras", text="")
            row.enabled = scene.use_frustum_culling

            box = layout.box()
            row = box.row()
            row.label(text="Proxy Settings:")
            row = box.row()
            row.prop(scene, 'base_proxy_object', text="")
            row = box.row()
            row.prop(scene, 'use_base_proxy_object',
                     text="Use Base Proxy Object", toggle=True)
            row = box.row()
            row.prop(scene, 'extra_proxy_object', text="")
            row = box.row()
            row.prop(scene, 'use_extra_proxy_object',
                     text="Use Extra Proxy Object", toggle=True)
            row = box.row()

            box = layout.box()
            row = box.row()
            row.label(text="Other Settings:")
            row = box.row()
            row.prop(scene, 'use_instances_only',
                     text="Use Instances Only", toggle=True)
            row = box.row()
            row.prop(scene, 'realize_on_render',
                     text="Realize on Render", toggle=True)
            row = box.row()
            row.label(text="Preview Pixel Size:")
            row = box.row()
            row.prop(scene.render, 'preview_pixel_size', text="")
            row = box.row()
            row.prop(scene.cycles, 'use_fast_gi',
                     text="Fast Global Illumination", toggle=True)


class VIEW3D_PT_quick_settings(BASE_PANEL, Panel):
    bl_label = "Quick Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SOLO_ON')

    def draw(self, context):
        scene = context.scene
        gm_color_img_texture = bpy.data.node_groups["Plane Setup Nodes"].nodes["Image Texture"]
        gm_height_img_texture = bpy.data.node_groups["Instancing Nodes"].nodes["Image Texture"]
        gm_inst_object_info_node = bpy.data.node_groups["Instancing Nodes"].nodes["Object Info"]

        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(scene, 'detail_size', text="Base Scale XY", slider=True)
        row = box.row()
        row.prop(scene, 'render_detail_size',
                 text="Render Base Scale XY", slider=True)
        row = box.row()
        row.prop(scene, 'detail_height', text="Base Height", slider=True)
        row = box.row()
        row.label(text="Base Object Material:")
        row = box.row()
        row.prop(scene, 'base_material', text="", icon='MATERIAL')
        row = box.row()
        row.label(text="Height Texture:")
        row = box.row()
        row.template_ID(gm_height_img_texture.inputs['Image'],
                        "default_value", new="image.new", open="image.open")
        row = box.row()
        row.label(text="Color Texture:")
        row = box.row()
        if scene.shading_mode == 'VERTEX':
            if gm_color_img_texture is None or "Invisible" in scene.base_material.name:
                row.label(text="No Texture in Material:", icon='ERROR')
            else:
                row.template_ID(gm_color_img_texture.inputs['Image'],
                                "default_value", new="image.new", open="image.open")
        else:
            try:
                mat = scene.base_material
                img_texture = mat.node_tree.nodes.get("Image Texture")
                if img_texture is None:
                    row.label(text="No Texture in Material:", icon='ERROR')
                else:
                    row.template_ID(
                        img_texture, 'image', new="image.new", open="image.open")
                    row = box.row()
                    row.label(text="Projection:")
                    row = box.row()
                    row.prop(img_texture, 'projection', text="")
            except AttributeError:
                row.label(text="No Base Material!", icon='ERROR')
        row = box.row()
        row.label(text="Base Object:")
        row = box.row()
        row.prop(scene, 'active_base_object', text="")
        row = layout.row()
        row = box.row()
        row.label(text="Sampling Channel (Height):")
        row = box.row()
        row.prop(scene, 'sampling_mode', text="")
        row = box.row()


class VIEW3D_PT_grid_settings(BASE_PANEL, Panel):
    bl_label = "Grid Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='LIGHTPROBE_GRID')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene
            box = layout.box()
            row = box.row()
            row.prop(scene, 'gap_size', text="Gap Size", slider=True)
            row = box.row()
            row.prop(scene, 'sparse_grid_x', text="Sparse Grid X", slider=True)
            row = box.row()
            row.prop(scene, 'sparse_grid_y', text="Sparse Grid Y", slider=True)


class VIEW3D_PT_instance_objects(BASE_PANEL, Panel):
    bl_label = "Instance Objects"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='OBJECT_DATA')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()

            row.label(text="Base Object:")
            row = box.row()
            row.prop(scene, 'active_base_object', text="")

            box = layout.box()
            row = box.row()
            row.label(text="Extra Object:")
            row = box.row()
            row.prop(scene, 'active_extra_object', text="")
            row = layout.row()
            row.prop(scene, 'use_extra_object',
                     text="Use Extra Object", toggle=True)
            row = layout.row()

            row = box.row()
            row.prop(scene, 'extra_object_treshold',
                     text="Height Treshold", slider=True)
            row = box.row()
            row.label(text="Height Treshold Mode:")
            row = box.row()
            row.prop(scene, 'threshold_mode', text="")


class VIEW3D_PT_base_scale(BASE_PANEL, Panel):
    bl_label = "Base Scale"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ORIENTATION_VIEW')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            gm_height_img_texture = bpy.data.node_groups["Instancing Nodes"].nodes["Image Texture"]
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.prop(scene, 'detail_size', text="Base Scale XY", slider=True)
            row = box.row()
            row.prop(scene, 'render_detail_size',
                     text="Render Base Scale XY", slider=True)
            row = box.row()
            row.prop(scene, 'detail_height', text="Base Height", slider=True)
            row = box.row()
            row.prop(scene, 'detail_height_multiplier', text="Base Height Multiplier", slider=True)
            row = box.row()
            row.prop(scene, 'negative_size_x',
                     text="Subtract Scale X", slider=True)
            row = box.row()
            row.prop(scene, 'negative_size_y',
                     text="Subtract Scale Y", slider=True)
            row = box.row()
            row.label(text="Sampling Channel (Height):")
            row = box.row()
            row.prop(scene, 'sampling_mode', text="")
            row.enabled = not scene.keep_base_height
            row = box.row()
            row.label(text="Height Texture:")
            row = box.row()
            row.template_ID(gm_height_img_texture.inputs['Image'],
                            "default_value", new="image.new", open="image.open")
            row.enabled = not scene.keep_base_height
            row = box.row()
            row.prop(scene, 'keep_base_height',
                     toggle=True, text="Keep Base Height")


class VIEW3D_PT_base_rotation(BASE_PANEL, Panel):
    bl_label = "Base Rotation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ORIENTATION_GIMBAL')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.label(text="Look At Object:")
            row = box.row()
            row.prop(scene, 'look_at_object', text="")
            row = box.row()
            row.prop(scene, 'use_look_at_rotation',
                     text="Use Look At Rotation", toggle=True)

            box = layout.box()
            row = box.row()
            row.prop(scene, 'use_random_rotation',
                     text="Use Random Rotation", toggle=True)
            row.enabled = not scene.use_look_at_rotation
            row = box.row()
            row.prop(scene, 'snap_rotation',
                     text="90 Degree Increments", toggle=True)
            row.enabled = scene.use_random_rotation


class VIEW3D_PT_base_shading(BASE_PANEL, Panel):
    bl_label = "Base Shading"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SHADING_RENDERED')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            gm_color_img_texture = bpy.data.node_groups["Plane Setup Nodes"].nodes["Image Texture"]

            scene = context.scene
            layout = self.layout
            box = layout.box()
            row = box.row()
            row = box.row()
            row.label(text="Base Object Material:")
            row = box.row()
            row.prop(scene, 'base_material', text="", icon='MATERIAL')
            row = box.row()
            row.label(text="Shading Mode:")
            row = box.row()
            row.prop(scene, 'shading_mode', text="")
            row.enabled = not scene.use_instances_only
            row = box.row()
            row.prop(scene, 'bevel_size', text="Bevel Size:", slider=True)
            plane_settings = bpy.data.objects["Plane"].modifiers["Plane Setup"]
            if plane_settings:
                row = box.row()
                row.label(text="Color Texture:")
                row = box.row()
                if scene.shading_mode == 'VERTEX':
                    if gm_color_img_texture is None or "Invisible" in scene.base_material.name:
                        row.label(text="No Texture in Material:", icon='ERROR')
                    else:
                        row.template_ID(gm_color_img_texture.inputs['Image'],
                                        "default_value", new="image.new", open="image.open")
                else:
                    try:
                        mat = scene.base_material
                        shader_img_texture = mat.node_tree.nodes.get(
                            "Image Texture")
                        if shader_img_texture is None:
                            row.label(text="No Texture in Material!",
                                      icon='ERROR')
                        else:
                            row.template_ID(
                                shader_img_texture, 'image', new="image.new", open="image.open")
                            row = box.row()
                            row.label(text="Projection:")
                            row = box.row()
                            row.prop(shader_img_texture, 'projection', text="")
                            row = box.row()
                            row.prop(scene, 'use_pixelation',
                                     text="Use Pixelation", toggle=True)
                            row.enabled = scene.shading_mode == 'TEXTURED'
                            row = box.row()
                            row.prop(scene, 'pixelation',
                                     text="Pixelation:", slider=True)
                            row.enabled = scene.shading_mode == 'TEXTURED' and scene.use_pixelation
                    except AttributeError:
                        row.label(text="No Base Material!", icon='ERROR')


class VIEW3D_PT_environment(BASE_PANEL, Panel):
    bl_label = "Environment"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='WORLD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            scene = context.scene
            layout = self.layout
            box = layout.box()
            row = box.row()
            row.label(text="Background Mode:")
            row = box.row()
            row.prop(scene, 'background_mode', text="")
            row = box.row()
            if scene.background_mode == 'COLOR':
                row.label(text="Background Color:")
                row = box.row()
                row.prop(scene, 'background_color', text="")
            elif scene.background_mode == 'TEXTURE':
                row.label(text="Environment Texture:")
                row = box.row()
                environment_texture_node = bpy.data.worlds["World"].node_tree.nodes["Environment Texture"]
                row.template_ID(environment_texture_node, 'image',
                                new="image.new", open="image.open")

            row = box.row()
            row.label(text="HDRI Lighting:")
            row = box.row()
            hdri_texture_node = bpy.data.worlds["World"].node_tree.nodes["HDRI Lighting"]
            row.template_ID(hdri_texture_node, 'image',
                            new="image.new", open="image.open")


class VIEW3D_PT_extra_scale(BASE_PANEL, Panel):
    bl_label = "Extra Scale"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.prop(scene, 'keep_extra_scale',
                     text="Keep Extra Scale Z", toggle=True)
            row = box.row()
            row.label(text="Extra Scale Offset:")
            row = box.row()
            row.prop(scene, 'extra_scale_offset', text="")
            row.enabled = not scene.use_extra_random_scale
            row = box.row()
            row.label(text="Extra Random Scale Min:")
            row = box.row()
            row.prop(scene, 'extra_random_scale_min', text="", slider=True)
            row.enabled = scene.use_extra_random_scale
            row = box.row()
            row.label(text="Extra Random Scale Max:")
            row = box.row()
            row.prop(scene, 'extra_random_scale_max', text="", slider=True)
            row.enabled = scene.use_extra_random_scale
            row = box.row()
            row.prop(scene, 'use_extra_random_scale',
                     text="Use Extra Random Scale", toggle=True)
            row = box.row()
            row.prop(scene, 'offset_z', text="Offset Z", slider=True)


class VIEW3D_PT_extra_rotation(BASE_PANEL, Panel):
    bl_label = "Extra Rotation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.label(text="Extra Look At Object:")
            row = box.row()
            row.prop(scene, 'extra_look_at_object', text="")
            row = box.row()
            row.prop(scene, 'use_extra_look_at_rotation',
                     text="Use Extra Look At Rotation", toggle=True)

            box = layout.box()
            row = box.row()
            row.prop(scene, 'use_extra_random_rotation',
                     text="Use Extra Random Rotation", toggle=True)
            row.enabled = not scene.use_extra_look_at_rotation
            row = box.row()
            row.prop(scene, 'extra_snap_rotation',
                     text="Extra 90 Degree Increments", toggle=True)
            row.enabled = scene.use_extra_random_rotation


class VIEW3D_PT_extra_location(BASE_PANEL, Panel):
    bl_label = "Extra Location"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene

            box = layout.box()
            row = box.row()
            row.prop(scene, 'extra_location_offset_z',
                     text="Extra Location Offset Z", slider=True)


class VIEW3D_PT_extra_shading(BASE_PANEL, Panel):
    bl_label = "Extra Shading"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        row.label(text="Extra Shading Mode:")
        row = box.row()
        row.prop(scene, 'extra_shading_mode', text="")
        row = box.row()
        row.prop(scene, 'extra_bevel_size',
                 text="Extra Bevel Size:", slider=True)
        if settings:
            gm_extra_color_img_texture = bpy.data.node_groups[
                "Plane Setup Nodes"].nodes["Image Texture.001"]

            row = box.row()
            row.label(text="Extra Color Texture:")
            row = box.row()
            if scene.extra_shading_mode == 'VERTEX':
                row.template_ID(gm_extra_color_img_texture.inputs['Image'],
                                "default_value", new="image.new", open="image.open")
            else:
                try:
                    mat = scene.extra_material
                    extra_shader_img_texture = mat.node_tree.nodes["Image Texture"]
                    row.template_ID(
                        extra_shader_img_texture, 'image', new="image.new", open="image.open")
                    row = box.row()
                    row.label(text="Extra Projection:")
                    row = box.row()
                    row.prop(extra_shader_img_texture, 'projection', text="")
                    row = box.row()
                except AttributeError:
                    row.label(text="No Extra Material!", icon='ERROR')

        row = box.row()
        row.prop(scene, 'use_extra_pixelation',
                 text="Use Extra Pixelation", toggle=True)
        row.enabled = scene.extra_shading_mode == 'TEXTURED'
        row = box.row()
        row.prop(scene, 'extra_pixelation', text="Pixelation:", slider=True)
        row.enabled = scene.extra_shading_mode == 'TEXTURED' and scene.use_extra_pixelation
        row = box.row()
        row.label(text="Extra Object Material:")
        row = box.row()
        row.prop(scene, 'extra_material', text="", icon='MATERIAL')


class VIEW3D_PT_extra_glass(BASE_PANEL, Panel):
    bl_label = "Extra Glass"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        extra_glass_gm_mat_node = bpy.data.node_groups["Extra Glass Nodes"].nodes["Set Material"]
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row()
        if settings and extra_glass_gm_mat_node:
            row.label(text="Extra Glass Settings:")
            row = box.row()
            row.prop(scene, 'extra_glass_material', text="")
            row.enabled = scene.use_extra_glass
            row = box.row()
            row.label(text="Glass Color:")
            row = box.row()
            mat = scene.extra_glass_material
            glass_material_node = mat.node_tree.nodes.get("RGB")
            if glass_material_node:
                row.prop(scene, 'extra_glass_color', text="")
                row.enabled = scene.use_extra_glass

            else:
                row.label(text="No 'RGB' node in material!", icon='ERROR')
            row = box.row()
            row.prop(scene, 'extra_glass_width',
                     text="Extra Glass Width", slider=True)
            row.enabled = scene.use_extra_glass
            row = box.row()
            row.prop(scene, 'use_extra_glass',
                     text="Use Extra Glass", toggle=True)


class VIEW3D_PT_extra_plane(BASE_PANEL, Panel):
    bl_label = "Extra Plane"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='ADD')

    def draw(self, context):
        settings = bpy.data.objects["Plane"].modifiers["Settings"]
        if settings:
            layout = self.layout
            scene = context.scene
            box = layout.box()
            row = box.row()
            row.label(text="Extra Plane Settings:")
            row = box.row()
            row.prop(scene, 'extra_plane_material', text="")
            row.enabled = scene.use_extra_plane
            row = box.row()
            row.label(text="Extra Plane Color:")
            row = box.row()
            mat = scene.extra_plane_material
            plane_material_node = mat.node_tree.nodes.get("RGB")
            if plane_material_node:
                row.prop(scene, 'extra_plane_color', text="")
                row.enabled = scene.use_extra_plane
            else:
                row.label(text="No 'RGB' node in material!", icon='ERROR')
            row = box.row()
            row.prop(scene, 'use_extra_plane',
                     text="Use Extra Plane", toggle=True)


class VIEW3D_PT_boolean_settings(BASE_PANEL, Panel):
    bl_label = "Boolean Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SELECT_SUBTRACT')

    def draw(self, context):
        scene = context.scene
        boolean_modifier = bpy.data.objects["Plane"].modifiers["Boolean"]

        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Boolean Object:")
        row = box.row()
        row.prop(scene, 'active_boolean_object', text="")
        row = box.row()
        row.label(text="Boolean Operation:")
        row = box.row()
        row.prop(scene, 'boolean_operation', text="")
        row = box.row()
        row.label(text="Solver:")
        row = box.row()
        row.prop(boolean_modifier, 'solver', text="")
        row = box.row()
        row.prop(scene, 'use_boolean', text="Use Boolean Modifier", toggle=True)


class VIEW3D_PT_frame_settings(BASE_PANEL, Panel):
    bl_label = "Frame Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='SELECT_SET')

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Frame Object:")
        row = box.row()
        row.prop(scene, 'active_frame_object', text="")
        row = box.row()
        row.prop(scene, 'frame_scale_offset',
                 text="Frame Scale Offset", slider=True)
        row = box.row()
        row.label(text="Frame Material:")
        row = box.row()
        row.prop(scene, 'frame_material', text="", icon='MATERIAL')
        row.enabled = scene.active_frame_object is not None
        row = box.row()
        row.label(text="Frame Color:")
        row = box.row()
        mat = scene.frame_material
        frame_material_node = mat.node_tree.nodes.get("RGB")
        if frame_material_node:
            row.prop(scene, 'frame_color', text="")
            row.enabled = scene.active_frame_object is not None
        else:
            row.label(text="No 'RGB' node in material!", icon='ERROR')
        row = box.row()


class VIEW3D_PT_floor_settings(BASE_PANEL, Panel):
    bl_label = "Floor Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='MESH_PLANE')

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text="Floor Material:")
        row = box.row()
        row.prop(scene, 'floor_material', text="", icon='MATERIAL')
        row = box.row()
        row.label(text="Floor Color:")
        row = box.row()
        mat = scene.floor_material
        floor_material_node = mat.node_tree.nodes.get("RGB")
        if floor_material_node:
            row.prop(scene, 'floor_color', text="")
        else:
            row.label(text="No 'RGB' node in material!", icon='ERROR')
        row = box.row()


class VIEW3D_PT_about(BASE_PANEL, Panel):
    bl_label = "About"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='URL')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        # TODO check for updates

        row.operator(
            "wm.url_open", text="Documentation (URL)").url = "https://3d-pixels.readthedocs.io/en/latest/"


def sampling_mode_enum_set(self, context):
    scene = bpy.context.scene
    sampling_mode = scene.sampling_mode
    plane = bpy.data.objects["Plane"]
    settings = plane.modifiers["Settings"]

    if sampling_mode == 'ALL':
        settings["Input_8"] = 0
    elif sampling_mode == 'RED':
        settings["Input_8"] = 1
    elif sampling_mode == 'GREEN':
        settings["Input_8"] = 2
    else:
        settings["Input_8"] = 3

    plane.update_tag()


def shading_mode_enum_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    shading_mode = scene.shading_mode
    gm_color_img_texture = bpy.data.node_groups["Plane Setup Nodes"].nodes["Image Texture"]

    if shading_mode == 'VERTEX':
        plane_settings["Input_31"] = 0
        mat = scene.base_material
        texture_node = mat.node_tree.nodes["Image Texture"]
        gm_color_img_texture.inputs['Image'].default_value = texture_node.image

        plane.update_tag()

    elif shading_mode == 'TEXTURED':
        plane_settings["Input_31"] = 1
        with contextlib.suppress(Exception):
            # loop all materials
            materials = [
                mat for mat in bpy.data.materials
                if contains_keyword(BASIC_INSTANCE_KW, mat.name)
                and not contains_keyword(EXTRA_INSTANCE_KW, mat.name)]
            for mat in materials:
                texture_node = mat.node_tree.nodes["Image Texture"]
                texture_node.image = gm_color_img_texture.inputs['Image'].default_value

            plane.update_tag()


def extra_shading_mode_enum_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    shading_mode = scene.extra_shading_mode

    gm_color_img_texture = bpy.data.node_groups["Plane Setup Nodes"].nodes["Image Texture.001"]

    if shading_mode == 'VERTEX':
        plane_settings["Input_32"] = 0
        mat = scene.extra_material
        texture_node = mat.node_tree.nodes["Image Texture"]
        gm_color_img_texture.inputs['Image'].default_value = texture_node.image

        if scene.use_extra_object:
            plane.update_tag()

    elif shading_mode == 'TEXTURED':
        plane_settings["Input_32"] = 1
        with contextlib.suppress(Exception):
            # loop all materials
            materials = [
                mat for mat in bpy.data.materials
                if contains_keyword(EXTRA_INSTANCE_KW, mat.name)
                and not contains_keyword(BASIC_INSTANCE_KW, mat.name)]
            for mat in materials:
                texture_node = mat.node_tree.nodes["Image Texture"]
                texture_node.image = gm_color_img_texture.inputs['Image'].default_value

            if scene.use_extra_object:
                plane.update_tag()


def use_extra_glass_bool_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_4"] = 1 if scene.use_extra_glass else 0
    plane.update_tag()


def extra_glass_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    extra_glass_gm_mat_node = bpy.data.node_groups["Extra Glass Nodes"].nodes["Set Material"]
    extra_glass_gm_mat_node.inputs['Material'].default_value = scene.extra_glass_material

    mat = scene.extra_glass_material
    glass_material_node = mat.node_tree.nodes.get("RGB")
    scene.extra_glass_color = glass_material_node.outputs[0].default_value

    plane.update_tag()


def extra_glass_material_poll(self, material):
    return contains_keyword(EXTRA_GLASS_KW, material.name)


def extra_plane_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    extra_plane_gm_mat_node = extra_plane_gm_mat_node = bpy.data.node_groups[
        "Extra Glass Nodes"].nodes["Set Material.001"]
    extra_plane_gm_mat_node.inputs['Material'].default_value = scene.extra_plane_material

    mat = scene.extra_plane_material
    extra_plane_material_node = mat.node_tree.nodes.get("RGB")
    scene.extra_plane_color = extra_plane_material_node.outputs[0].default_value

    plane.update_tag()


def extra_plane_material_poll(self, material):
    return contains_keyword(EXTRA_PLANE_KW, material.name)


def use_extra_plane_bool_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_30"] = 1 if scene.use_extra_plane else 0
    plane.update_tag()


def pixelation_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_33"] = scene.pixelation
    plane.update_tag()


def extra_pixelation_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_34"] = scene.extra_pixelation
    if scene.use_extra_object:
        plane.update_tag()


def detail_size_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_2"] = scene.detail_size
    plane.update_tag()
    plane.modifiers["Settings"].update_tag()


def render_detail_size_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_40"] = scene.render_detail_size
    plane.update_tag()


def detail_height_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_3"] = scene.detail_height
    plane.update_tag()


def detail_height_multiplier_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_62"] = scene.detail_height_multiplier
    plane.update_tag()


def extra_glass_width_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_5"] = scene.extra_glass_width
    if scene.use_extra_glass:
        plane.update_tag()


def use_pixelation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_16"] = 1 if scene.use_pixelation else 0
    plane.update_tag()


def use_extra_pixelation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_25"] = 1 if scene.use_extra_pixelation else 0
    if scene.use_extra_object:
        plane.update_tag()


def extra_object_treshold_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_17"] = scene.extra_object_treshold
    if scene.use_extra_object:
        plane.update_tag()


def use_extra_object_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_18"] = 1 if scene.use_extra_object else 0
    plane.update_tag()


def gap_size_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_21"] = scene.gap_size
    plane.update_tag()


def negative_size_x_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_19"] = scene.negative_size_x
    plane.update_tag()


def negative_size_y_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_20"] = scene.negative_size_y
    plane.update_tag()


def keep_extra_scale_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_22"] = 1 if scene.keep_extra_scale else 0
    if scene.use_extra_object:
        plane.update_tag()


def offset_z_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_23"] = scene.offset_z
    if scene.use_extra_object:
        plane.update_tag()


def use_frustum_culling_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_26"] = 1 if scene.use_frustum_culling else 0
    plane.update_tag()


def culling_camera_set(self, context):
    scene = bpy.context.scene
    if scene.culling_camera is not None:
        gm_frustum_culling_node_group = bpy.data.node_groups[
            "Instancing Nodes"].nodes["FrustumCullingGroup"]
        plane = bpy.data.objects["Plane"]
        camera_object = bpy.data.objects[scene.culling_camera.name]
        gm_frustum_culling_node_group.inputs[0].default_value = camera_object
        plane.update_tag()


def use_instances_only_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_27"] = 1 if scene.use_instances_only else 0
    if scene.use_instances_only:
        # prevent the issue of texture change when turning on instance only mode
        gm_color_img_texture = bpy.data.node_groups["Plane Setup Nodes"].nodes["Image Texture"]
        mat = scene.base_material
        texture_node = mat.node_tree.nodes["Image Texture"]
        gm_color_img_texture.inputs['Image'].default_value = texture_node.image

        scene.shading_mode = "TEXTURED"
    plane.update_tag()


def sparse_grid_x_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_28"] = scene.sparse_grid_x
    plane.update_tag()


def sparse_grid_y_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_29"] = scene.sparse_grid_y
    plane.update_tag()


def boolean_operation_enum_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane.modifiers["Boolean"].solver = scene.boolean_operation
    plane.update_tag()


def use_boolean_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    boolean_modifier = plane.modifiers["Boolean"]
    boolean_modifier.show_viewport = scene.use_boolean
    boolean_modifier.show_render = scene.use_boolean
    plane.update_tag()


def base_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    gm_set_base_material_node = bpy.data.node_groups["Instancing Nodes"].nodes["Set Material"]
    gm_set_base_material_node.inputs[2].default_value = scene.base_material
    plane.update_tag()


def base_material_poll(self, material):
    return contains_keyword(BASIC_INSTANCE_KW, material.name) and not contains_keyword(EXTRA_INSTANCE_KW, material.name)


def extra_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    gm_set_extra_material_node = bpy.data.node_groups["Instancing Nodes"].nodes["Set Material.001"]
    gm_set_extra_material_node.inputs[2].default_value = scene.extra_material
    plane.update_tag()


def extra_material_poll(self, material):
    return contains_keyword(EXTRA_INSTANCE_KW, material.name) and not contains_keyword(BASIC_INSTANCE_KW, material.name)


def bevel_size_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_36"] = scene.bevel_size
    plane.update_tag()


def extra_bevel_size_float_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_37"] = scene.extra_bevel_size
    plane.update_tag()


def realize_on_render_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_38"] = 1 if scene.realize_on_render else 0
    plane.update_tag()


def active_frame_object_set(self, context):
    scene = bpy.context.scene
    frame_ob_gm_node = bpy.data.node_groups["Frame Nodes"].nodes["Object Info"].inputs[0]
    frame_ob_gm_node.default_value = scene.active_frame_object


def active_frame_object_poll(self, object):
    return contains_keyword(FRAME_KW, object.name)


def frame_scale_offset_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_39"] = scene.frame_scale_offset
    plane.update_tag()


def frame_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    frame_ob = scene.active_frame_object
    frame_ob.active_material = scene.frame_material

    mat = scene.frame_material
    frame_material_node = mat.node_tree.nodes.get("RGB")
    scene.frame_color = frame_material_node.outputs[0].default_value

    plane.update_tag()


def frame_material_poll(self, material):
    return contains_keyword(FRAME_KW, material.name)


def floor_material_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    floor_ob = bpy.data.objects["Floor"]
    floor_ob.active_material = scene.floor_material

    mat = scene.floor_material
    floor_material_node = mat.node_tree.nodes.get("RGB")
    scene.floor_color = floor_material_node.outputs[0].default_value

    plane.update_tag()


def floor_material_poll(self, material):
    return contains_keyword(FLOOR_KW, material.name)


def use_random_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_41"] = 1 if scene.use_random_rotation else 0
    plane.update_tag()


def snap_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_42"] = 1 if scene.snap_rotation else 0
    plane.update_tag()


def use_extra_random_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_43"] = 1 if scene.use_extra_random_rotation else 0
    plane.update_tag()


def extra_snap_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_44"] = 1 if scene.extra_snap_rotation else 0
    plane.update_tag()


def extra_scale_offset_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_45"] = scene.extra_scale_offset
    plane.update_tag()


def use_extra_random_scale_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_46"] = scene.use_extra_random_scale
    plane.update_tag()


def extra_random_scale_min_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_47"] = scene.extra_random_scale_min
    plane.update_tag()


def extra_random_scale_max_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_48"] = scene.extra_random_scale_max
    plane.update_tag()


def threshold_mode_enum_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_49"] = 1 if scene.threshold_mode == "GREATER" else 0
    plane.update_tag()


def active_base_object_set(self, context):
    scene = bpy.context.scene
    active_base_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["Object Info"].inputs[0]
    active_base_ob_gm_node.default_value = scene.active_base_object


def active_base_object_poll(self, object):
    return contains_keyword(BASIC_INSTANCE_KW, object.name)


def active_extra_object_set(self, context):
    scene = bpy.context.scene
    active_extra_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["Object Info.001"].inputs[0]
    active_extra_ob_gm_node.default_value = scene.active_extra_object


def active_extra_object_poll(self, object):
    return contains_keyword(EXTRA_INSTANCE_KW, object.name)


def active_boolean_object_set(self, context):
    scene = bpy.context.scene
    boolean_modifier = bpy.data.objects["Plane"].modifiers["Boolean"]
    boolean_modifier.object = scene.active_boolean_object


def active_boolean_object_poll(self, object):
    return "Boolean" in object.name


def extra_glass_color_set(self, context):
    scene = bpy.context.scene
    mat = scene.extra_glass_material
    glass_material_node = mat.node_tree.nodes.get("RGB")
    glass_material_node.outputs[0].default_value = scene.extra_glass_color

    if scene.use_extra_glass:
        plane = bpy.data.objects["Plane"]
        plane.update_tag()


def base_proxy_object_set(self, context):
    scene = bpy.context.scene
    proxy_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["Object Info.002"]
    proxy_ob_gm_node.inputs[0].default_value = scene.base_proxy_object


def extra_proxy_object_set(self, context):
    scene = bpy.context.scene
    extra_proxy_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["Object Info.003"]
    extra_proxy_ob_gm_node.inputs[0].default_value = scene.extra_proxy_object


def proxy_object_poll(self, object):
    return "Proxy" in object.name


def use_base_proxy_object_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_55"] = 1 if scene.use_base_proxy_object else 0
    plane.update_tag()


def use_extra_proxy_object_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_56"] = 1 if scene.use_extra_proxy_object else 0
    plane.update_tag()


def use_look_at_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_57"] = 1 if scene.use_look_at_rotation else 0
    plane.update_tag()


def look_at_object_set(self, context):
    scene = bpy.context.scene
    look_at_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["LookAtRotation"]
    look_at_ob_gm_node.inputs[0].default_value = scene.extra_proxy_object


""" def look_at_object_poll(self, object):
    return "Look_At" in object.name """


def extra_location_offset_z_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_58"] = scene.extra_location_offset_z
    plane.update_tag()


def use_extra_look_at_rotation_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_59"] = 1 if scene.use_extra_look_at_rotation else 0
    plane.update_tag()


def extra_look_at_object_set(self, context):
    scene = bpy.context.scene
    look_at_ob_gm_node = bpy.data.node_groups["Instancing Nodes"].nodes["ExtraLookAtRotation"]
    look_at_ob_gm_node.inputs[0].default_value = scene.extra_proxy_object


def keep_base_height_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_60"] = 1 if scene.keep_base_height else 0
    plane.update_tag()


def background_mode_set(self, context):
    scene = bpy.context.scene
    plane = bpy.data.objects["Plane"]
    plane_settings = plane.modifiers["Settings"]
    plane_settings["Input_61"] = 0 if scene.background_mode == 'COLOR' else 1
    plane.update_tag()


def background_color_set(self, context):
    scene = bpy.context.scene
    bg_color_node = bpy.data.worlds["World"].node_tree.nodes["Background Color"]
    bg_color_node.inputs[0].default_value = scene.background_color


def contains_keyword(keyword, string):
    return keyword.upper() in string.upper()


def extra_plane_color_set(self, context):
    scene = bpy.context.scene
    mat = scene.extra_plane_material
    plane_material_node = mat.node_tree.nodes.get("RGB")
    plane_material_node.outputs[0].default_value = scene.extra_plane_color

    if scene.use_extra_plane:
        plane = bpy.data.objects["Plane"]
        plane.update_tag()


def floor_color_set(self, context):
    scene = bpy.context.scene
    mat = scene.floor_material
    floor_material_node = mat.node_tree.nodes.get("RGB")
    floor_material_node.outputs[0].default_value = scene.floor_color

    plane = bpy.data.objects["Plane"]
    plane.update_tag()


def frame_color_set(self, context):
    scene = bpy.context.scene
    mat = scene.frame_material
    frame_material_node = mat.node_tree.nodes.get("RGB")
    frame_material_node.outputs[0].default_value = scene.frame_color

    if scene.active_frame_object is not None:
        plane = bpy.data.objects["Plane"]
        plane.update_tag()


classes = (VIEW3D_PT_viewport_optimization_settings, VIEW3D_PT_quick_settings,
           VIEW3D_PT_grid_settings, VIEW3D_PT_instance_objects,
           VIEW3D_PT_base_scale, VIEW3D_PT_base_rotation, VIEW3D_PT_base_shading,
           VIEW3D_PT_environment, VIEW3D_PT_extra_location, VIEW3D_PT_extra_scale,
           VIEW3D_PT_extra_rotation, VIEW3D_PT_extra_shading, VIEW3D_PT_extra_glass,
           VIEW3D_PT_extra_plane, VIEW3D_PT_boolean_settings, VIEW3D_PT_frame_settings,
           VIEW3D_PT_floor_settings, VIEW3D_PT_about,
           )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    sampling_mode_items = (('ALL', 'All Channels', ''),
                           ('RED', 'Red', ''),
                           ('GREEN', 'Green', ''),
                           ('BLUE', 'Blue', ''))

    bpy.types.Scene.sampling_mode = bpy.props.EnumProperty(
        name="sampling_mode",
        items=sampling_mode_items,
        default='ALL',
        description="Change Sampling Mode (All Channels, Red, Green, Blue)",
        update=sampling_mode_enum_set
    )
    
    bpy.app.handlers.frame_change_pre.append(sampling_mode_enum_set)

    shading_mode_items = (('VERTEX', 'Vertex Color', ''),
                          ('TEXTURED', 'Textured', ''),
                          )

    bpy.types.Scene.shading_mode = bpy.props.EnumProperty(
        name="shading_mode",
        items=shading_mode_items,
        default='VERTEX',
        description="Change Shading Mode (Vertex, Textured)",
        update=shading_mode_enum_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(shading_mode_enum_set)

    bpy.types.Scene.extra_shading_mode = bpy.props.EnumProperty(
        name="extra_shading_mode",
        items=shading_mode_items,
        default='VERTEX',
        description="Change Extra Shading Mode (Vertex, Textured)",
        update=extra_shading_mode_enum_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_shading_mode_enum_set)

    bpy.types.Scene.use_extra_glass = bpy.props.BoolProperty(
        name="use_extra_glass",
        default=False,
        description="Use Extra Glass",
        update=use_extra_glass_bool_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_glass_bool_set)

    bpy.types.Scene.pixelation = bpy.props.FloatProperty(
        name="pixelation",
        default=200.0,
        min=0.0,
        max=5000.0,
        soft_min=0.0,
        soft_max=1000.0,
        description="Change Pixelation Amount",
        update=pixelation_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(pixelation_float_set)

    bpy.types.Scene.extra_pixelation = bpy.props.FloatProperty(
        name="extra_pixelation",
        default=200.0,
        min=0.0,
        max=5000.0,
        soft_min=0.0,
        soft_max=1000.0,
        description="Change Extra Pixelation Amount",
        update=extra_pixelation_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_pixelation_float_set)

    bpy.types.Scene.detail_size = bpy.props.FloatProperty(
        name="detail_size",
        default=10.0,
        min=1.0,
        max=100.0,
        soft_min=1.0,
        soft_max=100.0,
        description="Detail Size",
        update=detail_size_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(detail_size_float_set)

    bpy.types.Scene.render_detail_size = bpy.props.FloatProperty(
        name="render_detail_size",
        default=4.0,
        min=1.0,
        max=100.0,
        soft_min=1.0,
        soft_max=100.0,
        description="Render Detail Size",
        update=render_detail_size_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(render_detail_size_float_set)

    bpy.types.Scene.detail_height = bpy.props.FloatProperty(
        name="detail_height",
        default=20,
        min=1.0,
        max=1000,
        soft_min=1.0,
        soft_max=100,
        description="Detail Height",
        update=detail_height_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(detail_height_float_set)

    bpy.types.Scene.detail_height_multiplier = bpy.props.FloatProperty(
        name="detail_height",
        default=1,
        min=1.0,
        max=1000,
        soft_min=1.0,
        soft_max=100,
        description="Detail Height Multiplier",
        update=detail_height_multiplier_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(detail_height_multiplier_float_set)

    bpy.types.Scene.extra_glass_width = bpy.props.FloatProperty(
        name="extra_glass_width",
        default=3,
        min=1.0,
        max=100,
        soft_min=1.0,
        soft_max=100,
        description="Extra Glass Width",
        update=extra_glass_width_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_glass_width_float_set)

    bpy.types.Scene.use_pixelation = bpy.props.BoolProperty(
        name="use_pixelation",
        default=True,
        description="Use Pixelation for Image Texture",
        update=use_pixelation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_pixelation_set)

    bpy.types.Scene.use_extra_pixelation = bpy.props.BoolProperty(
        name="use_extra_pixelation",
        default=True,
        description="Use Extra Pixelation for Image Texture",
        update=use_extra_pixelation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_pixelation_set)

    bpy.types.Scene.extra_object_treshold = bpy.props.FloatProperty(
        name="extra_object_treshold ",
        default=50.0,
        min=-0.0,
        max=100.0,
        description="Height Threshold to control extra object placement",
        update=extra_object_treshold_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_object_treshold_float_set)

    bpy.types.Scene.use_extra_object = bpy.props.BoolProperty(
        name="use_extra_object",
        default=True,
        description="Use extra object on top of base instances",
        update=use_extra_object_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_object_set)

    bpy.types.Scene.gap_size = bpy.props.FloatProperty(
        name="gap_size",
        default=1.0,
        min=0.0,
        max=100.0,
        description="Gap Size between instances",
        update=gap_size_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(gap_size_float_set)

    bpy.types.Scene.negative_size_x = bpy.props.FloatProperty(
        name="negative_size_x",
        default=0.0,
        min=0.0,
        max=100.0,
        description="Negative Size X",
        update=negative_size_x_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(negative_size_x_float_set)

    bpy.types.Scene.negative_size_y = bpy.props.FloatProperty(
        name="negative_size_y",
        default=0.0,
        min=0.0,
        max=100.0,
        description="Negative Size Y",
        update=negative_size_y_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(negative_size_y_float_set)

    bpy.types.Scene.keep_extra_scale = bpy.props.BoolProperty(
        name="keep_extra_scale",
        default=True,
        description="Keep the scale of extra objects",
        update=keep_extra_scale_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(keep_extra_scale_set)

    bpy.types.Scene.offset_z = bpy.props.FloatProperty(
        name="offset_z",
        default=0.0,
        min=-100.0,
        max=100.0,
        description="Extra Object Offset Z",
        update=offset_z_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(offset_z_float_set)

    bpy.types.Scene.use_frustum_culling = bpy.props.BoolProperty(
        name="use_frustum_culling",
        default=False,
        description=(
            "Use Frustum Culling in viewport to improve performance.\n"
            "(messes up vertex colors, useful while blocking in shapes)"
        ),
        update=use_frustum_culling_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_frustum_culling_set)

    bpy.types.Scene.culling_camera = bpy.props.PointerProperty(
        name="culling_camera",
        description="Camera to use for frustum culling",
        type=bpy.types.Camera,
        update=culling_camera_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(culling_camera_set)

    bpy.types.Scene.use_instances_only = bpy.props.BoolProperty(
        name="use_instances_only",
        default=True,
        description="Use instances instead of realizing geometry (vertex color and extra object won't work)",
        update=use_instances_only_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_instances_only_set)

    bpy.types.Scene.sparse_grid_x = bpy.props.FloatProperty(
        name="sparse_grid_x",
        default=0.0,
        min=0.0,
        max=100.0,
        description="Reduce the vertices of the grid/plane (X), used as points to instance on",
        update=sparse_grid_x_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(sparse_grid_x_float_set)

    bpy.types.Scene.sparse_grid_y = bpy.props.FloatProperty(
        name="sparse_grid_y",
        default=0.0,
        min=0.0,
        max=100.0,
        description="Reduce the vertices of the grid/plane (Y), used as points to instance on",
        update=sparse_grid_y_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(sparse_grid_y_float_set)

    bpy.types.Scene.use_extra_plane = bpy.props.BoolProperty(
        name="use_extra_plane",
        default=True,
        description="Use Extra Plane",
        update=use_extra_plane_bool_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_plane_bool_set)

    boolean_operation_items = (('DIFFERENCE', 'Difference', ''),
                               ('INTERSECT', 'Intersect', ''),
                               )

    bpy.types.Scene.boolean_operation = bpy.props.EnumProperty(
        name="boolean_operation",
        items=boolean_operation_items,
        default='DIFFERENCE',
        update=boolean_operation_enum_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(boolean_operation_enum_set)

    bpy.types.Scene.use_boolean = bpy.props.BoolProperty(
        name="use_boolean",
        default=True,
        description="Use Boolean Operation",
        update=use_boolean_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_boolean_set)

    bpy.types.Scene.base_material = bpy.props.PointerProperty(
        name="base_material",
        description="Base Material",
        type=bpy.types.Material,
        update=base_material_set,
        poll=base_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(base_material_set)

    bpy.types.Scene.extra_material = bpy.props.PointerProperty(
        name="extra_material",
        description="Extra Material",
        type=bpy.types.Material,
        update=extra_material_set,
        poll=extra_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_material_set)

    bpy.types.Scene.bevel_size = bpy.props.FloatProperty(
        name="bevel_size",
        default=5.0,
        min=0.0,
        max=100.0,
        soft_min=0.0,
        soft_max=100.0,
        description="Material based bevel size (Cycles Only)",
        update=bevel_size_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(bevel_size_float_set)

    bpy.types.Scene.extra_bevel_size = bpy.props.FloatProperty(
        name="extra_bevel_size",
        default=5.0,
        min=0.0,
        max=100.0,
        soft_min=0.0,
        soft_max=100.0,
        description="Material based bevel size for Extra Object (Cycles Only)",
        update=extra_bevel_size_float_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_bevel_size_float_set)

    bpy.types.Scene.realize_on_render = bpy.props.BoolProperty(
        name="realize_on_render",
        default=False,
        description="Realize instances when rendering",
        update=realize_on_render_set
    )
    bpy.app.handlers.frame_change_pre.append(realize_on_render_set)

    bpy.types.Scene.active_frame_object = bpy.props.PointerProperty(
        name="active_frame_object",
        description="Currently active frame object",
        type=bpy.types.Object,
        update=active_frame_object_set,
        poll=active_frame_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(active_frame_object_set)

    bpy.types.Scene.frame_scale_offset = bpy.props.FloatProperty(
        name="frame_scale_offset",
        default=1.0,
        min=1.0,
        max=100.0,
        soft_min=1.0,
        soft_max=100.0,
        description="Extra Glass scale XY offset",
        update=frame_scale_offset_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(frame_scale_offset_set)

    bpy.types.Scene.frame_material = bpy.props.PointerProperty(
        name="frame_material",
        description="Frame Material",
        type=bpy.types.Material,
        update=frame_material_set,
        poll=frame_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(frame_material_set)

    bpy.types.Scene.floor_material = bpy.props.PointerProperty(
        name="floor_material",
        description="Floor Material",
        type=bpy.types.Material,
        update=floor_material_set,
        poll=floor_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(floor_material_set)

    bpy.types.Scene.extra_glass_material = bpy.props.PointerProperty(
        name="extra_glass_material",
        description="Extra Glass Material",
        type=bpy.types.Material,
        update=extra_glass_material_set,
        poll=extra_glass_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_glass_material_set)

    bpy.types.Scene.extra_plane_material = bpy.props.PointerProperty(
        name="extra_plane_material",
        description="Extra Plane Material",
        type=bpy.types.Material,
        update=extra_plane_material_set,
        poll=extra_plane_material_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_plane_material_set)

    bpy.types.Scene.use_random_rotation = bpy.props.BoolProperty(
        name="use_random_rotation",
        default=False,
        description="Use Random Rotation",
        update=use_random_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_random_rotation_set)

    bpy.types.Scene.snap_rotation = bpy.props.BoolProperty(
        name="snap_rotation",
        default=False,
        description="Snap rotation to 90 degree increments",
        update=snap_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(snap_rotation_set)

    bpy.types.Scene.use_extra_random_rotation = bpy.props.BoolProperty(
        name="use_extra_random_rotation",
        default=False,
        description="Use Extra Random Rotation",
        update=use_extra_random_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_random_rotation_set)

    bpy.types.Scene.extra_snap_rotation = bpy.props.BoolProperty(
        name="extra_snap_rotation",
        default=False,
        description="Snap Extra Object's rotation to 90 degree increments",
        update=extra_snap_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_snap_rotation_set)

    bpy.types.Scene.extra_scale_offset = bpy.props.FloatVectorProperty(
        name="extra_scale_offset",
        subtype='XYZ',
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=100.0,
        description="Extra Object scale offset",
        update=extra_scale_offset_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_scale_offset_set)

    bpy.types.Scene.use_extra_random_scale = bpy.props.BoolProperty(
        name="use_extra_random_scale",
        default=False,
        description="Extra Object random scale",
        update=use_extra_random_scale_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_random_scale_set)

    bpy.types.Scene.extra_random_scale_min = bpy.props.FloatVectorProperty(
        name="extra_random_scale_min",
        subtype='XYZ',
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=100.0,
        description="Extra Object random scale min",
        update=extra_random_scale_min_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_random_scale_min_set)

    bpy.types.Scene.extra_random_scale_max = bpy.props.FloatVectorProperty(
        name="extra_random_scale_max",
        subtype='XYZ',
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=100.0,
        description="Extra Object random scale max",
        update=extra_random_scale_max_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_random_scale_max_set)

    threshold_items = (('GREATER', 'Greater Than', ''),
                       ('LESS', 'Less Than', ''),
                       )

    bpy.types.Scene.threshold_mode = bpy.props.EnumProperty(
        name="threshold_mode",
        items=threshold_items,
        default='GREATER',
        update=threshold_mode_enum_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(threshold_mode_enum_set)

    bpy.types.Scene.active_base_object = bpy.props.PointerProperty(
        name="active_base_object",
        description="Currently active base instance object",
        type=bpy.types.Object,
        update=active_base_object_set,
        poll=active_base_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(active_base_object_set)

    bpy.types.Scene.active_extra_object = bpy.props.PointerProperty(
        name="active_extra_object",
        description="Currently active extra instance object",
        type=bpy.types.Object,
        update=active_extra_object_set,
        poll=active_extra_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(active_extra_object_set)

    bpy.types.Scene.active_boolean_object = bpy.props.PointerProperty(
        name="active_boolean_object",
        description="Currently active boolean object",
        type=bpy.types.Object,
        update=active_boolean_object_set,
        poll=active_boolean_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(active_boolean_object_set)

    bpy.types.Scene.extra_glass_color = bpy.props.FloatVectorProperty(
        name="extra_glass_color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        description="Extra Glass Color",
        update=extra_glass_color_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_glass_color_set)

    bpy.types.Scene.base_proxy_object = bpy.props.PointerProperty(
        name="base_proxy_object",
        description="Proxy object for base instance",
        type=bpy.types.Object,
        update=base_proxy_object_set,
        poll=proxy_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(base_proxy_object_set)

    bpy.types.Scene.extra_proxy_object = bpy.props.PointerProperty(
        name="extra_proxy_object",
        description="Proxy object for extra instance",
        type=bpy.types.Object,
        update=extra_proxy_object_set,
        poll=proxy_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_proxy_object_set)

    bpy.types.Scene.use_base_proxy_object = bpy.props.BoolProperty(
        name="use_base_proxy_object",
        default=False,
        description="Use base proxy object",
        update=use_base_proxy_object_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_base_proxy_object_set)

    bpy.types.Scene.use_extra_proxy_object = bpy.props.BoolProperty(
        name="use_extra_proxy_object",
        default=False,
        description="Use extra proxy object",
        update=use_extra_proxy_object_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_proxy_object_set)

    bpy.types.Scene.use_look_at_rotation = bpy.props.BoolProperty(
        name="use_look_at_rotation",
        default=False,
        description="Use Look At Rotation",
        update=use_look_at_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_look_at_rotation_set)

    bpy.types.Scene.look_at_object = bpy.props.PointerProperty(
        name="look_at_object",
        description="Look At Object",
        type=bpy.types.Object,
        update=look_at_object_set,
        # poll=look_at_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(look_at_object_set)

    bpy.types.Scene.use_extra_look_at_rotation = bpy.props.BoolProperty(
        name="use_extra_look_at_rotation",
        default=False,
        description="Use Extra Look At Rotation",
        update=use_extra_look_at_rotation_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(use_extra_look_at_rotation_set)

    bpy.types.Scene.extra_look_at_object = bpy.props.PointerProperty(
        name="extra_look_at_object",
        description="Extra Look At Object",
        type=bpy.types.Object,
        update=extra_look_at_object_set,
        # poll=look_at_object_poll,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_look_at_object_set)

    bpy.types.Scene.extra_location_offset_z = bpy.props.FloatProperty(
        name="extra_location_offset_z",
        default=0.0,
        min=-1000.0,
        max=1000.0,
        soft_min=-100.0,
        soft_max=100.0,
        description="Extra Object Location Offset Z",
        update=extra_location_offset_z_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_location_offset_z_set)

    bpy.types.Scene.keep_base_height = bpy.props.BoolProperty(
        name="keep_base_height",
        default=False,
        description="Keep Base Height",
        update=keep_base_height_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(keep_base_height_set)

    background_mode_items = (('COLOR', 'Solid Color', ''),
                             ('TEXTURE', 'Environment Texture', ''),)

    bpy.types.Scene.background_mode = bpy.props.EnumProperty(
        name="background_mode",
        items=background_mode_items,
        default='COLOR',
        description="Mode to use for world background",
        update=background_mode_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(background_mode_set)

    bpy.types.Scene.background_color = bpy.props.FloatVectorProperty(
        name="background_color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 0.0, 1.0),
        description="Background Color",
        update=background_color_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(background_color_set)

    bpy.types.Scene.extra_plane_color = bpy.props.FloatVectorProperty(
        name="extra_plane_color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        description="Extra Plane Color",
        update=extra_plane_color_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(extra_plane_color_set)

    bpy.types.Scene.floor_color = bpy.props.FloatVectorProperty(
        name="floor_color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        description="Floor Color",
        update=floor_color_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(floor_color_set)

    bpy.types.Scene.frame_color = bpy.props.FloatVectorProperty(
        name="frame_color",
        subtype='COLOR_GAMMA',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        description="Frame Color",
        update=frame_color_set,
        options={'ANIMATABLE'}
    )
    bpy.app.handlers.frame_change_pre.append(frame_color_set)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sampling_mode
    del bpy.types.Scene.shading_mode
    del bpy.types.Scene.use_extra_glass
    del bpy.types.Scene.pixelation
    del bpy.types.Scene.detail_size
    del bpy.types.Scene.detail_height
    del bpy.types.Scene.detail_height_multiplier
    del bpy.types.Scene.extra_glass_width
    del bpy.types.Scene.use_pixelation
    del bpy.types.Scene.extra_object_treshold
    del bpy.types.Scene.use_extra_object
    del bpy.types.Scene.gap_size
    del bpy.types.Scene.negative_size_x
    del bpy.types.Scene.negative_size_y
    del bpy.types.Scene.keep_extra_scale
    del bpy.types.Scene.offset_z
    del bpy.types.Scene.extra_shading_mode
    del bpy.types.Scene.extra_pixelation
    del bpy.types.Scene.use_extra_pixelation
    del bpy.types.Scene.use_frustum_culling
    del bpy.types.Scene.culling_camera
    del bpy.types.Scene.use_instances_only
    del bpy.types.Scene.sparse_grid_x
    del bpy.types.Scene.sparse_grid_y
    del bpy.types.Scene.use_extra_plane
    del bpy.types.Scene.boolean_operation
    del bpy.types.Scene.use_boolean
    del bpy.types.Scene.base_material
    del bpy.types.Scene.extra_material
    del bpy.types.Scene.bevel_size
    del bpy.types.Scene.extra_bevel_size
    del bpy.types.Scene.realize_on_render
    del bpy.types.Scene.active_frame_object
    del bpy.types.Scene.frame_scale_offset
    del bpy.types.Scene.frame_material
    del bpy.types.Scene.floor_material
    del bpy.types.Scene.extra_glass_material
    del bpy.types.Scene.extra_plane_material
    del bpy.types.Scene.render_detail_size
    del bpy.types.Scene.use_random_rotation
    del bpy.types.Scene.snap_rotation
    del bpy.types.Scene.use_extra_random_rotation
    del bpy.types.Scene.extra_snap_rotation
    del bpy.types.Scene.extra_scale_offset
    del bpy.types.Scene.use_extra_random_scale
    del bpy.types.Scene.extra_random_scale_min
    del bpy.types.Scene.extra_random_scale_max
    del bpy.types.Scene.threshold_mode
    del bpy.types.Scene.active_base_object
    del bpy.types.Scene.active_extra_object
    del bpy.types.Scene.active_boolean_object
    del bpy.types.Scene.extra_glass_color
    del bpy.types.Scene.base_proxy_object
    del bpy.types.Scene.extra_proxy_object
    del bpy.types.Scene.use_look_at_rotation
    del bpy.types.Scene.look_at_object
    del bpy.types.Scene.use_extra_look_at_rotation
    del bpy.types.Scene.extra_look_at_object
    del bpy.types.Scene.extra_location_offset_z
    del bpy.types.Scene.keep_base_height
    del bpy.types.Scene.background_mode
    del bpy.types.Scene.background_color
    del bpy.types.Scene.extra_plane_color
    del bpy.types.Scene.floor_color
    del bpy.types.Scene.frame_color


if __name__ == "__main__":
    register()
