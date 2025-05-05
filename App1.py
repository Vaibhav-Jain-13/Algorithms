# Without collision detection but proper functioning

bl_info = {
    "name": "CNC_Grinding",
    "author": "Vaibhav_Jain",
    "version": (1, 0),
    "blender": (4, 3, 2),
    "location": "View3d > Tool",
    "category": "Add Mesh"
}

import math
import bpy
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper
from math import sqrt
from mathutils.bvhtree import BVHTree
import bmesh

class WarningPopupOperator(bpy.types.Operator):
    bl_idname = "wm.warning_popup"
    bl_label = "Warning Popup"

    message: bpy.props.StringProperty(name="Message", default="Collision Detected: Kindly look for red regions!")

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.message)


    
class ADDONAME_OT_TemplateOperator(bpy.types.Operator):
    bl_label = "Machine Operator"
    bl_idname = "wm.template_operator"
    
    preset_enum:bpy.props.EnumProperty(
        name = "",
        description = "Select an option",
        items = [ 
                ("OP1","M1","Add machine 1 to the scene"),
                ("OP2","M2","Add machine 2 to the scene"),
                ("OP3","Heelo","Add a Hello to the scene")]
    )
    

        
    def invoke(self, context, event):    #Gives a clickable button
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):      #Displays what happens after clickable button
        layout = self.layout
        layout.prop(self,"preset_enum")
        layout.prop(self,"p_enum")
    
    def execute(self, context):    # Decides what happens after clicking OK
        # Clear existing objects
        bpy.ops.object.select_all(action='SELECT')
        
        bpy.ops.object.delete()
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')

        # Iterate through all collections and select them
        for collection in bpy.data.collections:
            
            bpy.data.collections.remove(collection)

        if self.preset_enum == "OP1":
            # Path to the Blender file
            blend_file_path = r"C:\Users\intern1\Desktop\Project\Pilot_Project\Blender\Model_Import2.blend"
            # Path inside the Blender file to the collection
            collection_path = "Collection"

            # Full path to the collection
            full_path = blend_file_path + "\\" + collection_path + "\\M1"

            # Append the collection
            bpy.ops.wm.append(
                filepath=full_path,
                directory=blend_file_path + "\\" + collection_path,
                filename="M1"
            )   

            
        elif self.preset_enum == "OP2":
            # Path to the Blender file
            blend_file_path = r"C:\Users\intern1\Desktop\Project\Pilot_Project\Blender\M2.blend"
            # Path inside the Blender file to the collection
            collection_path = "Collection"

            # Full path to the collection
            full_path = blend_file_path + "\\" + collection_path + "\\M1"

            # Append the collection
            bpy.ops.wm.append(
                filepath=full_path,
                directory=blend_file_path + "\\" + collection_path,
                filename="M2"
            )

            
        elif self.preset_enum == "OP3":
            bpy.ops.mesh.primitive_monkey_add()
        return {'FINISHED'}    

class ImportSTLOperator(bpy.types.Operator, ImportHelper): 
    bl_idname = "object.import_stl_operator"
    bl_label = "Import STL Operator"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        try:
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            # Select the object named "workpiece"
            workpiece = bpy.data.objects.get("workpiece")
#            if workpiece:
#                
#                workpiece.select_set(True)
#                bpy.ops.object.delete()
            filepath = self.filepath
            bpy.ops.wm.stl_import(filepath=filepath)
            workpiece = context.selected_objects[0]
            workpiece.name = "workpiece"
            workpiece.scale = (0.04, 0.04, 0.04)
            
            
            bpy.ops.object.editmode_toggle()
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class SelectHeadOperator(bpy.types.Operator):
    bl_idname = "object.select_head_operator"
    bl_label = "Select Head Operator"
    
    def execute(self, context):
        try:
            workpiece = context.object
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

            obj = bpy.data.objects['Headstock']
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.editmode_toggle()
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

class ExecuteRestOperator(bpy.types.Operator):
    bl_idname = "object.execute_rest_operator"
    bl_label = "Execute Rest Operator"
    
    toolpath: bpy.props.StringProperty(name="Toolpath")
    
    def check_intersection(self,obj1, obj2):
        bm1 = bmesh.new()
        bm2 = bmesh.new()
        
        bm1.from_mesh(obj1.data)
        bm2.from_mesh(obj2.data)
        
        bm1.transform(obj1.matrix_world)
        bm2.transform(obj2.matrix_world)
        
        bvh1 = BVHTree.FromBMesh(bm1)
        bvh2 = BVHTree.FromBMesh(bm2)
        
        intersections = bvh1.overlap(bvh2)
        
        return len(intersections) > 0

#    # Example usage
#    obj1 = bpy.context.scene.objects['Suzanne.001']
#    obj2 = bpy.context.scene.objects['Suzanne']

#    if check_intersection(obj1, obj2):
#        
#        bpy.ops.mesh.primitive_uv_sphere_add()

#    else:
#       
#        bpy.ops.mesh.primitive_cube_add()
    
    def execute(self, context):
        try:
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            
            obj = bpy.data.objects['workpiece']
            obj.select_set(True)
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
            
            grinder = bpy.data.objects.get("Grinding_Wheel")
            x_Slide = bpy.data.objects.get("x_Slide")
            Head = bpy.data.objects.get("Headstock")
            Tailstock = bpy.data.objects.get("Tailstock")
            workpiece = bpy.data.objects.get("workpiece")
            
#            g_mat = bpy.data.materials.new(name="GrindingMaterial")
#            g_mat.diffuse_color = (0.2, 0.6, 0.2, 1)
#            grinder.data.materials.append(g_mat)
            
            workpiece.driver_add("rotation_euler", 2).driver.expression = "frame * 0.1"
            
#            mat = bpy.data.materials.new(name="WorkpieceMaterial")
#            mat.diffuse_color = (0.2, 0.2, 0.2, 1)
#            workpiece.data.materials.append(mat)
            
            # Clear the animation
            objects_to_clear = ["grinder", "Head", "Tailstock", "workpiece","x_Slide"]
            for obj_name in objects_to_clear:
                obj = bpy.data.objects.get(obj_name)
                if obj and obj.animation_data:
                    obj.animation_data_clear()
            
            toolpath = eval(self.toolpath)
            frame_start = 1
            for index, (coords, feedrate) in enumerate(toolpath[:-1]):
                x, y, z = coords
                grinder.location = (x + 6.5, 0.032006, 1)
                x_Slide.location = (x + 6.5,0.032 ,1)
                Head.location = (0, 0, z)
                Tailstock.location = (0, 0, z)
                workpiece.location = (0, 0,  z)
                
                grinder.keyframe_insert(data_path="location", frame=frame_start)
                x_Slide.keyframe_insert(data_path="location", frame=frame_start)
                Head.keyframe_insert(data_path="location", frame=frame_start)
                Tailstock.keyframe_insert(data_path="location", frame=frame_start)
                workpiece.keyframe_insert(data_path="location", frame=frame_start)
                
                next_coords = toolpath[index + 1][0]
                next_x, next_y, next_z = next_coords
                distance = math.sqrt((next_x - x)**2 + (next_y - y)**2 + (next_z - z)**2)
                actual_feed = toolpath[index + 1][1]
                feed = actual_feed / 60
                frames_required = int(24 * distance / feed)
                frame_start += frames_required
                
                print(f"Inserting keyframe at frame: {frame_start}")
            
            grinder.keyframe_insert(data_path="location", frame=frame_start)
            x_Slide.keyframe_insert(data_path="location", frame=frame_start)
            Head.keyframe_insert(data_path="location", frame=frame_start)
            Tailstock.keyframe_insert(data_path="location", frame=frame_start)
            workpiece.keyframe_insert(data_path="location", frame=frame_start)
            
            context.scene.frame_end = frame_start
            context.scene.frame_start = 1
#            objects = ["Bed", "Grinding_Wheel", "Headstock", "Tailstock", "x_Slide", "workpiece"]

#            for i, obj_name1 in enumerate(objects):
#                for obj_name2 in objects[i + 1:]:
#                    intersection_found = False
#                    for frame in range(1, frame_start + 1):
#                        context.scene.frame_set(frame)
#                        obj1 = bpy.data.objects.get(obj_name1)
#                        obj2 = bpy.data.objects.get(obj_name2)
#                        if self.check_intersection(obj1, obj2):
#                            bpy.ops.mesh.primitive_cube_add()
#                            if not intersection_found:
#                                bpy.ops.wm.warning_popup('INVOKE_DEFAULT')
#                                intersection_found = True
            
#            objects = ["Bed","Grinding_Wheel","Headstock","Tailstock","x_Slide","workpiece"]
#            
#            for i in range(len(objects)):
#                for j in range(i + 1, len(objects)):
#                    f = 0
#                    for frame in range(1, frame_start + 1):
#                        context.scene.frame_set(frame)
#                        obj1 = bpy.data.objects.get(objects[i])
#                        obj2 = bpy.data.objects.get(objects[j])
#                        if self.check_intersection(obj1,obj2):
#                            bpy.ops.mesh.primitive_cube_add()
#  
#                            f =+ 1
#                            if f == 1:
##                                g_mat = obj1.active_material
##                                mat = obj2.active_material
#                                bpy.ops.wm.warning_popup('INVOKE_DEFAULT')
##                                g_mat.keyframe_insert(data_path="diffuse_color", frame=frame - 1)
#                                
#                                
##                               mat.keyframe_insert(data_path="diffuse_color", frame=frame-1)
##                            else:
##                                g_mat.diffuse_color = (1, 0, 0, 1)
##                                obj1.data.materials.append(g_mat)
##                                g_mat.keyframe_insert(data_path="diffuse_color", frame=frame)
##                                mat.diffuse_color = (1, 0, 0, 1)
##                                obj2.data.materials.append(mat)
##                                mat.keyframe_insert(data_path="diffuse_color", frame=frame)
#            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class SimpleOperatorPanel(Panel):
    bl_label = "Grinding Panel"
    bl_idname = "OBJECT_PT_simple_operator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CNC Grinding'

    def draw(self, context):
        layout = self.layout
        layout.operator(ADDONAME_OT_TemplateOperator.bl_idname)
        layout.operator(ImportSTLOperator.bl_idname)
        layout.operator(SelectHeadOperator.bl_idname)
        layout.operator(ExecuteRestOperator.bl_idname)

def menu_func(self, context):
    self.layout.operator(ADDONAME_OT_TemplateOperator.bl_idname)
    self.layout.operator(ImportSTLOperator.bl_idname)
    self.layout.operator(SelectHeadOperator.bl_idname)
    self.layout.operator(ExecuteRestOperator.bl_idname)

def register():
    bpy.utils.register_class(ADDONAME_OT_TemplateOperator)
    bpy.utils.register_class(ImportSTLOperator)
    bpy.utils.register_class(SelectHeadOperator)
    bpy.utils.register_class(ExecuteRestOperator)
    bpy.utils.register_class(SimpleOperatorPanel)
    bpy.utils.register_class(WarningPopupOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ADDONAME_OT_TemplateOperator)
    bpy.utils.unregister_class(ImportSTLOperator)
    bpy.utils.unregister_class(SelectHeadOperator)
    bpy.utils.unregister_class(ExecuteRestOperator)
    bpy.utils.unregister_class(SimpleOperatorPanel)
    bpy.utils.unregister_class(WarningPopupOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()


 



 

 
 
 
