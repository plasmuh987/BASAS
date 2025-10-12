bl_info = {
    "name": "Object Delete Sound",
    "author": "Plasmuh987",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when an object is deleted from the scene",
    "category": "System"
}

import bpy
import aud
import os
from bpy.app.handlers import persistent

sound_device = aud.Device()
existing_objects = None
delete_sound_handle = None

class DeleteSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    sound_delete: bpy.props.StringProperty(name="Delete Sound", subtype='FILE_PATH')
    volume_delete: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_delete")
        layout.prop(self, "volume_delete")

def play_delete_sound():
    global delete_sound_handle
    addon = bpy.context.preferences.addons.get(__name__)
    if not addon:
        return
    prefs = addon.preferences
    if prefs.sound_delete and os.path.exists(prefs.sound_delete):
        try:
            if delete_sound_handle and delete_sound_handle.status:
                print("Stopping previous delete sound.")
                delete_sound_handle.stop()
            print(f"DeleteSound: Playing sound: {prefs.sound_delete}")
            sound = aud.Sound(prefs.sound_delete)
            delete_sound_handle = sound_device.play(sound)
            delete_sound_handle.volume = prefs.volume_delete
        except Exception as e:
            print(f"DeleteSound: Error playing delete sound: {e}")

@persistent
def delete_handler(scene):
    global existing_objects
    current_objects = set(obj.name for obj in bpy.context.scene.objects)
    if existing_objects is None:
        existing_objects = current_objects
        return
    removed_objects = existing_objects - current_objects
    if removed_objects:
        print(f"DeleteSound: Objects deleted: {removed_objects}")
        play_delete_sound()
    existing_objects = current_objects

@persistent
def init_delete_handler(dummy):
    global existing_objects
    existing_objects = set(obj.name for obj in bpy.context.scene.objects)
    if delete_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(delete_handler)
    print("DeleteSound: Handlers reinitialized after load.")

classes = [DeleteSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(delete_handler)
    bpy.app.handlers.load_post.append(init_delete_handler)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if delete_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(delete_handler)
    if init_delete_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_delete_handler)