# make_paraview_script.py (Version 9 - The Final Frame Edition)
# This script generates a stable, presentation-quality ParaView animation script.
# This version perfects the camera controls, ensuring custom views are not overridden.

import os

# --- HOW TO USE AND CUSTOMIZE THIS SCRIPT ---
# 1. PRIMARY USAGE: Edit the settings in the "USER INPUTS" section below.
# 2. CUSTOMIZING NEW RESULTS: Add new entries to the `RESULT_CONFIG` dictionary.
# 3. MODIFYING NAMING RULES: The core logic is in the main `for` loop under
#    "DYNAMIC FIELD NAME AND TUPLE GENERATION".
# ---------------------------------------------------------------------------------

# --- USER INPUTS (Edit these settings for each run) ---

# --- 1. CORE SETTINGS (ALWAYS EDIT) ---
result_key = 'DEPL'

# --- 2. CAMERA SETTINGS ---
camera_mode = 'custom' # 'standard' or 'custom'

# Option A: For camera_mode = 'standard'
standard_camera_view = 'NegativeX' # 'PositiveX', 'NegativeX', etc.

# Option B: For camera_mode = 'custom'
# Paste the camera block from your ParaView Python trace here.
custom_camera_block = '''
# current camera placement for renderView1
renderView1.CameraPosition = [55.175156121063246, 10.0, 9.999999999999893]
renderView1.CameraFocalPoint = [0.5, 10.0, 9.999999999999893]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = 14.150971698084831
'''

# --- 3. COLORMAP & LEGEND SETTINGS ---
# A) Colormap
colormap_preset = 'Turbo'
fixed_colormap_min = 0.0
fixed_colormap_max = 0.15
colormap_table_values = 256

# B) Legend (Scalar Bar)
show_legend = True
legend_title = 'Displacement (mm)'
legend_number_format = '%-#6.3f' # '%.2e' for scientific, '%-#6.2f' for decimal (2 places)

# --- 4. GENERAL FILE & ANIMATION SETTINGS ---
num_files = 20
results_path = "C:/Users/DELL/Downloads/v2024/salome_meca/lpbf_run"
animation_base_name = f"animation_{result_key}"
output_filename = f"generated_paraview_script_{result_key}.py"
frame_rate = 10
timesteps_per_file = 18
image_resolution = [1920, 1080]

# --- 5. CONFIGURATION LIBRARY (ADVANCED: Add new results here) ---
RESULT_CONFIG = { 'TEMP': {'file_basename': 'ther', 'field_name': 'TEMP', 'component': None, 'result_prefix': 'res'}, 'DEPL': {'file_basename': 'mec', 'field_name': 'DEPL', 'component': 'Magnitude', 'result_prefix': 'res'}, 'SXX': {'file_basename': 'mec', 'field_name': 'SIGM_NOEU', 'component': 'SIXX', 'result_prefix': 'stress'}, 'SYY': {'file_basename': 'mec', 'field_name': 'SIGM_NOEU', 'component': 'SIYY', 'result_prefix': 'stress'}, 'SZZ': {'file_basename': 'mec', 'field_name': 'SIGM_NOEU', 'component': 'SIZZ', 'result_prefix': 'stress'}, 'VMIS': {'file_basename': 'mec', 'field_name': 'SIEQ_NOEU', 'component': 'VMIS', 'result_prefix': 'stress'} }
# --- END OF USER INPUTS ---


# --- SCRIPT GENERATION LOGIC (Fully automatic from here) ---

try:
    config = RESULT_CONFIG[result_key]
except KeyError:
    print(f"Error: Invalid result_key '{result_key}'. Please choose from {list(RESULT_CONFIG.keys())}")
    exit()

# Generate camera setup code based on user's choice
if camera_mode.lower() == 'standard':
    # For standard views, we SET the angle and then RESET the zoom to fit the data.
    camera_setup_code = f"""
# Set camera to a standard view and then frame the data
renderView1.ResetActiveCameraTo{standard_camera_view}()
renderView1.ResetCamera(False) # This is NECESSARY for standard views to frame the object
"""
elif camera_mode.lower() == 'custom':
    # For custom views, the block contains all info, including zoom. No ResetCamera is needed.
    camera_setup_code = f"""
# Apply the user's custom camera block directly.
# No ResetCamera() is needed here, as the block includes the precise zoom (ParallelScale).
{custom_camera_block.strip()}
"""
else:
    camera_setup_code = "# No camera mode selected, using default view."

loading_code = ""
for i in range(1, num_files + 1):
    reader_var = f"{config['file_basename']}{i}_reader"
    file_path = os.path.join(results_path, f"{config['file_basename']}{i}.rmed").replace("\\", "/")
    loading_code += f"\n{reader_var} = MEDReader(registrationName='{config['file_basename']}{i}.rmed', FileNames=['{file_path}'])"

processing_loop_code = ""
for i in range(1, num_files + 1):
    reader_var, display_var = f"{config['file_basename']}{i}_reader", f"{reader_var}_display"
    if config['component'] is None: full_field_name, color_by_tuple = (f"{config['result_prefix']}{config['file_basename']}{i if i < 10 else i // 10}{config['field_name']}", f"('POINTS', '{f'{config['result_prefix']}{config['file_basename']}{i if i < 10 else i // 10}{config['field_name']}'}')")
    else:
        if config['field_name'] == 'DEPL': full_field_name = f"{config['result_prefix']}{config['file_basename']}{i}_{config['field_name']}" if i < 10 else f"{config['result_prefix']}{config['file_basename']}{i}{config['field_name']}"
        else: full_field_name = f"{config['result_prefix']}{i}_{config['field_name']}" if i < 10 else f"{config['result_prefix']}{i}{config['field_name']}"
        color_by_tuple = f"('POINTS', '{full_field_name}', '{config['component']}')"
    start_frame, end_frame = (i - 1) * timesteps_per_file, i * timesteps_per_file - 1
    animation_output_path = os.path.join(results_path, f"{animation_base_name}_{i}.ogv").replace("\\", "/")
    legend_code = ""
    if show_legend:
        legend_code = f"color_bar = GetScalarBar(lut, renderView1)\ncolor_bar.Title = '{legend_title}'\ncolor_bar.ComponentTitle = ''\ncolor_bar.LabelFormat = '{legend_number_format}'\ncolor_bar.Visibility = 1"
    else:
        legend_code = f"{display_var}.SetScalarBarVisibility(renderView1, False)"
    processing_loop_code += f"""
# --- Processing and Animating File {i} for {result_key} ---
print("Processing file: {config['file_basename']}{i}.rmed | Field: {full_field_name}")
SetActiveSource({reader_var})
{display_var} = Show({reader_var}, renderView1, 'UnstructuredGridRepresentation')
{display_var}.Representation = 'Surface'
{'Hide(' + config['file_basename'] + str(i-1) + '_reader, renderView1)' if i > 1 else ''}
ColorBy({display_var}, {color_by_tuple})
lut = GetColorTransferFunction('{full_field_name}')
pwf = GetOpacityTransferFunction('{full_field_name}')
lut.ApplyPreset('{colormap_preset}', True)
lut.NumberOfTableValues = {colormap_table_values}
lut.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
pwf.RescaleTransferFunction({fixed_colormap_min}, {fixed_colormap_max})
{legend_code.strip()}
renderView1.Update()
SaveAnimation('{animation_output_path}', renderView1, ImageResolution={image_resolution}, FrameRate={frame_rate}, FrameWindow=[{start_frame}, {end_frame}])
"""

paraview_script_content = f"""
###
### This file was generated by the Final Frame Edition Python script (v9).
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
animationScene1 = GetAnimationScene()
animationScene1.UpdateAnimationUsingDataTimeSteps()

# --- Set Camera Position ---
# The camera logic is now applied correctly based on the selected mode.
{camera_setup_code.strip()}

# --- Loop through each result file to process and save animation ---
{processing_loop_code.strip()}
print("\\nAutomation for {result_key} finished successfully!")
"""

try:
    with open(output_filename, "w") as file:
        file.write(paraview_script_content)
    print(f"Successfully created ParaView script: '{output_filename}'")
    print(f" -> It will process {num_files} files for the '{result_key}' result.")
except IOError as e:
    print(f"Error writing to file: {e}")
