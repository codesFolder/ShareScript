# =============================================================================
#  SALOME SCRIPT GENERATOR
#  This script WRITES another Python script that you can run in Salome.
#
#  INSTRUCTIONS:
#  1. Edit the variables in the '--- CONFIGURATION ---' section below.
#  2. Run this Python script. It will create a new file with the Salome commands.
#  3. If using an online compiler, download the generated output file.
#  4. Load and run the new file inside Salome.
# =============================================================================

# --- CONFIGURATION ---
# Edit the variables below.

# The full path to your STL geometry file.
# This path must be correct on the computer where you run SALOME.
# Use forward slashes (/).
STL_FILE_PATH = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run/cut1.stl"

# The desired number of layers/divisions. Must be 2 or more.
NUMBER_OF_DIVISIONS = 50

# The name of the Salome script file that this script will create.
OUTPUT_FILENAME = "salome_generated_script.py"

# --- MAIN SCRIPT (No need to edit below this line) ---

def generate_script():
    """Generates the Salome script file using the configuration above."""

    print("--- Salome STL Partition Script Generator ---")
    
    # This generator no longer checks if the file exists, so it can run in any environment.
    # The path will be used by Salome later.

    # Prepare the path for the Salome script
    stl_path_for_salome = STL_FILE_PATH.replace('\\', '/')

    print(f"Generating script file named '{OUTPUT_FILENAME}'...")
    print(f"It will process '{stl_path_for_salome}' with {NUMBER_OF_DIVISIONS} divisions.")

    # 2. Build the content of the new script file using the requested logic.
    # This follows the steps from your example: import, heal, partition.
    
    script_content = f"""#!/usr/bin/env python
#
# This file was generated automatically.
# It will import an STL, convert it to a solid, and partition it.
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
final_solid = geompy.UnionFaces(NoInternalFaces_1)
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
# Create N-1 planes to slice the solid into N layers
for i in range(1, {NUMBER_OF_DIVISIONS}):
    z_position = z_min + (i * layer_thickness)
    translated_plane = geompy.MakeTranslation(cutting_plane_proto, 0, 0, z_position)
    cutting_tools.append(translated_plane)

# --- PARTITION THE GEOMETRY ---
print("Partitioning the solid...")
Partition_1 = geompy.MakePartition([final_solid], cutting_tools, [], [], geompy.ShapeType["SOLID"], 0, [], 0)
print("Partition complete.")

# --- ADD OBJECTS TO STUDY ---
# (No groups will be created, as requested)
geompy.addToStudy(cut1_stl_1, 'imported_stl')
geompy.addToStudy(final_solid, 'final_solid')
geompy.addToStudy(Partition_1, 'Partition_1')

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
