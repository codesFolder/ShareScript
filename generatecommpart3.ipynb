# ==============================================================================
#      Code_Aster Command File Generator for N-Layer Cooling Simulation
# ==============================================================================
#
# This script generates a .comm file for a multi-layer thermomechanical
# simulation based on an initial temperature cooling model. Each new layer
# is activated at a high temperature and then cools down.
#
# It "unrolls" the loop by generating a distinct block of commands for each
# layer, including the necessary state transfer (temperature and displacement)
# from the previous step.
#
# --- HOW TO USE ---
# 1. Set the parameters in the "USER-DEFINED PARAMETERS" section below.
# 2. Run the script: python generate_cooling_comm.py
# 3. Use the generated file in your Code_Aster study.
#
# --- IMPORTANT ---
# This script faithfully reproduces the logic of the provided 2-layer code.
# If run with num_layers = 2, it will generate a functionally identical file.
# The only difference will be some variable names, which are generated
# sequentially for clarity.
#
# ==============================================================================

# ------------------------------------------------------------------------------
# USER-DEFINED PARAMETERS
# ------------------------------------------------------------------------------

# Total number of layers to simulate
num_layers = 2

# Output filename for the generated command file
output_filename = "lpbf_n_layer_cooling.comm"

# --- Process Parameters (must match your simulation) ---
time_per_layer = 0.003  # Cooling time for one layer (s)
initial_melt_temp = 1605.0 # Temperature of a newly activated layer (K)
baseplate_temp = 300.0   # Constant temperature of the bottom plate (K)

# --- Output Units ---
# The original code uses a simple incremental pattern (81, 91, 82, 92, ...)
# We will follow this: thermal unit = 80+i, mechanical unit = 90+i
base_ther_unit = 80
base_meca_unit = 90

# ------------------------------------------------------------------------------

def generate_comm_file():
    """Main function to generate the .comm file."""

    # Use a list to build the file content as strings
    comm_file_content = []

    def add_line(text):
        """Helper to add a line to the content list."""
        comm_file_content.append(text)

    # ==========================================================================
    # 1. Preamble and One-Time Definitions
    # ==========================================================================
    add_line("DEBUT(LANG='FR')\n")
    add_line("mesh = LIRE_MAILLAGE(FORMAT='MED', UNITE=7)\n")

    # --- Material Properties (copied exactly from the original) ---
    add_line("# --- Material and Function Definitions ---")
    add_line("kappa1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(430.0, 5.957, 1270.0, 17.0, 1383.0, 19.87, 1799.0, 21.9, 1801.0, 28.8, 2666.0, 42.2))")
    add_line("rhocp1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(293.0, 2.435, 873.0, 2.958, 1799.0, 3.149, 1801.0, 4.616, 2073.0, 4.532, 2573.0, 4.278))")
    add_line("youngmo1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(300.0, 107000.0, 600.0, 99000.0, 800.0, 90000.0, 1000.0, 80000.0, 1200.0, 70000.0))")
    add_line("poiss1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(300.0, 0.32, 600.0, 0.31, 800.0, 0.3, 1000.0, 0.29, 1200.0, 0.28))")
    add_line("rho1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(293.0, 4.15e-06, 973.0, 4.35e-06, 1799.0, 4.15e-06, 1801.0, 4.1e-06, 2073.0, 4e-06, 2573.0, 3.8e-06))")
    add_line("alpha1 = DEFI_FONCTION(NOM_PARA='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE=(300.0, 8.9e-06, 600.0, 9.2e-06, 800.0, 9.5e-06, 1000.0, 9.8e-06, 1200.0, 1e-05))")
    add_line("mater1 = DEFI_MATERIAU(ECRO_LINE=_F(D_SIGM_EPSI=3000.0, EPSI_LIM=0.01, SY=950.0), ELAS_FO=_F(ALPHA=alpha1, E=youngmo1, NU=poiss1, RHO=rho1, TEMP_DEF_ALPHA=300.0), THER_NL=_F(LAMBDA=kappa1, RHO_CP=rhocp1))\n")

    # ==========================================================================
    # 2. Loop to Generate Commands for Each Layer
    # ==========================================================================
    for i in range(1, num_layers + 1):
        add_line(f"\n# --- Layer {i} --- #\n")

        # --- Dynamic variable names ---
        active_groups_list = [f"'layer{j}'" for j in range(1, i + 1)]
        active_groups_str = f"({', '.join(active_groups_list)}, )"
        
        # Names for current step
        model_ther = f"model{i}"
        model_meca = f"modmeca{i}"
        mat_ther_assign = f"assth{i}"
        list_inst = f"listr{i}"
        bottemp_load = f"bottemp{i}"
        fixmec_load = f"fixmec{i}"
        temp_init_new_layer = f"tmp{i}"
        res_ther = f"resther{i}"
        mat_meca_assign = f"assmec{i}"
        res_meca = f"resmec{i}"
        stress = f"stress{i}"

        # --- Variables from previous step (i-1) ---
        prev_res_ther = f"resther{i-1}"
        prev_res_meca = f"resmec{i-1}"

        # --- Time definition for current layer ---
        time_start = (i - 1) * time_per_layer
        time_end = i * time_per_layer

        # --- AFFE_MODELE and AFFE_MATERIAU ---
        add_line(f"{model_ther} = AFFE_MODELE(MAILLAGE=mesh, AFFE=_F(GROUP_MA={active_groups_str}, PHENOMENE='THERMIQUE', MODELISATION='3D'))")
        add_line(f"{model_meca} = AFFE_MODELE(MAILLAGE=mesh, AFFE=_F(GROUP_MA={active_groups_str}, PHENOMENE='MECANIQUE', MODELISATION='3D'))")
        add_line(f"{mat_ther_assign} = AFFE_MATERIAU(MAILLAGE=mesh, AFFE=_F(GROUP_MA={active_groups_str}, MATER=mater1))\n")

        # --- Time list and Loads ---
        add_line(f"{list_inst} = DEFI_LIST_REEL(DEBUT={time_start}, INTERVALLE=_F(JUSQU_A={time_end}, PAS=1e-5))")
        add_line(f"{bottemp_load} = AFFE_CHAR_THER(MODELE={model_ther}, TEMP_IMPO=_F(GROUP_MA=('bottom', ), TEMP={baseplate_temp}))")
        add_line(f"{fixmec_load} = AFFE_CHAR_MECA(MODELE={model_meca}, DDL_IMPO=_F(BLOCAGE=('DEPLACEMENT', ), GROUP_MA=('bottom', )))\n")
        
        # --- Create high-temperature field for the newly activated layer ---
        add_line(f"# Initial temperature field for the new layer")
        add_line(f"{temp_init_new_layer} = CREA_CHAMP(MAILLAGE=mesh, OPERATION='AFFE', TYPE_CHAM='NOEU_TEMP_R', AFFE=_F(GROUP_MA=('layer{i}', ), NOM_CMP=('TEMP', ), VALE=({initial_melt_temp}, )))\n")

        # --- Prepare ETAT_INIT for thermal and mechanical steps ---
        if i == 1:
            # For the first layer, the initial state is simply the hot temperature field
            etat_init_ther_str = f"ETAT_INIT=_F(CHAM_NO={temp_init_new_layer}),"
            etat_init_meca_str = ""
        else: # For layers > 1, we must transfer the state from the previous step
            add_line(f"# --- State Transfer from Layer {i-1} to Layer {i} ---")
            
            # --- Thermal State Transfer ---
            # 1. Extract final temperature from previous step
            # 2. Assemble with the new hot layer to create the initial thermal state
            temp_ext = f"tmpext{i-1}"
            temp_init_combined = f"fieldini{i}"
            prev_active_groups_list = [f"'layer{j}'" for j in range(1, i)]
            prev_active_groups_str = f"({', '.join(prev_active_groups_list)}, )"
            add_line(f"{temp_ext} = CREA_CHAMP(OPERATION='EXTR', TYPE_CHAM='NOEU_TEMP_R', RESULTAT={prev_res_ther}, INST={time_start}, NOM_CHAM='TEMP')")
            add_line(f"{temp_init_combined} = CREA_CHAMP(MAILLAGE=mesh, OPERATION='ASSE', TYPE_CHAM='NOEU_TEMP_R', ASSE=(_F(CHAM_GD={temp_ext}, GROUP_MA={prev_active_groups_str}), _F(CHAM_GD={temp_init_new_layer}, GROUP_MA=('layer{i}', ))))")
            etat_init_ther_str = f"ETAT_INIT=_F(CHAM_NO={temp_init_combined}),"
            
            # --- Mechanical State Transfer ---
            # 1. Create zero displacement field for the new layer
            # 2. Extract final displacement from previous step
            # 3. Assemble them to create the initial mechanical state
            field_depl_new = f"field{i}_1" # new layer part
            field_depl_ext = f"field{i}_2" # extracted part
            field_depl_init = f"field{i}_3" # combined
            add_line(f"{field_depl_new} = CREA_CHAMP(MAILLAGE=mesh, OPERATION='AFFE', TYPE_CHAM='NOEU_DEPL_R', AFFE=_F(GROUP_MA=('layer{i}', ), NOM_CMP=('DX', 'DY', 'DZ'), VALE=(0.0, 0.0, 0.0)))")
            add_line(f"{field_depl_ext} = CREA_CHAMP(OPERATION='EXTR', TYPE_CHAM='NOEU_DEPL_R', RESULTAT={prev_res_meca}, INST={time_start}, NOM_CHAM='DEPL')")
            add_line(f"{field_depl_init} = CREA_CHAMP(MAILLAGE=mesh, OPERATION='ASSE', TYPE_CHAM='NOEU_DEPL_R', ASSE=(_F(CHAM_GD={field_depl_new}, GROUP_MA=('layer{i}', )), _F(CHAM_GD={field_depl_ext}, GROUP_MA={prev_active_groups_str})))")
            etat_init_meca_str = f"ETAT_INIT=_F(DEPL={field_depl_init}),"
            add_line(f"# --- End State Transfer --- \n")

        # --- THER_NON_LINE (Cooling analysis) ---
        add_line(f"""{res_ther} = THER_NON_LINE(
                         MODELE={model_ther},
                         CHAM_MATER={mat_ther_assign},
                         {etat_init_ther_str}
                         EXCIT=_F(CHARGE={bottemp_load}),
                         INCREMENT=_F(LIST_INST={list_inst}),
                         CONVERGENCE=_F(ITER_GLOB_MAXI=50, RESI_GLOB_RELA=0.0001),
                         NEWTON=_F(REAC_ITER=1),
                         RECH_LINEAIRE=_F(ITER_LINE_MAXI=50),
                         SOLVEUR=_F(MATR_DISTRIBUEE='OUI', METHODE='MUMPS'))\n""")

        # --- STAT_NON_LINE (Thermal stress analysis) ---
        add_line(f"""{mat_meca_assign} = AFFE_MATERIAU(
                         MAILLAGE=mesh,
                         MODELE={model_meca},
                         AFFE=_F(GROUP_MA={active_groups_str}, MATER=(mater1, )),
                         AFFE_VARC=_F(EVOL={res_ther}, NOM_VARC='TEMP', PROL_DROITE='CONSTANT', PROL_GAUCHE='CONSTANT', VALE_REF=300.0))\n""")

        add_line(f"""{res_meca} = STAT_NON_LINE(
                        MODELE={model_meca},
                        CHAM_MATER={mat_meca_assign},
                        {etat_init_meca_str}
                        EXCIT=_F(CHARGE={fixmec_load}),
                        COMPORTEMENT=_F(DEFORMATION='PETIT', RELATION='VMIS_ISOT_LINE', TOUT='OUI'),
                        CONVERGENCE=_F(ITER_GLOB_MAXI=50, RESI_GLOB_RELA=0.0001),
                        INCREMENT=_F(LIST_INST={list_inst}),
                        NEWTON=_F(REAC_ITER=3),
                        RECH_LINEAIRE=_F(ITER_LINE_MAXI=50),
                        SOLVEUR=_F(MATR_DISTRIBUEE='OUI', METHODE='MUMPS'))\n""")

        # --- CALC_CHAMP and IMPR_RESU ---
        add_line(f"{stress} = CALC_CHAMP(RESULTAT={res_meca}, CONTRAINTE=('SIGM_NOEU', ), CRITERES=('SIEQ_NOEU', ))\n")
        
        ther_unit = base_ther_unit + i
        meca_unit = base_meca_unit + i
        
        # The first layer output includes TOUT_CHAM, subsequent layers do not (as per original file).
        impr_ther_options = f"RESULTAT={res_ther}, TOUT_CHAM='OUI'" if i == 1 else f"RESULTAT={res_ther}"
        impr_meca_options = f"RESULTAT={stress}, TOUT_CHAM='OUI'" if i == 1 else f"RESULTAT={stress}"
        
        add_line(f"IMPR_RESU(UNITE={ther_unit}, RESU=_F(LIST_INST={list_inst}, {impr_ther_options}))")
        add_line(f"IMPR_RESU(UNITE={meca_unit}, RESU=(_F(LIST_INST={list_inst}, NOM_CHAM=('DEPL',), RESULTAT={res_meca}), _F(LIST_INST={list_inst}, {impr_meca_options})))")

    # ==========================================================================
    # 3. Finalization
    # ==========================================================================
    add_line("\nFIN()")

    # --- Write the collected content to the output file ---
    with open(output_filename, 'w') as f:
        for line in comm_file_content:
            f.write(line + '\n')
    
    print(f"Successfully generated command file: {output_filename}")


# --- Main execution block ---
if __name__ == "__main__":
    generate_comm_file()
