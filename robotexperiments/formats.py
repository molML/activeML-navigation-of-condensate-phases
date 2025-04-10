#!
import os

MASTER_FILE_NAME_FORMAT = 'master_file_version_insilico_{}.csv'

TARGET_LABEL = 'Phase'
UNASSIGNED_TARGET_VALUES = -1
INDICATOR_LABEL = 'Barcode'

OUTPUT_FILE_PATTERN = 'output_points'
VALIDATED_FILE_PATTERN = 'validated_points'

MASTER_FILE_COLUMNS = [
    TARGET_LABEL ,
    INDICATOR_LABEL ,
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXP_REPO_PATH = os.path.abspath(os.path.join(BASE_DIR, '../experiments/'))
MASTER_FILE_PATH = os.path.abspath(os.path.join(BASE_DIR, EXP_REPO_PATH+'/master_file/'))
GT_FILE_PATH = os.path.abspath(os.path.join(BASE_DIR, EXP_REPO_PATH+'/ground_truth/'))

FOLDERS_TREE = {
    'master_file' : MASTER_FILE_PATH+'/',
    'experiments' : {
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R1' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R1/',
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R2' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R2/',
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R3' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R3/',
        'RoboLab008_Lys100_Asp200_NaCl_Matrix_R1' : EXP_REPO_PATH+'/RoboLab008_Lys100_Asp200_NaCl_Matrix_R1/',
        'RoboLab008_Lys100_Asp200_NaCl_Matrix_R2' : EXP_REPO_PATH+'/RoboLab008_Lys100_Asp200_NaCl_Matrix_R2/',
        'RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R1' : EXP_REPO_PATH+'/RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R1/',
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R1' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R1/',
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R2' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R2/',
        'RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R3' : EXP_REPO_PATH+'/RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_insilico_R3/',
        'RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R2' : EXP_REPO_PATH+'/RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R2/',
        'RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R3' : EXP_REPO_PATH+'/RoboLab008_Lys100_Asp200_NaCl_Matrix_insilico_R3/',
    }
}

MAPPING_PHASES = {
    1 : 0,  # no phase separation
    3 : 1,  # coacervate phase separation
    2 : 2,  # aggregate ?
}
