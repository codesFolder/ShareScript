# make_paraview_script.py (Version 6 - The Polished & Perfected Edition)
# This script generates a ParaView python script to automate animation creation.
# It is the definitive version, handling all known Salome naming conventions.

import os

# --- HOW TO USE AND CUSTOMIZE THIS SCRIPT IN THE FUTURE ---
#
# 1. PRIMARY USAGE:
#    - To create an animation script, you only need to edit TWO things below:
#      a) `result_key`: Change this to the result you want (e.g., 'DEPL', 'TEMP', 'VMIS').
#      b) `fixed_colormap_min`/`max`: Set the color range for your chosen result.
#
# 2. CUSTOMIZING FOR NEW RESULTS:
#    - If you have a new result type in the future, you only need to add a new entry
#      to the `RESULT_CONFIG` dictionary below.
#    - Study the existing entries ('TEMP', 'DEPL', 'SXX') to see the patterns.
#
# 3. MODIFYING NAMING RULES:
#    - If Salome changes how it names fields, the logic is in the main `for` loop
#      under the comment "DYNAMIC FIELD NAME AND TUPLE GENERATION".
#    - Read the comments there to understand how it builds the names. You can tweak
#      the f-strings (e.g., `f"{...}"`) in that section to match any new pattern.
#
# ---------------------------------------------------------------------------------

# --- USER INPUTS (Edit these for each run) ---

# 1. CHOOSE THE RESULT TO PROCESS
#    (e.g., 'TEMP', 'DEPL', 'SXX', 'SYY', 'SZZ', 'VMIS')
result_key = 'DEPL'

# 2. SET THE FIXED COLORMAP RANGE FOR YOUR CHOSEN RESULT
fixed_colormap_min = 0.0
fixed_colormap_max = 0.15

# --- THE CONFIGURATION LIBRARY (Add new results here) ---
RESULT_CONFIG = {
    # 'KEY': This is the name you use in `result_key` above.
    'TEMP': {
        'file_basename': 'ther',  # The start of the .rmed filename (ther1.rmed, ther2.rmed...).
        'field_name': 'TEMP',     # The base name of the result field inside the file.
        'component': None,        # Use `None` for SCALAR results (like temperature).
        'result_prefix': 'res'    # The text that comes before the number in the field name.
    },
    'DEPL': {
        'file_basename': 'mec',
        'field_name': 'DEPL',
        'component': 'Magnitude', # Use 'Magnitude' for VECTOR results (like displacement).
        'result_prefix': 'res'
    },
    'SXX': {
        'file_basename': 'mec',
        'field_name': 'SIGM_NOEU', # The base name for the TENSOR result (stress).
        'component': 'SIXX',      # The specific component of the tensor to visualize.
        'result_prefix': 'stress'
    },
    # ... other stress components ...
    'SYY': {'file_basename': 'mec', 'field_name': 'SIGM_NOEU', 'component': 'SIYY', 'result_prefix': 'stress'},
    'SZZ': {'file_basename': 'mec', 'field_name': 'SIGM_NOEU', 'component': 'SIZZ', 'result_prefix': 'stress'},
    'VMIS': {
        'file_basename': 'mec',
        'field_name': 'SIEQ_NOEU',
        'component': 'VMIS',
        'result_prefix': 'stress'
    }
}
# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC (Fully automatic from here) ---

try:
    config = RESULT_CONFIG[result_key]
except KeyError:
    print(f"Error: Invalid result_key '{result_key}'. Please choose from {list(RESULT_CONFIG.keys())}")
    exit()

# Other Parameters
num_files = 20
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

loading_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{config['file_basename']}{i}_reader"
    file_path = os.path.join(results_path, f"{config['file_basename']}{i}.rmed").replace("\\", "/")
    loading_code += f"\n{reader_var} = MEDReader(registrationName='{config['file_basename']}{i}.rmed', FileNames=['{file_path}'])"

processing_loop_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{config['file_basename']}{i}_reader"
    display_var = f"{reader_var}_display"
    
    # --- DYNAMIC FIELD NAME AND TUPLE GENERATION ---
    # This is the core logic that adapts to different naming rules.
    # If you ever need to change a naming rule, this is the place to do it.

    if config['component'] is None:  # SCALAR CASE (e.g., 'TEMP')
        # Rule: Field name number rolls over every 10 files (resther1TEMP, resther2TEMP...).
        field_num_in_name = i if i < 10 else i // 10
        full_field_name = f"{config['result_prefix']}{config['file_basename']}{field_num_in_name}{config['field_name']}"
        color_by_tuple = f"('POINTS', '{full_field_name}')"
        
    else:  # VECTOR/TENSOR CASE (e.g., 'DEPL', 'SXX', 'VMIS')
        if config['field_name'] == 'DEPL': # Special handling for Displacement
            # Rule for DEPL: Underscore disappears for layers >= 10.
            # Name format: res + mec + number + [_] + DEPL
            if i < 10:
                # FIX: Added config['file_basename'] to correctly form 'resmec1_DEPL'
                full_field_name = f"{config['result_prefix']}{config['file_basename']}{i}_{config['field_name']}"
            else: # i >= 10
                full_field_name = f"{config['result_prefix']}{config['file_basename']}{i}{config['field_name']}"
        
        else: # Generic handling for other Tensors (Stress)
            # Rule for STRESS: Underscore disappears for layers >= 10.
            # Name format: stress + number + [_] + SIGM_NOEU
            if i < 10:
                full_field_name = f"{config['result_prefix']}{i}_{config['field_name']}"
            else: # i >= 10
                full_field_name = f"{config['result_prefix']}{i}{config['field_name']}"
        
        # Finally, build the tuple for the ColorBy command
        color_by_tuple = f"('POINTS', '{full_field_name}', '{config['component']}')"
        
    start_frame = (i - 1) * timesteps_per_file
    end_frame = i * timesteps_per_file - 1
    animation_output_path = os.path.join(results_path, f"{animation_base_name}_{i}.ogv").replace("\\", "/")

    processing_loop_code += f"""
# --- Processing and Animating File {i} for {result_key} ---
print("Processing file: {config['file_basename']}{i}.rmed | Field: {full_field_name}")
SetActiveSource({reader_var})
{display_var} = Show({reader_var}, renderView1, 'UnstructuredGridRepresentation')
{display_var}.Representation = 'Surface'
"""

    if i > 1:
        prev_reader_var = f"{config['file_basename']}{i-1}_reader"
        processing_loop_code += f"Hide({prev_reader_var}, renderView1)\n"
    
    processing_loop_code += f"""
ColorBy({display_var}, {color_by_tuple})
lut = GetColorTransferFunction('{full_field_name}')
pwf = GetOpacityTransferFunction('{full_field_name}')
lut.ApplyPreset('{colormap_preset}', True)
lut.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
pwf.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
{display_var}.SetScalarBarVisibility(renderView1, {show_legend_in_animation})
renderView1.Update()
SaveAnimation('{animation_output_path}', renderView1, ImageResolution={image_resolution},
    FrameRate={frame_rate},
    FrameWindow=[{start_frame}, {end_frame}])
"""

# --- Assemble the final ParaView script ---
paraview_script_content = f"""
###
### This file was generated by the PERFECTED Python script (v6).
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
    print(f" -> It will process {num_files} files for the '{result_key}' result.")
except IOError as e:
    print(f"Error writing to file: {e}")
