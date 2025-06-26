# =============================================================================
#  SALOME SCRIPT GENERATOR (FINAL WORKING VERSION)
#  This script WRITES another Python script that you can run in Salome.
#
#  INSTRUCTIONS:
#  1. Edit the variables in the '--- CONFIGURATION ---' section below.
#  2. Run this Python script.
#  3. Load and run the new file inside Salome. The groups will now appear.
# =============================================================================

# --- CONFIGURATION ---
# Edit the variables below.

# The full path to your STL geometry file.
STL_FILE_PATH = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run/cut1.stl"

# The desired number of layers/divisions.
NUMBER_OF_DIVISIONS = 6

# The name of the Salome script file that this script will create.
OUTPUT_FILENAME = "salome_generated_script.py"

# --- MAIN SCRIPT (No need to edit below this line) ---

def generate_script():
    """Generates the Salome script file with the final, working group creation logic."""

    print("--- Salome STL Partition & Grouping Script Generator (v5 - Final) ---")
    
    stl_path_for_salome = STL_FILE_PATH.replace('\\', '/')

    print(f"Generating script file named '{OUTPUT_FILENAME}'...")

    # Build the content of the new script file with the corrected addToStudy call.
    
    script_content = f"""#!/usr/bin/env python
#
# This file was generated automatically.
# It will import an STL, convert it to a solid, partition it,
# and create a named group for each solid layer.
#
import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

geompy = geomBuilder.New()

# --- GEOMETRY PROCESSING ---

# 1. Import STL and convert to a healed solid
print("Importing STL: {stl_path_for_salome}")
cut1_stl_1 = geompy.ImportSTL(r"{stl_path_for_salome}")
Shell_1 = geompy.MakeShell([cut1_stl_1])
Solid_1 = geompy.MakeSolid([Shell_1])
NoInternalFaces_1 = geompy.RemoveInternalFaces(Solid_1)
NoExtraEdges_1 = geompy.RemoveExtraEdges(NoInternalFaces_1, False)
final_solid = geompy.UnionFaces(NoExtraEdges_1)
print("Solid created and healed.")

# 2. Automatically calculate the solid's height for partitioning
b_box = geompy.BoundingBox(final_solid)
z_min = b_box[2]
z_max = b_box[5]
total_height = z_max - z_min
layer_thickness = total_height / {NUMBER_OF_DIVISIONS}
print(f"Detected total height: {{total_height}}, Layer thickness: {{layer_thickness}}")

# 3. Create the cutting planes
print("Creating {NUMBER_OF_DIVISIONS - 1} cutting planes...")
cutting_plane_proto = geompy.MakePlaneLCS(None, 2000, 1)

cutting_tools = []
for i in range(1, {NUMBER_OF_DIVISIONS}):
    z_position = z_min + (i * layer_thickness)
    translated_plane = geompy.MakeTranslation(cutting_plane_proto, 0, 0, z_position)
    cutting_tools.append(translated_plane)

# --- PARTITION THE GEOMETRY ---
print("Partitioning the solid...")
Partition_1 = geompy.MakePartition([final_solid], cutting_tools, [], [], geompy.ShapeType["SOLID"], 0, [], 0)
geompy.addToStudy(Partition_1, 'Partition_1')
print("Partition complete and added to study.")

# --- CREATE AND ADD VOLUME GROUPS FOR EACH LAYER ---
print("Creating volume groups for each layer...")
all_solids_in_partition = geompy.SubShapeAll(Partition_1, geompy.ShapeType["SOLID"])

layers_with_z_position = []
for solid_sub_shape in all_solids_in_partition:
    cdg_vertex = geompy.MakeCDG(solid_sub_shape)
    coords = geompy.PointCoordinates(cdg_vertex)
    center_z = coords[2]
    layers_with_z_position.append((center_z, solid_sub_shape))

layers_with_z_position.sort(key=lambda item: item[0])

sorted_layer_shapes = [item[1] for item in layers_with_z_position]
for i, layer_shape in enumerate(sorted_layer_shapes):
    group_name = f"layer_{{i + 1}}"
    layer_group = geompy.CreateGroup(Partition_1, geompy.ShapeType["SOLID"])
    sub_shape_id = geompy.GetSubShapeID(Partition_1, layer_shape)
    geompy.UnionIDs(layer_group, [sub_shape_id])
    
    # CORRECTION: Use the direct addToStudy method. This is more robust.
    # This will add the group to the top level of the study tree.
    geompy.addToStudy(layer_group, group_name)
    
    print(f"Created and added group to study: {{group_name}}")

print("Group creation complete.")

# --- ADD OTHER OBJECTS TO STUDY ---
geompy.addToStudy(final_solid, 'final_solid')

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

print("\\nSalome script finished execution.")
"""

    # 3. Write the content to the new file
    try:
        with open(OUTPUT_FILENAME, "w") as f:
            f.write(script_content)
        print(f"\nSUCCESS: Created the Salome script file named '{OUTPUT_FILENAME}'")
        print("You can now download this file and load it into Salome.")
    except Exception as e:
        print(f"\nERROR: Could not write to file. {e}")


# --- Run the generator function ---
if __name__ == "__main__":
    generate_script()
