import bpy
import bmesh
from mathutils import Vector

# Function to check if two objects are colliding
def check_collision(obj1, obj2):
    # Get the bounding boxes of both objects
    bbox1 = [obj1.matrix_world @ Vector(corner) for corner in obj1.bound_box]
    bbox2 = [obj2.matrix_world @ Vector(corner) for corner in obj2.bound_box]
    
    # Check for overlap in all three axes
    for i in range(3):
        if max(bbox1, key=lambda v: v[i])[i] < min(bbox2, key=lambda v: v[i])[i] or \
           max(bbox2, key=lambda v: v[i])[i] < min(bbox1, key=lambda v: v[i])[i]:
            return False
    return True

# Create the first shape (Cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.object

cube_mat = bpy.data.materials.new(name="CubeMaterial")
cube_mat.diffuse_color = (0, 0, 1, 1)  # Blue color
cube.data.materials.append(cube_mat)


# Create the second shape (Sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(1, 0, 0))
sphere = bpy.context.object
sphere_mat = bpy.data.materials.new(name="SphereMaterial")
sphere_mat.diffuse_color = (0, 1, 0, 1)  # Green color
sphere.data.materials.append(sphere_mat)

if check_collision(cube,sphere):
    # Assign initial materials
    cube_mat.diffuse_color = (1, 0, 0, 1)  # Blue color
    cube.data.materials.append(cube_mat)
    # Assign initial materials
    
