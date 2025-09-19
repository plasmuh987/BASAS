bl_info = {
    "name": "Object Delete Sound",
    "author": "Plasmuh987", #Microsoft Copilot Assisted
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when an object is deleted from the scene",
    "category": "System"
}

import bpy
import aud
import os

sound_device = aud.Device()
existing_objects = None  # Will be initialized in handler

class ObjectDeleteSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    sound_delete: bpy.props.StringProperty(name="Delete Sound", subtype='FILE_PATH')
    volume_delete: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_delete")
        layout.prop(self, "volume_delete")

def play_delete_sound():
    prefs = bpy.context.preferences.addons[__name__].preferences
    if os.path.exists(prefs.sound_delete):
        try:
            sound = aud.Sound(prefs.sound_delete)
            handle = sound_device.play(sound)
            handle.volume = prefs.volume_delete
        except Exception as e:
            print(f"Error playing delete sound: {e}")

def object_delete_handler(scene):
    global existing_objects
    current_objects = set(obj.name for obj in bpy.context.scene.objects)

    if existing_objects is None:
        existing_objects = current_objects
        return

    deleted_objects = existing_objects - current_objects
    if deleted_objects:
        play_delete_sound()

    existing_objects = current_objects

classes = [ObjectDeleteSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(object_delete_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.depsgraph_update_post.remove(object_delete_handler)

if __name__ == "__main__":
    register()
