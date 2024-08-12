
import bpy
import os
from pathlib import Path, PurePath
import sys
from math import pi

def single_importer(filepath):
    dae_list = []
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    
    file = Path(filepath)
    folder = Path(filepath.rsplit('\\', 1)[0])
    x = 0
    y = 0
    z = 0
    bpy.ops.wm.collada_import(filepath = str(file))

    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    #Setup materials
    for mat in bpy.data.materials:
        for path, subdirs, files in os.walk(folder):
            for texture in files:
                if mat.name.replace("_dds", ".dds") == texture:
                    material = mat
                    #Setup material mode and keywords
                    material.use_nodes = True
                    material.blend_method = 'CLIP'
                    material.use_backface_culling = True
                    nodes = material.node_tree.nodes
                    new_link = material.node_tree.links.new

                    #Defining nodes
                    shader_node = material.node_tree.nodes["Principled BSDF"]
                    texture_image = nodes.new("ShaderNodeTexImage")
                    texture_image.location = (-506, 444)
                    texture_image.image = bpy.data.images.load(path+'\\'+texture)
                    #Linking nodes: colour -> shader; alpha -> shader; normal -> curves -> normal map -> shader
                    new_link(shader_node.inputs[0], texture_image.outputs[0])

