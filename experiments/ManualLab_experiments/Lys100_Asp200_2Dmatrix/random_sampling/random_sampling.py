#!

import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF, ConstantKernel
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler
from robotexperiments import human_sampler
from robotexperiments.formats import GT_FILE_PATH

# Setup

gt_experiment = '/RoboLab007_GT/RoboLab007_GT.csv'
gt_df_file = GT_FILE_PATH+f'{gt_experiment}'
gt_df = pd.read_csv(gt_df_file)
gt_proba = np.loadtxt(GT_FILE_PATH+'/RoboLab007_GT/RoboLab007_GT_pdf.dat')

coordinates = gt_df.drop(columns='Phase').to_numpy()
indices_pool = gt_df.index.to_list()
scaler = StandardScaler()
X = scaler.fit_transform(X=coordinates)

N_rep = 6
n_point_to_sample = np.arange(8,120,8)

# Main

if __name__ == "__main__":

    rnd_sample_points = []
    rnd_sample_labels = []
    rnd_sample_probab = []
    bacc_rnd = []

    for npoints in n_point_to_sample:

        sampled_points = human_sampler.random_sampler(indices_pool=indices_pool,
                                                        n_points=npoints)
        
        X_sampled = X[sampled_points]
        y_sampled = gt_df['Phase'].iloc[sampled_points].to_list()

        # Define the kernel as RBF * Constant
        kernel = ConstantKernel(1.0) * RBF(length_scale=.1)

        # Create the Gaussian Process Classifier with the specified parameters
        gpc = GaussianProcessClassifier(kernel=kernel, 
                                        n_restarts_optimizer=5, 
                                        max_iter_predict=300)

        # one shot evaluation        
        gpc.fit(X=X_sampled, y=y_sampled)

        X_predict = gpc.predict(X=X)
        X_predict_proba = gpc.predict_proba(X=X)

        # store
        rnd_sample_points.append(X_sampled)
        rnd_sample_labels.append(X_predict)
        rnd_sample_probab.append(X_predict_proba)

        bacc_rnd.append(balanced_accuracy_score(y_pred=X_predict, y_true=gt_df.Phase.to_list()))

        # save
        np.save(f'./rep{N_rep}/rnd_sample_{len(sampled_points)}p_labels', X_predict)
        np.save(f'./rep{N_rep}/rnd_sample_{len(sampled_points)}p_probab', X_predict_proba)
        np.save(f'./rep{N_rep}/rnd_sample_{len(sampled_points)}p_points_ndxa', sampled_points)

    np.save(f'./rep{N_rep}/rnd_sample_baccuracy.npy')