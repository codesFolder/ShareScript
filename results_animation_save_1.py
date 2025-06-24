# make_paraview_script.py
# This script generates a ParaView python script to automate animation creation.
import os

# --- USER INPUTS ---
# --- You can change these values to define your automation ---

# 1. File and Path Parameters
num_files = 5  # Total number of result files to process (e.g., 100 for 100 layers)
# IMPORTANT: Use forward slashes '/' for paths for better cross-platform compatibility.
results_path = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run"
result_base_name = "mec"  # The script will look for mec1.rmed, mec2.rmed, etc.
animation_base_name = "animation_layer" # The script will save animation_layer1.ogv, etc.

# 2. Visualization Parameters
param_to_visualize = "DEPL" # The result field to visualize (e.g., "DEPL", "TEMP")
colormap_preset = "Rainbow Uniform" # Name of the ParaView colormap preset

# 3. Animation Parameters
frame_rate = 1
timesteps_per_file = 18 # The number of time steps contained IN EACH individual result file. 
                        # In your example, file 1 (0 to 17s) has 18 steps.

# 4. View and Camera Parameters (Copied from your trace)
image_resolution = [1507, 756]
camera_position = [-6.199558541584951, -43.822811095266864, 25.07184498694432]
camera_focal_point = [10.0, 10.0, 5.999999999999982]
camera_view_up = [-0.003982202060091894, 0.33505850691906064, 0.942188908344777]
camera_parallel_scale = 15.362291495737209

# 5. Output file name
output_filename = "generated_paraview_script.py"

# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC ---

# Generate the block of code for loading all MED files
loading_code = ""
reader_vars = []
for i in range(1, num_files + 1):
    reader_var = f"{result_base_name}{i}_reader"
    reader_vars.append(reader_var)
    file_path = os.path.join(results_path, f"{result_base_name}{i}.rmed").replace("\\", "/")
    
    loading_code += f"""
# Create a new 'MED Reader' for result {i}
{reader_var} = MEDReader(registrationName='{result_base_name}{i}.rmed', FileNames=['{file_path}'])
"""

# Generate the main processing loop for each file
processing_loop_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{result_base_name}{i}_reader"
    display_var = f"{reader_var}_display"
    
    # The result field name inside the .rmed file (e.g., 'resmec1_DEPL')
    # Note: ParaView often prefixes the result name with 'res'. We will assume this pattern.
    # If your files name it differently (e.g. just 'DEPL'), you may need to adjust this.
    result_field_name = f"res{result_base_name}{i}_{param_to_visualize}"
    
    # Calculate the time window for this animation clip
    start_frame = (i - 1) * timesteps_per_file
    end_frame = i * timesteps_per_file - 1
    
    # Path for the output animation file
    animation_output_path = os.path.join(results_path, f"{animation_base_name}{i}.ogv").replace("\\", "/")

    processing_loop_code += f"""
# --- Processing and Animating File {i} ---
print("Processing file: {result_base_name}{i}.rmed")
SetActiveSource({reader_var})
{display_var} = Show({reader_var}, renderView1, 'UnstructuredGridRepresentation')
{display_var}.Representation = 'Surface'
"""

    # Add code to hide the previous result file
    if i > 1:
        prev_reader_var = f"{result_base_name}{i-1}_reader"
        processing_loop_code += f"""
# Hide the previous data source
Hide({prev_reader_var}, renderView1)
"""
    
    processing_loop_code += f"""
# Set scalar coloring
ColorBy({display_var}, ('POINTS', '{result_field_name}', 'Magnitude'))

# Rescale color and/or opacity maps used to include current data range
{display_var}.RescaleTransferFunctionToDataRange(True, False)

# Show color bar/color legend
{display_var}.SetScalarBarVisibility(renderView1, True)

# Get color transfer function/color map and apply preset
lut = GetColorTransferFunction('{result_field_name}')
lut.ApplyPreset('{colormap_preset}', True)

# Update view to apply changes
renderView1.Update()

# Save the animation for the current time window
print(f"Saving animation to: {animation_output_path}")
SaveAnimation('{animation_output_path}', renderView1, ImageResolution={image_resolution},
    FrameRate={frame_rate},
    FrameWindow=[{start_frame}, {end_frame}])
"""

# --- Assemble the final ParaView script using an f-string ---

paraview_script_content = f"""
###
### This file was generated automatically by a custom Python script.
###

import pvsimple
pvsimple.ShowParaviewView()

#### import the simple module from the paraview
from pvsimple import *

#### disable automatic camera reset on 'Show'
pvsimple._DisableFirstRenderCameraReset()

# --- Load all result files ---
{loading_code.strip()}

# --- Initial Scene Setup ---
# Get active view and layout
renderView1 = GetActiveViewOrCreate('RenderView')
layout1 = GetLayout()

# Set layout size
layout1.SetSize({image_resolution[0]}, {image_resolution[1]})

# Set consistent camera placement for all animations
renderView1.CameraPosition = {camera_position}
renderView1.CameraFocalPoint = {camera_focal_point}
renderView1.CameraViewUp = {camera_view_up}
renderView1.CameraParallelScale = {camera_parallel_scale}

# get animation scene and time-keeper
animationScene1 = GetAnimationScene()
timeKeeper1 = GetTimeKeeper()

# This is important: it makes ParaView aware of all timesteps from all files
animationScene1.UpdateAnimationUsingDataTimeSteps()

# --- Loop through each result file to process and save animation ---
{processing_loop_code.strip()}


print("\\nAutomation finished successfully!")
"""

# --- Write the generated script to a file ---
try:
    with open(output_filename, "w") as file:
        file.write(paraview_script_content)
    print(f"Successfully created ParaView script: '{output_filename}'")
    print(f" -> It will process {num_files} files from the path: '{results_path}'")
except IOError as e:
    print(f"Error writing to file: {e}")
