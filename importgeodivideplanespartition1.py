# =============================================================================
#  SALOME SCRIPT GENERATOR
#  This script WRITES another Python script that you can run in Salome.
# =============================================================================

# --- CONFIGURATION ---
# The total height of your geometry. Based on your example (25, 50, 75 for 4 layers),
# the total height is 100. Change this if your box has a different height.
TOTAL_HEIGHT = 100.0

# The full path to your geometry file.
# The script will ask you for this when you run it.

# The name of the file that this script will create.
OUTPUT_FILENAME = "salome_partition_script.py"

# --- MAIN SCRIPT ---

def generate_script():
    """Asks for user input and generates the Salome script file."""

    print("--- Salome Partition Script Generator ---")
    
    # 1. Get user input
    try:
        num_divisions = int(input(f"Enter the desired number of divisions (e.g., 4 or 100): "))
        if num_divisions < 2:
            print("Error: Number of divisions must be at least 2.")
            return
    except ValueError:
        print("Error: Please enter a valid integer.")
        return

    #brep_path = input(r"Enter the FULL path to your .brep file (e.g., C:\Users\YourUser\Box_1.brep): ")
    # Replace single backslashes with forward slashes for Python/Salome compatibility
    #brep_path_for_salome = brep_path.replace('\\', '/')

    print("-" * 40)
    print(f"Generating script '{OUTPUT_FILENAME}' for {num_divisions} divisions...")

    # 2. Start building the content of the new script file
    
    # --- HEADER ---
    script_content = f"""#!/usr/bin/env python
#
# This file was generated automatically by a script generator.
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

# --- GEOMETRY DEFINITION ---
O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

# Import the base geometry
Box_1_brep_1 = geompy.ImportBREP("C:/Users/DELL/Downloads/v2024/salome_meca/Box_1.brep")

# Create the initial plane that will be copied and translated
Plane_1 = geompy.MakePlaneLCS(None, 2000, 1)

# --- CREATE TRANSLATED PLANES ---
"""

    # --- LOOP TO CREATE TRANSLATION LINES ---
    layer_thickness = TOTAL_HEIGHT / num_divisions
    translation_variable_names = []
    
    # We need N-1 planes to create N divisions
    for i in range(1, num_divisions):
        z_position = i * layer_thickness
        variable_name = f"Translation_{i}"
        
        # Add the line of code to the script content
        script_content += f"{variable_name} = geompy.MakeTranslation(Plane_1, 0, 0, {z_position})\n"
        
        # Keep track of the variable name for the partition step
        translation_variable_names.append(variable_name)

    # --- PARTITION AND FOOTER ---
    # Join the variable names with commas: "Translation_1, Translation_2, ..."
    translations_list_str = ", ".join(translation_variable_names)

    script_content += f"""
# --- PARTITION THE GEOMETRY ---
# Use all the translated planes to cut the box
Partition_1 = geompy.MakePartition([Box_1_brep_1], [{translations_list_str}], [], [], geompy.ShapeType["SOLID"], 0, [], 0)

# --- ADD OBJECTS TO STUDY ---
# (Group creation is commented out below as requested)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Box_1_brep_1, 'Box_1.brep_1' )
geompy.addToStudy( Plane_1, 'Plane_1' )
"""
    # Add all the translation objects to the study
    for var_name in translation_variable_names:
        script_content += f"geompy.addToStudy( {var_name}, '{var_name}' )\n"

    script_content += f"""geompy.addToStudy( Partition_1, 'Partition_1' )

# =================================================================
# --- OPTIONAL: MANUAL GROUP CREATION ---
# After running this script, you can manually create groups in the GUI.
# Then, you can dump the study to a Python file to see the IDs Salome used.
# The code would look like this, but the IDs ([31], [2], etc.) will change
# every time and cannot be predicted.
#
# bottom = geompy.CreateGroup(Partition_1, geompy.ShapeType["FACE"])
# geompy.UnionIDs(bottom, [31]) # ID will be different for you
# layer1 = geompy.CreateGroup(Partition_1, geompy.ShapeType["SOLID"])
# geompy.UnionIDs(layer1, [2]) # ID will be different for you
#
# geompy.addToStudyInFather( Partition_1, bottom, 'bottom' )
# geompy.addToStudyInFather( Partition_1, layer1, 'layer1' )
# =================================================================

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

print("\\nScript finished execution.")
"""

    # 3. Write the content to the new file
    try:
        with open(OUTPUT_FILENAME, "w") as f:
            f.write(script_content)
        print(f"\nSUCCESS: Created the Salome script file named '{OUTPUT_FILENAME}'")
        print("You can now load this new file into Salome.")
    except Exception as e:
        print(f"\nERROR: Could not write to file. {e}")


# --- Run the generator function ---
if __name__ == "__main__":
    generate_script()
