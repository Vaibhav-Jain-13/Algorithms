import bpy
import bmesh
from mathutils.bvhtree import BVHTree

def check_intersection(obj1, obj2):
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

for obj in bpy.context.scene.objects:
    if obj.animation_data:
        obj.animation_data_clear()

# Clear animation data for the scene itself
bpy.context.scene.animation_data_clear()

# Retrieve the imported shapes
T1 = bpy.data.objects.get("T1")
shape3 = bpy.data.objects.get("Shape3")
shape2 = bpy.data.objects.get("Shape2")
p4 = bpy.data.objects.get("Part4")

# Set initial locations
T1.location = (-10, 0, 0)
shape3.location = (0, 20, 0)
shape2.location = (-20,0,0)
p4.location = (0,-30,0)

T1.keyframe_insert(data_path="location", frame=1)
shape3.keyframe_insert(data_path="location", frame=1)
shape2.keyframe_insert(data_path="location", frame=1)
p4.keyframe_insert(data_path="location", frame=1)

## Retrieve the materials for the imported shapes
T1_mat = T1.active_material
nodes_T1 = T1_mat.node_tree.nodes
principled_T1 = nodes_T1.get("Principled BSDF")
t_T1 = tuple(principled_T1.inputs['Base Color'].default_value)

# Retrieve the materials for the imported shapes
s2_mat = shape2.active_material
nodes_s2 = s2_mat.node_tree.nodes
principled_s2 = nodes_s2.get("Principled BSDF")
t_s2 = tuple(principled_s2.inputs['Base Color'].default_value)

# Retrieve the materials for the imported shapes
s3_mat = shape3.active_material
nodes_s3 = s3_mat.node_tree.nodes
principled_s3 = nodes_s3.get("Principled BSDF")
t_s3 = tuple(principled_s3.inputs['Base Color'].default_value)

# Retrieve the materials for the imported shapes
p4_mat = p4.active_material
nodes_p4 = p4_mat.node_tree.nodes
principled_p4 = nodes_p4.get("Principled BSDF")
t_p4 = tuple(principled_p4.inputs['Base Color'].default_value)

principled_T1.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=1)
principled_s2.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=1)
principled_s3.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=1)
principled_p4.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=1)

#Set final locations
T1.location = (10, 0, 0)
shape3.location = (0, -20, 0)
shape2.location = (20,5,0)
p4.location = (30,10,0)

# Insert keyframe for the final location
T1.keyframe_insert(data_path="location", frame=60)
shape3.keyframe_insert(data_path="location", frame=60)
shape2.keyframe_insert(data_path="location", frame=60)
p4.keyframe_insert(data_path="location", frame=60)

objects = ["Part4","Shape2","Shape3","T1"]
for obj1 in range (len(objects)):
    for obj2 in range (obj1+1,len(objects),1):
        
        # Retrieve the imported shapes
        cu = bpy.data.objects.get(objects[obj1])
        su = bpy.data.objects.get(objects[obj2])
      
        # Retrieve the materials for the imported shapes
        c_mat = cu.active_material
        nodes = c_mat.node_tree.nodes
        principled = nodes.get("Principled BSDF")
        c = tuple(principled.inputs['Base Color'].default_value)

        # Retrieve the materials for the imported shapes
        mat = su.active_material
        nod = mat.node_tree.nodes
        princi = nod.get("Principled BSDF")
        s = tuple(princi.inputs['Base Color'].default_value)

        # Collision detection and color change
        colliding_f = 0
        i = 0
        for frame in range(1, 70, 1):
            bpy.context.scene.frame_set(frame)
            if check_intersection(cu, su):
                i += 1
                colliding_f = frame
                if i == 1:
                    if tuple(principled.inputs['Base Color'].default_value) != (1,0,0,1):
                        principled.inputs['Base Color'].default_value = c         
                        principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f-1)
                    if tuple(princi.inputs['Base Color'].default_value) != (1,0,0,1):
                        princi.inputs['Base Color'].default_value = s
                        princi.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f-1)           
                    
                    principled.inputs['Base Color'].default_value = (1, 0, 0, 1)
                    princi.inputs['Base Color'].default_value = (1, 0, 0, 1)
                    principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f)
                    princi.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f) 
                else:
                    principled.inputs['Base Color'].default_value = (1, 0, 0, 1)
                    princi.inputs['Base Color'].default_value = (1, 0, 0, 1)            
                    principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f)
                    princi.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f) 
            else:
                principled.inputs['Base Color'].default_value = c
                princi.inputs['Base Color'].default_value = s      
                principled.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f+1)
                princi.inputs['Base Color'].keyframe_insert(data_path="default_value", frame=colliding_f+1) 
