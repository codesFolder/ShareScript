# make_paraview_script.py (Version 2)
# This script generates a ParaView python script to automate animation creation
# with a FIXED color scale and optional legend.
import os

# --- USER INPUTS ---
# --- You can change these values to define your automation ---

# 1. File and Path Parameters
num_files = 5  # Total number of result files to process
# IMPORTANT: Use forward slashes '/' for paths.
results_path = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run"
result_base_name = "mec"  # Will look for mec1.rmed, mec2.rmed, etc.
animation_base_name = "animation_layer" # Will save animation_layer1.ogv, etc.

# 2. Visualization Parameters
param_to_visualize = "DEPL" # Result field (e.g., "DEPL", "TEMP")
colormap_preset = "Rainbow Uniform"

# 3. NEW! Colormap and Legend Control
# Set the min and max for the color scale. This will be applied to ALL animations.
fixed_colormap_min = 0.0
fixed_colormap_max = 0.2
# Set to False to hide the legend/color bar in the saved animations.
show_legend_in_animation = False

# 4. Animation Parameters
frame_rate = 3
timesteps_per_file = 18 # Number of time steps IN EACH individual result file

# 5. View and Camera Parameters (Copied from your trace)
image_resolution = [1507, 756]
camera_position = [3.1871728696380877, -42.19736772419114, 18.564227966722942]
camera_focal_point = [10.0, 10.000000000000002, 1.9999999999999631]
camera_view_up = [0.03140228511734646, 0.2985984056925679, 0.9538620909792282]
camera_parallel_scale = 14.282856857085696

# 6. Output file name
output_filename = "generated_paraview_script_fixed_scale.py"

# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC ---

# Generate the block of code for loading all MED files
loading_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{result_base_name}{i}_reader"
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
    result_field_name = f"res{result_base_name}{i}_{param_to_visualize}"
    start_frame = (i - 1) * timesteps_per_file
    end_frame = i * timesteps_per_file - 1
    animation_output_path = os.path.join(results_path, f"{animation_base_name}{i}.ogv").replace("\\", "/")

    processing_loop_code += f"""
# --- Processing and Animating File {i} ---
print("Processing file: {result_base_name}{i}.rmed")
SetActiveSource({reader_var})
{display_var} = Show({reader_var}, renderView1, 'UnstructuredGridRepresentation')
{display_var}.Representation = 'Surface'
"""

    if i > 1:
        prev_reader_var = f"{result_base_name}{i-1}_reader"
        processing_loop_code += f"Hide({prev_reader_var}, renderView1)\n"
    
    processing_loop_code += f"""
# Set scalar coloring
ColorBy({display_var}, ('POINTS', '{result_field_name}', 'Magnitude'))

# --- Apply a FIXED color scale for visual consistency ---
# Get the color and opacity functions for the current result
lut = GetColorTransferFunction('{result_field_name}')
pwf = GetOpacityTransferFunction('{result_field_name}')

# Apply the preset colormap style
lut.ApplyPreset('{colormap_preset}', True)

# **IMPORTANT**: Rescale the color and opacity maps to the fixed min/max values
lut.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
pwf.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})

# Set the visibility of the color bar/legend for the animation
{display_var}.SetScalarBarVisibility(renderView1, {show_legend_in_animation})

# Update view to apply all changes
renderView1.Update()

# Save the animation for the current time window
print(f"Saving animation to: {animation_output_path}")
SaveAnimation('{animation_output_path}', renderView1, ImageResolution={image_resolution},
    FrameRate={frame_rate},
    FrameWindow=[{start_frame}, {end_frame}])
"""

# --- Assemble the final ParaView script ---

paraview_script_content = f"""
###
### This file was generated automatically by a custom Python script.
### Creates animations with a fixed color scale and hidden legend.
###

import pvsimple
pvsimple.ShowParaviewView()
from pvsimple import *

pvsimple._DisableFirstRenderCameraReset()

# --- Load all result files ---
{loading_code.strip()}

# --- Initial Scene Setup ---
renderView1 = GetActiveViewOrCreate('RenderView')
layout1 = GetLayout()
layout1.SetSize({image_resolution[0]}, {image_resolution[1]})

# Set consistent camera placement for all animations
renderView1.CameraPosition = {camera_position}
renderView1.CameraFocalPoint = {camera_focal_point}
renderView1.CameraViewUp = {camera_view_up}
renderView1.CameraParallelScale = {camera_parallel_scale}

# Make ParaView aware of all timesteps from all loaded files
animationScene1 = GetAnimationScene()
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
    print(f" -> Using FIXED color scale: Min={fixed_colormap_min}, Max={fixed_colormap_max}")
    print(f" -> Legend visibility in animation: {show_legend_in_animation}")
except IOError as e:
    print(f"Error writing to file: {e}")
