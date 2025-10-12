bl_info = {
    "name": "Selection Sound",
    "author": "Plasmuh987",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when selecting an object",
    "category": "System"
}

import bpy
import aud
import os
from bpy.app.handlers import persistent

sound_device = aud.Device()
last_selected = set()
selection_sound_handle = None

class SelectionSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    sound_select: bpy.props.StringProperty(name="Select Sound", subtype='FILE_PATH')
    volume_select: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_select")
        layout.prop(self, "volume_select")

def play_selection_sound():
    global selection_sound_handle
    addon = bpy.context.preferences.addons.get(__name__)
    if not addon:
        return
    prefs = addon.preferences
    if prefs.sound_select and os.path.exists(prefs.sound_select):
        try:
            if selection_sound_handle and selection_sound_handle.status:
                print("Stopping previous selection sound.")
                selection_sound_handle.stop()
            print(f"SelectionSound: Playing sound: {prefs.sound_select}")
            sound = aud.Sound(prefs.sound_select)
            selection_sound_handle = sound_device.play(sound)
            selection_sound_handle.volume = prefs.volume_select
        except Exception as e:
            print(f"SelectionSound: Error playing selection sound: {e}")

@persistent
def selection_handler(scene):
    global last_selected
    current_selected = set(obj.name for obj in bpy.context.selected_objects)
    if current_selected != last_selected and current_selected:
        print(f"SelectionSound: New selection: {current_selected}")
        play_selection_sound()
    last_selected = current_selected

@persistent
def init_selection_handler(dummy):
    global last_selected
    last_selected = set(obj.name for obj in bpy.context.selected_objects)
    if selection_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(selection_handler)
    print("SelectionSound: Handlers reinitialized after load.")

classes = [SelectionSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(selection_handler)
    bpy.app.handlers.load_post.append(init_selection_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if selection_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(selection_handler)
    if init_selection_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_selection_handler)