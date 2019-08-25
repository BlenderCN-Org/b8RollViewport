bl_info = {
	"name": "Roll Viewport",
	"description": "Adds a roll function like in Krita's or Gimp's 2D viewports.",
	"location": "View 3D, ctrl-alt + MMB/LMB/RMB",
	"author": "Jace Priester, Martin Capitanio",
	"wiki_url": "https://github.com/capnm/b8RollViewport/",
	"category": "3D View",
	"blender": (2, 80, 0),
	"version": (1, 0, 1),
}

import bpy
from bpy.types import (Operator)
from mathutils import *
from math import *


class RollViewport(Operator):
	bl_idname = "view3d.roll_viewport"
	bl_label = "Roll Viewport"
	bl_options = {'GRAB_CURSOR'}

	initial_angle = 0
	angle_now = 0
	initial_rotation = Vector((0, 0, 0))
	camNormal = Vector((0, 0, -1))

	def invoke(self, context, event):
		rv3d = context.space_data.region_3d
		context.window_manager.modal_handler_add(self)

		if rv3d.view_perspective == 'CAMERA':
			rv3d.view_perspective = 'PERSP'

		self.view3d_bounds = Vector((context.region.width, context.region.height))
		self.view3d_center = self.view3d_bounds / 2

		mpos = Vector((event.mouse_region_x, event.mouse_region_y))
		mpos_centered = mpos - self.view3d_center

		self.initial_rotation = rv3d.view_rotation.copy()
		self.initial_angle = atan2(mpos_centered.y, mpos_centered.x)
		self.angle_now = self.initial_angle
		return {'RUNNING_MODAL'}

	def execute(self, context):
		rv3d = context.space_data.region_3d
		angle_diff = self.angle_now - self.initial_angle
		q = Quaternion(self.camNormal, angle_diff)
		rv3d.view_rotation = self.initial_rotation @ q
		return {'FINISHED'}

	def modal(self, context, event):
		rv3d = context.space_data.region_3d
		if event.type == 'MOUSEMOVE':
			mpos = Vector((event.mouse_region_x, event.mouse_region_y))
			mpos_centered = mpos - self.view3d_center
			self.angle_now = atan2(mpos_centered.y, mpos_centered.x)
			self.execute(context)
		elif event.type in {'MIDDLEMOUSE'}:
			return {'FINISHED'}
		elif event.type in {'ESC', 'RIGHTMOUSE'}:
			rv3d.view_rotation = self.initial_rotation
			return {'CANCELLED'}
		return {'RUNNING_MODAL'}


addon_keymaps = []


# TODO shouldn't be hardcoded
def register():
	bpy.utils.register_class(RollViewport)

	wm = bpy.context.window_manager
	kc = wm.keyconfigs.addon
	if kc:
		km = wm.keyconfigs.addon.keymaps.new('3D View', space_type='VIEW_3D')
		kmi = km.keymap_items.new(
			"view3d.roll_viewport", 'MIDDLEMOUSE', 'PRESS', alt=True, ctrl=True
		)
		# TODO use LMB to reset the z-axis ?
		kmi = km.keymap_items.new(
			"view3d.roll_viewport", 'LEFTMOUSE', 'PRESS', alt=True, ctrl=True
		)
		addon_keymaps.append((km, kmi))


def unregister():
	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	bpy.utils.unregister_class(RollViewport)


if __name__ == "__main__":
	register()
