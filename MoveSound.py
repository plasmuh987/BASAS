bl_info = {
    "name": "Move/Rotate Sound",
    "author": "Plasmuh987",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when moving, rotating, stretching an object",
    "category": "System"
}

import bpy
import aud
import os
import time
from bpy.app.handlers import persistent

sound_device = aud.Device()
last_move_time = 0
previous_locations = {}
move_sound_handle = None

class MoveSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    sound_move: bpy.props.StringProperty(name="Move Sound", subtype='FILE_PATH')
    volume_move: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=0.8)
    cooldown_move: bpy.props.FloatProperty(name="Cooldown (s)", min=0.0, max=2.0, default=0.5)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_move")
        layout.prop(self, "volume_move")
        layout.prop(self, "cooldown_move")

def play_move_sound():
    global move_sound_handle
    addon = bpy.context.preferences.addons.get(__name__)
    if not addon:
        return
    prefs = addon.preferences
    if prefs.sound_move and os.path.exists(prefs.sound_move):
        try:
            if move_sound_handle and move_sound_handle.status:
                print("Stopping previous move sound.")
                move_sound_handle.stop()
            print(f"MoveSound: Playing sound: {prefs.sound_move}")
            sound = aud.Sound(prefs.sound_move)
            move_sound_handle = sound_device.play(sound)
            move_sound_handle.volume = prefs.volume_move
        except Exception as e:
            print(f"MoveSound: Error playing move sound: {e}")

@persistent
def move_handler(scene):
    global previous_locations, last_move_time
    addon = bpy.context.preferences.addons.get(__name__)
    if not addon:
        return
    prefs = addon.preferences
    current_time = time.time()

    for obj in bpy.context.selected_objects:
        if obj.name not in previous_locations:
            previous_locations[obj.name] = obj.matrix_world.copy()
            continue

        prev_loc = previous_locations[obj.name]
        curr_loc = obj.matrix_world

        if curr_loc != prev_loc:
            if current_time - last_move_time >= prefs.cooldown_move:
                play_move_sound()
                last_move_time = current_time

        previous_locations[obj.name] = curr_loc.copy()

@persistent
def init_move_handler(dummy):
    global previous_locations
    previous_locations = {obj.name: obj.matrix_world.copy() for obj in bpy.context.scene.objects}
    if move_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(move_handler)
    print("MoveSound: Handlers reinitialized after load.")

classes = [MoveSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(move_handler)
    bpy.app.handlers.load_post.append(init_move_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if move_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(move_handler)
    if init_move_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_move_handler)