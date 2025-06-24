# make_paraview_script.py (Version 4 - The Ultimate Edition)
# This script generates a ParaView python script to automate animation creation
# for SCALAR, VECTOR, and TENSOR results by simply changing one variable.
import os

# --- USER INPUTS ---
# --- You only need to edit the 'result_key' and the min/max values! ---

# 1. CHOOSE THE RESULT TO PROCESS
# Just pick one of the keys from the RESULT_CONFIG library below.
# Examples: 'TEMP', 'DEPL', 'SXX', 'SYY', 'SZZ', 'SXY', 'SYZ', 'SXZ', 'VMIS'
result_key = 'VMIS'

# 2. SET THE FIXED COLORMAP RANGE FOR YOUR CHOSEN RESULT
# Example for Von Mises Stress (VMIS):
fixed_colormap_min = 0.0
fixed_colormap_max = 1000.0
# Example for Stress XX (SXX):
# fixed_colormap_min = -200.0
# fixed_colormap_max = 2500.0

# --- THE CONFIGURATION LIBRARY (No need to edit this part) ---
# This library stores all the unique settings for each result type.
RESULT_CONFIG = {
    'TEMP': {
        'file_basename': 'ther',  # Base name of the .rmed files (ther1, ther2...)
        'field_name': 'TEMP',     # Field name inside the .rmed file
        'component': None,        # None indicates this is a SCALAR result
        'result_prefix': 'res'    # 'res' + 'ther1' + 'TEMP' -> resther1TEMP
    },
    'DEPL': {
        'file_basename': 'mec',
        'field_name': 'DEPL',
        'component': 'Magnitude', # This is a VECTOR result, show its Magnitude
        'result_prefix': 'res'    # 'res' + 'mec1' + '_DEPL' -> resmec1_DEPL
    },
    'SXX': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU', # The Stress tensor field
        'component': 'SIXX',      # The specific component to show
        'result_prefix': 'stress' # 'stress' + '1' + '_SIGM_NOEU' -> stress1_SIGM_NOEU
    },
    'SYY': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU',
        'component': 'SIYY',
        'result_prefix': 'stress'
    },
    'SZZ': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU',
        'component': 'SIZZ',
        'result_prefix': 'stress'
    },
    'SXY': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU',
        'component': 'SIXY', # Note: Paraview often uses SXY and SIXY interchangeably
        'result_prefix': 'stress'
    },
    'SYZ': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU',
        'component': 'SIYZ',
        'result_prefix': 'stress'
    },
    'SXZ': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU',
        'component': 'SIXZ',
        'result_prefix': 'stress'
    },
    'VMIS': {
        'file_basename': 'mec',
        'field_name': 'SIEQ_NOEU', # The Von Mises equivalent stress field
        'component': 'VMIS',      # The von mises component
        'result_prefix': 'stress' # 'stress' + '1' + '_SIEQ_NOEU' -> stress1_SIEQ_NOEU
    }
}
# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC (Fully automatic from here) ---

# Retrieve the configuration for the chosen result
try:
    config = RESULT_CONFIG[result_key]
except KeyError:
    print(f"Error: Invalid result_key '{result_key}'. Please choose from {list(RESULT_CONFIG.keys())}")
    exit()

# Other Parameters (can be customized if needed)
num_files = 3
results_path = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run"
animation_base_name = f"animation_{result_key}"
output_filename = f"generated_paraview_script_{result_key}.py"
colormap_preset = "Rainbow Uniform"
show_legend_in_animation = False
frame_rate = 2
timesteps_per_file = 18
image_resolution = [1507, 756]
camera_position = [11.06857794191841, -39.664396099178866, 26.03454514364917]
camera_focal_point = [10.0, 10.0, 1.9999999999999616]
camera_view_up = [-0.05134727680585449, 0.4341406562705134, 0.8993805355563523]
camera_parallel_scale = 14.282856857085696

# Generate code for loading all MED files
loading_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{config['file_basename']}{i}_reader"
    file_path = os.path.join(results_path, f"{config['file_basename']}{i}.rmed").replace("\\", "/")
    loading_code += f"""
{reader_var} = MEDReader(registrationName='{config['file_basename']}{i}.rmed', FileNames=['{file_path}'])
"""

# Generate the main processing loop
processing_loop_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{config['file_basename']}{i}_reader"
    display_var = f"{reader_var}_display"
    
    # Dynamically build the result field name and ColorBy command tuple
    if config['component'] is None: # SCALAR CASE (e.g., TEMP)
        full_field_name = f"{config['result_prefix']}{config['file_basename']}{i}{config['field_name']}"
        color_by_tuple = f"('POINTS', '{full_field_name}')"
    else: # VECTOR/TENSOR CASE (e.g., DEPL, SXX, VMIS)
        full_field_name = f"{config['result_prefix']}{i}_{config['field_name']}"
        color_by_tuple = f"('POINTS', '{full_field_name}', '{config['component']}')"
        
    start_frame = (i - 1) * timesteps_per_file
    end_frame = i * timesteps_per_file - 1
    animation_output_path = os.path.join(results_path, f"{animation_base_name}_{i}.ogv").replace("\\", "/")

    processing_loop_code += f"""
# --- Processing and Animating File {i} for {result_key} ---
print("Processing file: {config['file_basename']}{i}.rmed for {result_key}")
SetActiveSource({reader_var})
{display_var} = Show({reader_var}, renderView1, 'UnstructuredGridRepresentation')
{display_var}.Representation = 'Surface'
"""

    if i > 1:
        prev_reader_var = f"{config['file_basename']}{i-1}_reader"
        processing_loop_code += f"Hide({prev_reader_var}, renderView1)\n"
    
    processing_loop_code += f"""
# Set scalar coloring using the correct format for {result_key}
ColorBy({display_var}, {color_by_tuple})

# Apply a FIXED color scale
lut = GetColorTransferFunction('{full_field_name}')
pwf = GetOpacityTransferFunction('{full_field_name}')
lut.ApplyPreset('{colormap_preset}', True)
lut.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
pwf.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})

# Set legend visibility
{display_var}.SetScalarBarVisibility(renderView1, {show_legend_in_animation})

# Update view and save animation
renderView1.Update()
print(f"Saving animation to: {animation_output_path}")
SaveAnimation('{animation_output_path}', renderView1, ImageResolution={image_resolution},
    FrameRate={frame_rate},
    FrameWindow=[{start_frame}, {end_frame}])
"""

# --- Assemble the final ParaView script ---

paraview_script_content = f"""
###
### This file was generated automatically by the ULTIMATE Python script.
### Animation for: {result_key}
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
renderView1.CameraPosition = {camera_position}
renderView1.CameraFocalPoint = {camera_focal_point}
renderView1.CameraViewUp = {camera_view_up}
renderView1.CameraParallelScale = {camera_parallel_scale}
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

# --- Loop through each result file to process and save animation ---
{processing_loop_code.strip()}

print("\\nAutomation for {result_key} finished successfully!")
"""

# --- Write the generated script to a file ---
try:
    with open(output_filename, "w") as file:
        file.write(paraview_script_content)
    print(f"Successfully created ParaView script: '{output_filename}'")
    print(f" -> It will process files for the '{result_key}' result.")
except IOError as e:
    print(f"Error writing to file: {e}")
