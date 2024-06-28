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

GIT_REPO_PATH = '/home/andreag/Work/1.main_project/git_repo/'

FOLDERS_TREE = {
    'master_file' : GIT_REPO_PATH+'RobotLabExperiments/master_file/',
    'experiments' : {
        'robot001' : GIT_REPO_PATH+'RobotLabExperiments/experiments/1.Asp200_Lys100_robot_test/',
    }
}
