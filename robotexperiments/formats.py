#!

MASTER_FILE_NAME_FORMAT = 'master_file_version_{}.csv'

MASTER_FILE_COLUMNS = [
    'Phase' ,
    'conc_HEPES' ,
    'pH' ,
    'conc_Cy5_AP_Lys100' ,
    'plate_barcode' ,
    'plate_position' ,
    'preparation_date' ,
    'experiment_code' ,
    'openT_protocol' ,
    'Volume' ,
    'barcode' ,
]

FOLDERS_TREE = {
    'master_file' : '/home/andreag/Work/1.main_project/git_repo/RobotLabExperiments/master_file/',
    'experiments' : {
        'robot001' : '/home/andreag/Work/1.main_project/git_repo/RobotLabExperiments/experiments/1.Asp200_Lys100_robot/',
    }
}
