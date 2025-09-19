bl_info = {
    "name": "Move/Rotate Sound",
    "author": "Plasmuh987", #Microsoft Copilot Assisted
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when moving or rotating an object",
    "category": "System"
}

import bpy
import aud
import os
import time
import threading

sound_device = aud.Device()
last_move_time = 0
previous_locations = {}

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
    prefs = bpy.context.preferences.addons[__name__].preferences
    if os.path.exists(prefs.sound_move):
        try:
            sound = aud.Sound(prefs.sound_move)
            handle = sound_device.play(sound)
            handle.volume = prefs.volume_move
        except Exception as e:
            print(f"Error playing move sound: {e}")

def move_handler(scene):
    global last_move_time, previous_locations
    prefs = bpy.context.preferences.addons[__name__].preferences
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

classes = [MoveSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(move_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.remove(move_handler)

if __name__ == "__main__":
    register()
