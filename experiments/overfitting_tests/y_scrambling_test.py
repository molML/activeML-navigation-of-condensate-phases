#!

import random
import numpy as np
import pandas as pd
import scipy
from sklearn.metrics import r2_score, balanced_accuracy_score
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from robotexperiments.formats import GT_FILE_PATH, FOLDERS_TREE
from robotexperiments.beauty import get_alphas, get_axes
import matplotlib.pyplot as plt
import seaborn as sns

# - Set up
exp = '012'
exp_name = 'RoboLab012_Lys250_Asp100_150mM_NaCl_2Dmatrix_R2'
experiment_folder = f'/home/andreag/Work/1.main_project/molML_git_repo/activeML-navigation-of-condensate-phases/experiments/{exp_name}/'
df = pd.read_csv(experiment_folder+f'/dataset/DOE_Asp100_Lys250_150mM_NaCl_matrix_R2.csv')
last_cycle_pdf = np.load(experiment_folder+f'cycle_9/{exp_name}_cycle_9_output_points_pdf.npy')

screened_mask = df.Phase != -1
unscreened_mask = df.Phase == -1
X_unscreened = df.drop(columns='Phase')[unscreened_mask].to_numpy()
unscreened_labels = np.argmax(last_cycle_pdf, axis=1)[unscreened_mask]

X = df.drop(columns='Phase')[screened_mask].to_numpy()
y = df.Phase[screened_mask].to_numpy()

scaler = StandardScaler()
X_unscreened = scaler.fit_transform(X_unscreened)
X = scaler.transform(X)

# Define the kernel as RBF * Constant
kernel = ConstantKernel(1.0) * RBF(length_scale=1.)

# Create the Gaussian Process Classifier with the specified parameters
gpc = GaussianProcessClassifier(kernel=kernel, 
                                n_restarts_optimizer=10, 
                                max_iter_predict=500)

# - Main

if __name__ == '__main__':

    gpc.fit(X=X, y=y)
    ypred = gpc.predict(X_unscreened)
    original_bacc = balanced_accuracy_score(y_true=unscreened_labels, y_pred=ypred)
    print(f'Original accuracy: {original_bacc}')

    shuffled_bacc2 = []
    for i in range(100):
        np.random.shuffle(y)
        gpc.fit(X,y)
        ypred = gpc.predict(X_unscreened)
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

    np.save(f'robolab{exp}_yscrambling.npy', np.array(shuffled_bacc2))