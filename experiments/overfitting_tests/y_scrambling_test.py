#!

import random
import numpy as np
import pandas as pd
import scipy
from tqdm import tqdm
from sklearn.metrics import r2_score, balanced_accuracy_score
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from sklearn.preprocessing import StandardScaler
from robotexperiments.formats import GT_FILE_PATH, FOLDERS_TREE
from robotexperiments.beauty import get_axes
from sklearn.model_selection import cross_val_score, KFold
import matplotlib.pyplot as plt
import seaborn as sns


experiment_dict = {
    '013' : ('RoboLab013_Lys250_Asp200_150mM_NaCl_2Dmatrix_R2',
             'DOE_Asp200_Lys250_150mM_NaCl_matrix_R2.csv'),
    '014' : ('RoboLab014_Lys20_Asp30_150mM_NaCl_2Dmatrix_R2',
             'DOE_Asp30_Lys20_150mM_NaCl_matrix_R2.csv'),
    '015' : ('RoboLab015_Lys20_Asp100_150mM_NaCl_2Dmatrix_R2',
             'DOE_Asp100_Lys20_150mM_NaCl_matrix_R2.csv'),
    '016' : ('RoboLab016_Lys20_Asp200_150mM_NaCl_2Dmatrix_R2',
             'DOE_Asp200_Lys20_150mM_NaCl_matrix_R2.csv'),
    '011' : ('RoboLab011_Lys250_Asp30_150mM_NaCl_2Dmatrix_R2',
             'DOE_Asp30_Lys250_150mM_NaCl_matrix_R2.csv'),
    '010' : ('RoboLab010_Lys100_Asp30_150mM_NaCl_2Dmatrix_R1',
             'DOE_Asp30_Lys100_150mM_NaCl_matrix_R1.csv'),
    '009' : ('RoboLab009_Lys100_Asp100_150mM_NaCl_2Dmatrix_R1',
             'DOE_Asp100_Lys100_150mM_NaCl_matrix_R1.csv'),
    '007' : ('RoboLab007_Lys100_Asp200_150mM_NaCl_2Dmatrix_1decimal_R2',
             'DOE_Asp200_Lys100_150mM_NaCl_matrix_1decimal_R2.csv'),
}


if __name__ == '__main__':

# - Set up
# exp = '012'
    for exp,exp_name in experiment_dict.items():

        print(exp_name)
        experiment_folder = f'/home/andreag/Work/1.main_project/molML_git_repo/activeML-navigation-of-condensate-phases/experiments/{exp_name[0]}/'
        df = pd.read_csv(experiment_folder+f'/dataset/{exp_name[1]}')
        last_cycle_pdf = np.load(experiment_folder+f'cycle_9/{exp_name[0]}_cycle_9_output_points_pdf.npy')

        screened_mask = df.Phase != -1
        unscreened_mask = df.Phase == -1
        X_unscreened = df.drop(columns='Phase')[unscreened_mask].to_numpy()
        unscreened_labels = np.argmax(last_cycle_pdf, axis=1)[unscreened_mask]

        X = df.drop(columns='Phase')[screened_mask].to_numpy()
        y = df.Phase[screened_mask].to_numpy()
        y_to_scramble = y.copy()

        scaler = StandardScaler()
        X_unscreened = scaler.fit_transform(X_unscreened)
        X = scaler.transform(X)

        # Define the kernel as RBF * Constant
        kernel = ConstantKernel(1.0) * RBF(length_scale=1.)

        # Create the Gaussian Process Classifier with the specified parameters
        gpc = GaussianProcessClassifier(kernel=kernel, 
                                        n_restarts_optimizer=10, 
                                        max_iter_predict=500,
                                        n_jobs=10)

        gpc.fit(X=X, y=y)
        ypred = gpc.predict(X_unscreened)
        original_bacc = balanced_accuracy_score(y_true=unscreened_labels, y_pred=ypred)
        print(f'Original accuracy: {original_bacc}')

        kf = KFold(n_splits=5, shuffle=True)

        shuffled_bacc2 = []
        # cv_score_scrambled = []
        # cv_score_non_scrambled = []
        for i in tqdm(range(500)):

            # cv_score_non_scrambled.append(
            #     cross_val_score(gpc, X, y, cv=kf, scoring='balanced_accuracy').mean()
            # )

            np.random.shuffle(y_to_scramble)

            gpc.fit(X,y_to_scramble)

            ypred = gpc.predict(X_unscreened)
            # cv_score_scrambled.append(
            #     cross_val_score(gpc, X, y_to_scramble, cv=kf, scoring='balanced_accuracy').mean()
            # )
            shuffled_bacc2.append(balanced_accuracy_score(unscreened_labels,ypred))

        fig, ax = get_axes(1,1)
        sns.histplot(data=shuffled_bacc2, kde=False, binwidth=0.025, ax=ax, label='y-scrambling')  # Histogram
        sns.kdeplot(shuffled_bacc2, color='black', fill=True, ax=ax)  # KDE plot with black line
        ax.axvline(x=original_bacc, ls='--', c='red', label='Original')
        ax.set_xlabel('Balanced Acc.')
        ax.set_xlim(0.,1.)
        ax.set_title(f'y-scrambling RoboLab{exp}')
        fig.tight_layout()
        fig.savefig(f'y_scrambling_robolab{exp}.png')

        np.save(f'robolab{exp}_yscrambling_500.npy', np.array(shuffled_bacc2))
        # np.save(f'robolab{exp}_cv_on_train.npy', np.array(cv_score_non_scrambled))
        # np.save(f'robolab{exp}_yscrambling_cv_on_train.npy', np.array(cv_score_scrambled))