
bl_info = {
    "name": "Undo/Redo Sound",
    "author": "Plasmuh987", #Microsoft Copilot Assisted
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when undoing or redoing an action with customizable keybindings",
    "category": "System"
}

import bpy
import aud
import os

sound_device = aud.Device()
keymaps = []

class UndoRedoSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    sound_undo: bpy.props.StringProperty(name="Undo Sound", subtype='FILE_PATH')
    volume_undo: bpy.props.FloatProperty(name="Undo Volume", min=0.0, max=2.0, default=1.0)
    key_undo: bpy.props.EnumProperty(name="Undo Key", items=[(k, k, "") for k in ['Z','U','Y','X']])
    ctrl_undo: bpy.props.BoolProperty(name="Ctrl", default=True)
    shift_undo: bpy.props.BoolProperty(name="Shift", default=False)
    alt_undo: bpy.props.BoolProperty(name="Alt", default=False)

    sound_redo: bpy.props.StringProperty(name="Redo Sound", subtype='FILE_PATH')
    volume_redo: bpy.props.FloatProperty(name="Redo Volume", min=0.0, max=2.0, default=1.0)
    key_redo: bpy.props.EnumProperty(name="Redo Key", items=[(k, k, "") for k in ['Z','U','Y','X']])
    ctrl_redo: bpy.props.BoolProperty(name="Ctrl", default=True)
    shift_redo: bpy.props.BoolProperty(name="Shift", default=True)
    alt_redo: bpy.props.BoolProperty(name="Alt", default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Undo Sound Settings")
        layout.prop(self, "sound_undo")
        layout.prop(self, "volume_undo")
        layout.prop(self, "key_undo")
        layout.prop(self, "ctrl_undo")
        layout.prop(self, "shift_undo")
        layout.prop(self, "alt_undo")
        layout.label(text="Redo Sound Settings")
        layout.prop(self, "sound_redo")
        layout.prop(self, "volume_redo")
        layout.prop(self, "key_redo")
        layout.prop(self, "ctrl_redo")
        layout.prop(self, "shift_redo")
        layout.prop(self, "alt_redo")

class PlayUndoSoundOperator(bpy.types.Operator):
    bl_idname = "wm.play_undo_sound"
    bl_label = "Play Undo Sound"

    def execute(self, context):
        if bpy.ops.ed.undo.poll():
            bpy.ops.ed.undo()
            prefs = context.preferences.addons[__name__].preferences
            if os.path.exists(prefs.sound_undo):
                try:
                    sound = aud.Sound(prefs.sound_undo)
                    handle = sound_device.play(sound)
                    handle.volume = prefs.volume_undo
                except Exception as e:
                    self.report({'WARNING'}, f"Undo sound error: {e}")
        else:
            self.report({'WARNING'}, "Undo operation not available in current context.")
        return {'FINISHED'}

class PlayRedoSoundOperator(bpy.types.Operator):
    bl_idname = "wm.play_redo_sound"
    bl_label = "Play Redo Sound"

    def execute(self, context):
        if bpy.ops.ed.redo.poll():
            bpy.ops.ed.redo()
            prefs = context.preferences.addons[__name__].preferences
            if os.path.exists(prefs.sound_redo):
                try:
                    sound = aud.Sound(prefs.sound_redo)
                    handle = sound_device.play(sound)
                    handle.volume = prefs.volume_redo
                except Exception as e:
                    self.report({'WARNING'}, f"Redo sound error: {e}")
        else:
            self.report({'WARNING'}, "Redo operation not available in current context.")
        return {'FINISHED'}

classes = [UndoRedoSoundPreferences, PlayUndoSoundOperator, PlayRedoSoundOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = bpy.context.preferences.addons.get(__name__)
    if prefs:
        prefs = prefs.preferences
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = kc.keymaps.new(name='Window', space_type='EMPTY')
            kmi_undo = km.keymap_items.new("wm.play_undo_sound", type=prefs.key_undo, value='PRESS', ctrl=prefs.ctrl_undo, shift=prefs.shift_undo, alt=prefs.alt_undo)
            kmi_redo = km.keymap_items.new("wm.play_redo_sound", type=prefs.key_redo, value='PRESS', ctrl=prefs.ctrl_redo, shift=prefs.shift_redo, alt=prefs.alt_redo)
            keymaps.append(km)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km in keymaps:
            kc.keymaps.remove(km)
        keymaps.clear()

if __name__ == "__main__":
    register()
