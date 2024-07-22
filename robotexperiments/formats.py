#!

MASTER_FILE_NAME_FORMAT = 'master_file_version_{}.csv'

MASTER_FILE_COLUMNS = [
    'Phase' ,
    'Conc_HEPES' ,
    'pH' ,
    'Conc_Dye_Cy5_AP_Lys_100_(mM)' ,
    'Conc_Dye_FITC_AP_Asp_100_(mM)' ,
    'Plate_Barcode' ,
    'Plate_Position' ,
    'Preparation_Date' ,
    'Experiment_Code' ,
    'Mixing_Volume' ,
    'Final_Volume'  ,
    'Barcode' ,
]

EXP_REPO_PATH = '../'

FOLDERS_TREE = {
    'master_file' : EXP_REPO_PATH+'/master_file/',
    'experiments' : {
        'robot001' : EXP_REPO_PATH+'/experiments/1.Asp200_Lys100_robot_test/',
    }
}
