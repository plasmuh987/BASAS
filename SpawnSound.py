bl_info = {
    "name": "Object Add Sound",
    "author": "Plasmuh987", #Microsoft Copilot Assisted
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when an object is added to the scene",
    "category": "System"
}

import bpy
import aud
import os

sound_device = aud.Device()
existing_objects = None  # Delay initialization

class ObjectAddSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    sound_add: bpy.props.StringProperty(name="Add Sound", subtype='FILE_PATH')
    volume_add: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_add")
        layout.prop(self, "volume_add")

def play_add_sound():
    prefs = bpy.context.preferences.addons[__name__].preferences
    if os.path.exists(prefs.sound_add):
        try:
            sound = aud.Sound(prefs.sound_add)
            handle = sound_device.play(sound)
            handle.volume = prefs.volume_add
        except Exception as e:
            print(f"Error playing add sound: {e}")

def object_add_handler(scene):
    global existing_objects
    current_objects = set(obj.name for obj in bpy.context.scene.objects)

    if existing_objects is None:
        existing_objects = current_objects
        return

    new_objects = current_objects - existing_objects
    if new_objects:
        play_add_sound()

    existing_objects = current_objects

classes = [ObjectAddSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(object_add_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.remove(object_add_handler)

if __name__ == "__main__":
    register()
