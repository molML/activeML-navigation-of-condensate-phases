# -------------------------------------------------- #
# Script to extract validated points
# from a validated master file at 
# the end of the cycle
# 
#
# AUTHOR: Andrea Gardin
# -------------------------------------------------- #

from robotexperiments.cycle import extract_validated_points

# --- Variables

experimentID = 'asp250_lys100_NaCl_robotExp0'
cycle_number_tmp = 3

# --- main

if __name__ == '__main__':

    print('# --------------------------------------\n'\
         f'# \tExtract validated points of {cycle_number_tmp}     \n'\
          '# --------------------------------------\n'\
          )

    extract_validated_points(experimentID=experimentID,
                             cycle_number=cycle_number_tmp)