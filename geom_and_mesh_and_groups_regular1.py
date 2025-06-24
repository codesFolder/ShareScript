# make_salome_script.py
# This script generates a Salome Meca python script to create and mesh a cuboid.

# --- USER INPUTS ---
# --- You can change these values to define your cuboid ---

# 1. Geometry Parameters
length_x = 1.0  # Dimension in X direction
width_y  = 20.0  # Dimension in Y direction
height_z = 25.0  # Dimension in Z direction

# 2. Meshing Parameters (Number of divisions along each axis)
nx = 2  # Number of divisions in X
ny = 40  # Number of divisions in Y
nz = 50  # Number of divisions in Z (this will also be the number of layers)

# 3. Output file name
output_filename = "generated_cuboid_script.py"

# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC ---

# Calculate element size for the Body Fitting algorithm
# The format requires the size of the element, not the number of divisions.
element_size_x = length_x / nx
element_size_y = width_y / ny
element_size_z = height_z / nz

# Calculate the number of volume elements per layer
elements_per_layer = nx * ny

# --- Build the Layer Creation Code ---
# We will create a loop in Python to generate the text for each layer group.
layer_creation_code = ""
all_layer_names = []

for i in range(1, nz + 1):
    layer_name = f"layer{i}"
    all_layer_names.append(layer_name)

    # Calculate the start and end IDs for the elements in this layer
    start_id = (i - 1) * elements_per_layer + 1
    end_id = i * elements_per_layer
    
    # Create a list of element IDs for the Add() command
    element_ids = list(range(start_id, end_id + 1))

    # Append the Python code for this layer to our string
    layer_creation_code += f"""
{layer_name} = Mesh_1.CreateEmptyGroup( SMESH.VOLUME, '{layer_name}' )
nbAdd = {layer_name}.Add( {element_ids} )"""

# Create the string for the list of all group objects, used by GetGroups() and SetName()
all_group_names_str = ", ".join(all_layer_names)
set_name_for_layers_code = ""
for name in all_layer_names:
    set_name_for_layers_code += f"smesh.SetName({name}, '{name}')\n"


# --- Assemble the final Salome script using an f-string ---

salome_script_content = f"""
#!/usr/bin/env python

###
### This file was generated automatically by a custom Python script.
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
# sys.path.insert(0, r'path/to/your/salome/meca/folder') # Optional: Adjust if needed

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Box_1 = geompy.MakeBoxDXDYDZ({length_x}, {width_y}, {height_z})
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Box_1, 'Box_1' )

###
### SMESH component
###

import SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
Mesh_1 = smesh.Mesh(Box_1, 'Mesh_1')
Cartesian_3D = Mesh_1.BodyFitted()

# Set meshing parameters based on calculated element sizes
Body_Fitting_Parameters_1 = Cartesian_3D.SetGrid([ [ '{element_size_x}' ], [ 0, 1 ]],[ [ '{element_size_y}' ], [ 0, 1 ]],[ [ '{element_size_z}' ], [ 0, 1 ]],4,0)
isDone = Mesh_1.Compute()

# --- Create Groups for each layer ---
{layer_creation_code.strip()}

# Get all the layer groups
[ {all_group_names_str} ] = Mesh_1.GetGroups()

# --- Create a placeholder group for bottom nodes ---
# As requested, this group is created empty. You can select the nodes
# in the Salome GUI and add them to this group manually.
bottom = Mesh_1.CreateEmptyGroup( SMESH.NODE, 'bottom' )
# To add nodes later: Right-click 'bottom' -> Edit Group -> Select nodes -> Add -> Apply and Close

[ {all_group_names_str}, bottom ] = Mesh_1.GetGroups()

## Set names of Mesh objects
smesh.SetName(Cartesian_3D.GetAlgorithm(), 'Cartesian_3D')
smesh.SetName(Body_Fitting_Parameters_1, 'Body Fitting Parameters_1')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')
{set_name_for_layers_code.strip()}
smesh.SetName(bottom, 'bottom')

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

"""

# --- Write the generated script to a file ---
try:
    with open(output_filename, "w") as file:
        file.write(salome_script_content)
    print(f"Successfully created Salome script: '{output_filename}'")
    print(f" -> Dimensions: {length_x} x {width_y} x {height_z}")
    print(f" -> Divisions: {nx} (x), {ny} (y), {nz} (z)")
except IOError as e:
    print(f"Error writing to file: {e}")
