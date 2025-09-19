bl_info = {
    "name": "Selection Sound",
    "author": "Plasmuh987", #Microsoft Copilot Assisted
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when selecting an object",
    "category": "System"
}

import bpy
import aud
import os

sound_device = aud.Device()
last_selected = set()

class SelectionSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    sound_select: bpy.props.StringProperty(name="Select Sound", subtype='FILE_PATH')
    volume_select: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_select")
        layout.prop(self, "volume_select")

def play_selection_sound():
    prefs = bpy.context.preferences.addons[__name__].preferences
    if os.path.exists(prefs.sound_select):
        try:
            sound = aud.Sound(prefs.sound_select)
            handle = sound_device.play(sound)
            handle.volume = prefs.volume_select
        except Exception as e:
            print(f"Error playing selection sound: {e}")

def selection_handler(scene):
    global last_selected
    current_selected = set(obj.name for obj in bpy.context.selected_objects)

    # Play sound only if new selection occurred
    if current_selected != last_selected and current_selected:
        play_selection_sound()

    last_selected = current_selected

classes = [SelectionSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(selection_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.remove(selection_handler)

if __name__ == "__main__":
    register()
