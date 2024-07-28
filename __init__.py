
bl_info = {
    "name" : "Medieval 2 Toolkit",
    "author" : "WK",
    "description" : "Bulk import models",
    "blender" : (4, 0, 0),
    "version" : (0, 8, 28, 7),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
import bpy.utils
import sys
import pickle
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from . import EDU_converter, strat_import
from pathlib import Path
script_folder = Path(__file__).parent


def Read_Mod(directory):
    EDU_converter.mod_reader(bpy.path.abspath(directory))


def Import_Faction(import_faction, directory, upg_model):
    EDU_converter.importer(bpy.path.abspath(directory), import_faction, 0, 0, 1, upg_model)


def Import_Unit(import_faction, import_unit, directory, upg_model):
    EDU_converter.single_importer(bpy.path.abspath(directory), import_faction, import_unit, 0, 0, 1, upg_model)


def Sort_By_Faction(self, context):
    with open(script_folder/('text/master_dictionary.pkl'), 'rb') as master_input:
        master_dictionary = pickle.load(master_input)
    import_faction = context.scene.med2_tools.import_faction_single
    #print(import_faction)
    faction_units = []
    for unit in master_dictionary:
        if import_faction in unit["factions"]:
            entry = (unit["name"], unit["name"], "")
            faction_units.append(entry)
    #print(faction_units)
    return(faction_units)


def Import_Strat(directory):
    strat_import.strat_importer(bpy.path.abspath(directory))


class MEDIMPORTER_OT_Properties(bpy.types.PropertyGroup):
    directory_mod: StringProperty(name = "Mod data folder", description = "Directory to read mod data from", default = "C:\\Program Files", subtype = "DIR_PATH")
    directory_units: StringProperty(name = "Units folder", description = "Directory to get unit models from", default = "C:\\Program Files", subtype = "DIR_PATH")
    directory_strat: StringProperty(name = "Strat folder", description = "Directory to get strat models from", default = "C:\\Program Files", subtype = "DIR_PATH")

    with open(script_folder/('text/available_factions.pkl'), 'rb') as import_factions_input:
        factions = pickle.load(import_factions_input)
    with open(script_folder/('text/master_dictionary.pkl'), 'rb') as master_input:
        master_dictionary = pickle.load(master_input)
    import_faction: bpy.props.EnumProperty(name = "", description = "Select Faction", items = [(entry, entry, "") for entry in factions])
    import_faction_single: bpy.props.EnumProperty(name = "", description = "Select Faction", items = [(entry, entry, "") for entry in factions])
    import_unit: bpy.props.EnumProperty(name = "", description = "Select Unit", items = Sort_By_Faction)
    upg_model: bpy.props.IntProperty(name="Upgrade tier", description = "Select armour upgrade level", default = 0, min = 0, max = 3)
    upg_model_single: bpy.props.IntProperty(name="Upgrade tier", description = "Select armour upgrade level", default = 0, min = 0, max = 3)

class MEDIMPORTER_PT_Toolkit(bpy.types.Panel):
    bl_idname = "MEDIMPORTER_PT_Toolkit"
    bl_label = "Medieval 2 Toolkit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Import"

    def draw(self, context):
        if(context.mode == 'OBJECT'):
            col = self.layout.column(align=True)


class MEDIMPORTER_PT_Mod_Data(bpy.types.Panel):
    bl_idname = "MEDIMPORTER_PT_Mod_Data"
    bl_parent_id = "MEDIMPORTER_PT_Toolkit"
    bl_label = "Mod Data"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Import"

    def draw(self, context):
        if(context.mode == 'OBJECT'):
            col = self.layout.column(align=True)
            col.prop (context.scene.med2_tools, "directory_mod", text="")
            col.operator ("med2toolkit.reader", text="Read Mod Data")


class MEDIMPORTER_OT_Sorter(bpy.types.Operator):
    bl_idname = "med2toolkit.sorter"
    bl_label = "Select Mod Data Folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Sort_By_Faction(self, context)
        return{"FINISHED"}


class MEDIMPORTER_OT_Reader(bpy.types.Operator):
    bl_idname = "med2toolkit.reader"
    bl_label = "Select Mod Data Folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Read_Mod(context.scene.med2_tools.directory_mod)
        return{"FINISHED"}


class MEDIMPORTER_PT_Importer(bpy.types.Panel):
    bl_idname = "MEDIMPORTER_PT_Faction_Importer"
    bl_parent_id = "MEDIMPORTER_PT_Toolkit"
    bl_label = "Import Units"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Import"

    def draw(self, context):
        if(context.mode == 'OBJECT'):
            layout=self.layout
            layout.label(text = "Import By Faction")
            col = self.layout.column(align=True)
            col.prop (context.scene.med2_tools, "directory_units", text="")
            col.prop (context.scene.med2_tools, "import_faction", text="")
            col.prop (context.scene.med2_tools, "upg_model", text="Armour upgrade level:")
            col.operator ("med2toolkit.importer", text="Import Faction")
            layout.label(text = "Import Single Unit")
            col = self.layout.column(align=True)
            col.prop (context.scene.med2_tools, "import_faction_single", text="Faction")
            col.prop (context.scene.med2_tools, "import_unit", text="Unit")
            col.prop (context.scene.med2_tools, "upg_model_single", text="Armour upgrade level:")
            col.operator ("med2toolkit.singe_importer", text="Import Unit")


class MEDIMPORTER_OT_Importer(bpy.types.Operator):
    bl_idname = "med2toolkit.importer"
    bl_label = "Select Models Folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        inputs = context.scene.med2_tools
        Import_Faction(context.scene.med2_tools.import_faction, context.scene.med2_tools.directory_units, context.scene.med2_tools.upg_model)
        return{"FINISHED"}


class MEDIMPORTER_OT_Single_Importer(bpy.types.Operator):
    bl_idname = "med2toolkit.singe_importer"
    bl_label = "Select Models Folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        inputs = context.scene.med2_tools
        Import_Unit(context.scene.med2_tools.import_faction_single, context.scene.med2_tools.import_unit, context.scene.med2_tools.directory_units, context.scene.med2_tools.upg_model_single)
        return{"FINISHED"}
 

class MEDIMPORTER_PT_Misc(bpy.types.Panel):
    bl_idname = "MEDIMPORTER_PT_Misc"
    bl_parent_id = "MEDIMPORTER_PT_Toolkit"
    bl_label = "Misc."
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Import"

    def draw(self, context):
        if(context.mode == 'OBJECT'):
            layout=self.layout
            col = self.layout.column(align=True)
            col.operator("med2toolkit.variations", text="Randomize Variations")
            col.operator("med2toolkit.rendered", text="Render Unit Cards")
            layout=self.layout
            layout.label(text = "Import Strat Models")
            col = self.layout.column(align=True)
            col.prop (context.scene.med2_tools, "directory_strat", text="")
            col.operator("med2toolkit.strat", text="Import strat models")


class MEDIMPORTER_OT_Randomizer(bpy.types.Operator):
    bl_idname = "med2toolkit.variations"
    bl_label = "Randomize unit variations for the selection"
    bl_options = {"REGISTER", "UNDO"}
    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0: return False
        return context.object.select_get() and context.object.type == 'ARMATURE'

    def execute(self, context):
        EDU_converter.hide_variations()
        return{"FINISHED"}  


class MEDIMPORTER_OT_Renderer(bpy.types.Operator):
    bl_idname = "med2toolkit.rendered"
    bl_label = "Render unit cards"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        EDU_converter.renderer()
        return{"FINISHED"}


class MEDIMPORTER_OT_Strat(bpy.types.Operator):
    bl_idname = "med2toolkit.strat"
    bl_label = "Select Models Folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Import_Strat(context.scene.med2_tools.directory_strat)
        return{"FINISHED"}


classes = [
    MEDIMPORTER_PT_Toolkit,
    MEDIMPORTER_OT_Sorter,
    MEDIMPORTER_OT_Properties,
    MEDIMPORTER_PT_Mod_Data,
    MEDIMPORTER_PT_Importer,
    MEDIMPORTER_PT_Misc,
    MEDIMPORTER_OT_Reader,
    MEDIMPORTER_OT_Importer,
    MEDIMPORTER_OT_Randomizer,
    MEDIMPORTER_OT_Renderer,
    MEDIMPORTER_OT_Single_Importer,
    MEDIMPORTER_OT_Strat,
    ]

def register():
    for item in classes:
        bpy.utils.register_class(item)
    bpy.types.Scene.med2_tools = bpy.props.PointerProperty(type=MEDIMPORTER_OT_Properties)
    bpy.types.Scene.med2_unit = bpy.props.EnumProperty(name = "", description = "Select Unit", items = Sort_By_Faction)

def unregister():
    for item in classes:
        bpy.utils.unregister_class(item)
    del bpy.types.Scene.med2_tools
    del bpy.types.Scene.med2_unit
    
if __name__ == "__main__":
    register()