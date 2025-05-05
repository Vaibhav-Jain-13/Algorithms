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
# Deselect all objects
bpy.ops.object.select_all(action='DESELECT')

# Select the object named "workpiece"
workpiece = bpy.data.objects.get("workpiece")
if workpiece:
    workpiece.select_set(True)
    bpy.ops.object.delete()

class ImportSTLOperator(bpy.types.Operator, ImportHelper): 
    bl_idname = "object.import_stl_operator"
    bl_label = "Import STL Operator"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        try:
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
            
            obj = bpy.data.objects['Head']
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
    
    def check_collision(self, obj1, obj2):
        height1 = obj1.dimensions.z
        height2 = obj2.dimensions.z
        radius1 = obj1.dimensions.x / 2
        radius2 = obj2.dimensions.x / 2
        center1 = obj1.matrix_world.translation
        center2 = obj2.matrix_world.translation
        
        if abs(center1.z - center2.z) > (height1 + height2) / 2:
            return False
        
        distance = sqrt((center1.x - center2.x)**2 + (center1.y - center2.y)**2)
        if distance > (radius1 + radius2):
            return False
        
        return True
    
    def execute(self, context):
        try:
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            
            obj = bpy.data.objects['workpiece']
            obj.select_set(True)
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
            
            grinder = bpy.data.objects.get("grinder")
            Head = bpy.data.objects.get("Head")
            Tailstock = bpy.data.objects.get("Tailstock")
            workpiece = bpy.data.objects.get("workpiece")
            
            g_mat = bpy.data.materials.new(name="GrindingMaterial")
            g_mat.diffuse_color = (0.2, 0.6, 0.2, 1)
            grinder.data.materials.append(g_mat)
            
            workpiece.driver_add("rotation_euler", 2).driver.expression = "frame * 0.1"
            
            mat = bpy.data.materials.new(name="WorkpieceMaterial")
            mat.diffuse_color = (0.2, 0.2, 0.2, 1)
            workpiece.data.materials.append(mat)
            
            objects_to_clear = ["grinder", "Head", "Tailstock", "workpiece"]
            for obj_name in objects_to_clear:
                obj = bpy.data.objects.get(obj_name)
                if obj and obj.animation_data:
                    obj.animation_data_clear()
            
            toolpath = eval(self.toolpath)
            frame_start = 1
            for index, (coords, feedrate) in enumerate(toolpath[:-1]):
                x, y, z = coords
                grinder.location = (x + 6.5, 0.032006, 7)
                Head.location = (0, 0, z)
                Tailstock.location = (0, 0, z)
                workpiece.location = (0, 0, z)
                
                grinder.keyframe_insert(data_path="location", frame=frame_start)
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
            Head.keyframe_insert(data_path="location", frame=frame_start)
            Tailstock.keyframe_insert(data_path="location", frame=frame_start)
            workpiece.keyframe_insert(data_path="location", frame=frame_start)
            
            context.scene.frame_end = frame_start
            context.scene.frame_start = 1
            
#            i = 0
#            for frame in range(1, frame_start + 1):
#                context.scene.frame_set(frame)
#                if self.check_collision(grinder, workpiece):
#                    i += 1
#                    if i == 1:
#                        g_mat.diffuse_color = (0.2, 0.6, 0.2, 1)
#                        grinder.data.materials.append(g_mat)
#                        g_mat.keyframe_insert(data_path="diffuse_color", frame=frame - 1)
#                        mat.diffuse_color = (0.5, 0.5, 0.5, 1)
#                        workpiece.data.materials.append(mat)
#                        mat.keyframe_insert(data_path="diffuse_color", frame=frame)
#                else:
#                    g_mat.diffuse_color = (1, 0, 0, 1)
#                    grinder.data.materials.append(g_mat)
#                    g_mat.keyframe_insert(data_path="diffuse_color", frame=frame)
#                    mat.diffuse_color = (1, 0, 0, 1)
#                    workpiece.data.materials.append(mat)
#                    mat.keyframe_insert(data_path="diffuse_color", frame=frame)
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
        
        layout.operator(ImportSTLOperator.bl_idname)
        layout.operator(SelectHeadOperator.bl_idname)
        layout.operator(ExecuteRestOperator.bl_idname)

def menu_func(self, context):
    
    self.layout.operator(ImportSTLOperator.bl_idname)
    self.layout.operator(SelectHeadOperator.bl_idname)
    self.layout.operator(ExecuteRestOperator.bl_idname)

def register():
    
    bpy.utils.register_class(ImportSTLOperator)
    bpy.utils.register_class(SelectHeadOperator)
    bpy.utils.register_class(ExecuteRestOperator)
    bpy.utils.register_class(SimpleOperatorPanel)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(ImportSTLOperator)
    bpy.utils.unregister_class(SelectHeadOperator)
    bpy.utils.unregister_class(ExecuteRestOperator)
    bpy.utils.unregister_class(SimpleOperatorPanel)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()


 

 
