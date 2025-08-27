#!

import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler

# -------------------------------------------------- #
# FUNCTIONS
# -------------------------------------------------- #

def generate_ground_truth(df: pd.DataFrame, screened_var: str, ml_model):

    # Prepare training and pool data
    print("Preparing training and pool data...")
    if screened_var not in df.columns:
        raise ValueError(f"The screened variable '{screened_var}' is not in the DataFrame.")
    if df[screened_var].isnull().all():
        raise ValueError(f"The screened variable '{screened_var}' contains no valid data.")
    if df[screened_var].nunique() < 2:
        raise ValueError(f"The screened variable '{screened_var}' must have at least two unique values for classification.")

    X_train = df[df[screened_var] != -1].drop(columns=[screened_var])
    y_train = df[screened_var][df[screened_var] != -1]

    X_pool = df.drop(columns=[screened_var])

    # Scale the features
    print("Scaling features...")
    scaler = StandardScaler()
    scaler.fit(X_pool)

    X_train_scaled = scaler.transform(X_train)
    X_pool_scaled = scaler.transform(X_pool)

    # Train the machine learning model
    print("Training the machine learning model...")
    if ml_model is None:
        raise ValueError("Machine learning model must be provided.")
    ml_model.fit(X_train_scaled, y_train)

    print("Model training completed.")

    y_pred = ml_model.predict(X_pool_scaled)
    y_proba = ml_model.predict_proba(X_pool_scaled)

    return y_pred, y_proba


def save_ground_truth(df: pd.DataFrame, output_path: str, output_name: str, screened_var: str, y_pred: np.ndarray, y_proba: np.ndarray):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Save predictions and probabilities
    predicted_col = f'predicted_{screened_var}'
    df[predicted_col] = y_pred

    for proba_col, proba in enumerate(list(y_proba.T)):
        df[f'probability_{screened_var}_{proba_col}'] = proba

    output_file = os.path.join(output_path, output_name + '_ground_truth.csv')
    df.to_csv(output_file, index=False)
    print(f"Ground truth saved to {output_file}")


def plot_ground_truth(df: pd.DataFrame, output_path: str, screened_var: str):
    import matplotlib.pyplot as plt
    from activeclf.utils.beauty import get_axes

    CMAP_LIST = ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges']

    predicted_col = f'predicted_{screened_var}'
    if predicted_col not in df.columns:
        raise ValueError(f"The predicted column '{predicted_col}' is not in the DataFrame.")
    
    probability_cols = [col for col in df.columns if col.startswith(f'probability_{screened_var}')]

    cols_to_remove = [screened_var, predicted_col] + probability_cols
    X = df.drop(columns=cols_to_remove).to_numpy()

    plot_cols = [predicted_col] + probability_cols
    fig, ax = get_axes(len(plot_cols), len(plot_cols))

    for i, col in enumerate(plot_cols):
        if col == predicted_col:
            ax[i].scatter(*X.T, c=np.array(['r', 'b'])[df[col]], s=1)
            ax[i].set_title('Ground Truth Labels')
        else:
            ax[i].scatter(*X.T, c=df[col], cmap=CMAP_LIST[i-1], s=1)
            ax[i].set_title(f'Probability of {col}')

        ax[i].set_xlabel('[Feature 1]')
        ax[i].set_ylabel('[Feature 2]')
    fig.tight_layout()
    fig.savefig(os.path.join(output_path, f'ground_truth_plot_{screened_var}.png'))
    plt.show()


if __name__ == "__main__":
    # Example usage
    import argparse
    import activeclf as alclf
    from sklearn.gaussian_process import GaussianProcessClassifier
    from robotexperiments.formats import EXP_REPO_PATH

    parser = argparse.ArgumentParser(description="Generate ground truth for a dataset.")
    parser.add_argument('--exp_name', type=str, required=True, help='Name of the experiment.')
    parser.add_argument('--screened_var', type=str, required=True, help='The variable screened in the experiments.')    
    args = parser.parse_args()

    # Setting up the ml model
    classifier_dict = {
        'kernel': ['*', {'type': 'C', 'constant_value': 1.0}, {'type': 'RBF', 'length_scale': 1.0}],
        'n_restarts_optimizer': 5,
        'max_iter_predict': 300,
        'n_jobs': 8
    }
    kernel_factory = alclf.classification.KernelFactory(kernel_dict=classifier_dict['kernel'])
    classifier_dict['kernel'] = kernel_factory.get_kernel()
    ml_model = GaussianProcessClassifier(**classifier_dict)

    # reading the dataset
    exp_path = os.path.join(EXP_REPO_PATH, args.exp_name)
    if not os.path.exists(exp_path):
        raise FileNotFoundError(f"Experiment path {exp_path} does not exist.")
    dataset_path = os.path.join(exp_path, 'dataset/')
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path {dataset_path} does not exist.")
    
    # get dataset file
    dataset_file_name = [f for f in os.listdir(dataset_path) if f.startswith('DOE_')][0]
    df = pd.read_csv(os.path.join(dataset_path, dataset_file_name))

    y_pred, y_proba = generate_ground_truth(df, args.screened_var, ml_model)
    save_ground_truth(
        df, 
        dataset_path, 
        dataset_file_name.replace('.csv', ''),
        args.screened_var,
        y_pred, 
        y_proba
    )

    # plot_ground_truth(df, dataset_path, args.screened_var)