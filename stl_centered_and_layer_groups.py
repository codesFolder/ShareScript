# =============================================================================
#  SALOME SCRIPT: STL to Layered Volume Groups
#  - Imports an STL file.
#  - Converts and heals it into a single solid.
#  - Centers the solid at the origin (0,0,0) for reliability.
#  - Partitions the solid into a specified number of layers.
#  - Creates a volume group for each layer (e.g., 'layer_1', 'layer_2').
# =============================================================================

# Please run this using file instead of copy pasting directly

import sys
import salome
salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()

import GEOM
from salome.geom import geomBuilder

# --- 1. CONFIGURATION ---
# Please edit these two variables

# The full path to your STL geometry file. Use forward slashes '/'.
STL_FILE_PATH = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run/stl/rocket1.stl"

# The desired number of layers/divisions.
NUMBER_OF_DIVISIONS = 6

# --- MAIN SCRIPT ---

# Wrap the entire workflow in a try/except block for clear error messages
try:
    print("--- Starting script ---")
    geompy = geomBuilder.New()

    # =========================================================================
    # --- 2. IMPORT AND HEAL STL ---
    # =========================================================================
    print(f"Importing and healing STL file: {STL_FILE_PATH}")
    
    # This is a robust chain of commands to convert an STL to a usable solid
    imported_stl = geompy.ImportSTL(STL_FILE_PATH, False) # False = do not create sewing
    shell = geompy.MakeShell([imported_stl])
    solid = geompy.MakeSolid([shell])
    solid = geompy.RemoveInternalFaces(solid)
    part_solid = geompy.RemoveExtraEdges(solid)

    # CRITICAL CHECK: Verify that the solid was created successfully.
    if part_solid is None:
        raise RuntimeError("Failed to create a valid solid from the STL. The file is likely damaged or non-manifold. Please repair it in a 3D modeling tool like Meshmixer or Blender.")
    
    print("STL successfully converted to a solid.")
    geompy.addToStudy(part_solid, 'original_healed_solid')

    # =========================================================================
    # --- 3. CENTER THE GEOMETRY ---
    # =========================================================================
    print("Centering the part so its base is at Z=0...")
    
    bbox = geompy.BoundingBox(part_solid)
    center_x = (bbox[0] + bbox[1]) / 2.0
    center_y = (bbox[2] + bbox[3]) / 2.0
    z_min = bbox[4] # Use index 4 for Z_min

    # This is the final, positioned part solid that we will work with
    part_solid_centered = geompy.MakeTranslation(part_solid, -center_x, -center_y, -z_min)
    geompy.addToStudy(part_solid_centered, 'part_solid_centered')
    print("Part centered successfully.")
    
    # =========================================================================
    # --- 4. PARTITION THE SOLID INTO LAYERS ---
    # =========================================================================
    # Get the dimensions of the newly centered part
    bbox_centered = geompy.BoundingBox(part_solid_centered)
    part_z_min = bbox_centered[4] # Should be 0.0
    part_z_max = bbox_centered[5]
    layer_thickness = (part_z_max - part_z_min) / NUMBER_OF_DIVISIONS
    
    print(f"Partitioning solid into {NUMBER_OF_DIVISIONS} layers of thickness {layer_thickness:.3f} mm...")

    # Create cutting planes
    cutting_tools = []
    plane_size = max(bbox_centered[1]-bbox_centered[0], bbox_centered[3]-bbox_centered[2]) * 1.5
    plane_proto = geompy.MakePlaneLCS(None, plane_size, plane_size)

    for i in range(1, NUMBER_OF_DIVISIONS):
        z_pos = part_z_min + (i * layer_thickness)
        plane = geompy.MakeTranslation(plane_proto, 0, 0, z_pos)
        cutting_tools.append(plane)

    # Perform the partition
    Partition_1 = geompy.MakePartition([part_solid_centered], cutting_tools, [], [], geompy.ShapeType["SOLID"], 0, [], 0)
    
    # CRITICAL CHECK: Verify the partition worked
    if Partition_1 is None:
        raise RuntimeError("Partition operation failed. The geometry may be too complex, or the STL still contains errors.")

    geompy.addToStudy(Partition_1, 'Partition_1')
    print("Partition complete.")

    # =========================================================================
    # --- 5. CREATE VOLUME GROUPS FOR EACH LAYER ---
    # =========================================================================
    print("Creating volume groups for each layer...")
    
    # Get all the individual solid volumes resulting from the partition
    all_solids_in_partition = geompy.SubShapeAll(Partition_1, geompy.ShapeType["SOLID"])

    # Sort the solids by their Z-position to ensure correct layer numbering
    sorted_layers = sorted(
        all_solids_in_partition,
        key=lambda s: geompy.PointCoordinates(geompy.MakeCDG(s))[2]
    )

    # Loop through the sorted solids and create a named group for each
    for i, layer_shape in enumerate(sorted_layers):
        group_name = f"layer_{i + 1}"
        
        # Create an empty group on the Partition_1 object
        layer_group = geompy.CreateGroup(Partition_1, geompy.ShapeType["SOLID"])
        
        # Get the unique ID of the sub-shape (the layer solid)
        sub_shape_id = geompy.GetSubShapeID(Partition_1, layer_shape)
        
        # Add that ID to the group
        geompy.UnionIDs(layer_group, [sub_shape_id])
        
        # Add the group to the study tree as a child of Partition_1
        geompy.addToStudyInFather(Partition_1, layer_group, group_name)
        
        print(f"Created group: {group_name}")
    
    print("\nAll tasks completed successfully.")

except Exception as e:
    # This will catch any error and print it clearly
    print("\n--- SCRIPT FAILED ---")
    import traceback
    traceback.print_exc()

finally:
    # This part always runs, even if the script fails
    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser()
    print("--- Script finished execution ---")
