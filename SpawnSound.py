bl_info = {
    "name": "Object Spawn Sound",
    "author": "Plasmuh987",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays a sound when an object is spawned into the scene",
    "category": "System"
}

import bpy
import aud
import os
from bpy.app.handlers import persistent

sound_device = aud.Device()
existing_objects = None
add_sound_handle = None

class ObjectAddSoundPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    sound_add: bpy.props.StringProperty(name="Add Sound", subtype='FILE_PATH')
    volume_add: bpy.props.FloatProperty(name="Volume", min=0.0, max=2.0, default=1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sound_add")
        layout.prop(self, "volume_add")

def play_add_sound():
    global add_sound_handle
    addon = bpy.context.preferences.addons.get(__name__)
    if not addon:
        return
    prefs = addon.preferences
    if prefs.sound_add and os.path.exists(prefs.sound_add):
        try:
            if add_sound_handle and add_sound_handle.status:
                print("Stopping previous add sound.")
                add_sound_handle.stop()
            print(f"SpawnSound: Playing sound: {prefs.sound_add}")
            sound = aud.Sound(prefs.sound_add)
            add_sound_handle = sound_device.play(sound)
            add_sound_handle.volume = prefs.volume_add
        except Exception as e:
            print(f"SpawnSound: Error playing add sound: {e}")

@persistent
def object_add_handler(scene):
    global existing_objects
    current_objects = set(obj.name for obj in scene.objects)
    if existing_objects is None:
        existing_objects = current_objects
        return
    new_objects = current_objects - existing_objects
    if new_objects:
        print(f"SpawnSound: New objects detected: {new_objects}")
        play_add_sound()
    existing_objects = current_objects

@persistent
def init_existing_objects(dummy):
    global existing_objects
    existing_objects = set(obj.name for obj in bpy.context.scene.objects)
    if object_add_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(object_add_handler)
    print("SpawnSound: Handlers reinitialized after load.")

classes = [ObjectAddSoundPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(object_add_handler)
    bpy.app.handlers.load_post.append(init_existing_objects)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if object_add_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(object_add_handler)
    if init_existing_objects in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_existing_objects)