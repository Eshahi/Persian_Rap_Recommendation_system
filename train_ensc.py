# train_ensc.py

import pandas as pd
import numpy as np
import os
import numpy.linalg as la

# =============== 1) Load Data ================
def load_beat_sync_data(csv_path="music_beat_sync_features.csv"):
    return pd.read_csv(csv_path)

# =============== 2) Simple ADMM Solver (Optional) ================
def ensc_solver(X, lam1=0.1, lam2=0.05, lam3=0.1, max_iter=10):
    """
    Solve a simplified ENSC:
      min_{Z,E} lam1 ||Z||_1 + (lam2/2)||Z||_F^2 + lam3 ||E||_1
      s.t. X = XZ + E, diag(Z)=0

    X: (d x N) data matrix
    Returns: Z (N x N), E (d x N) [though E not used further here].
    """
    d, N = X.shape
    Z = np.zeros((N, N))
    E = np.zeros((d, N))
    Y = np.zeros((d, N))
    mu = 1.0

    def soft_threshold(M, tau):
        return np.sign(M) * np.maximum(np.abs(M) - tau, 0.0)

    for _ in range(max_iter):
        # Update Z
        R = X - E + (1.0 / mu) * Y
        step_size = 0.5 / (la.norm(X, 2) ** 2 + lam2)
        Z_grad = (X.T @ (X @ Z - R)) + lam2 * Z
        Z_new = Z - step_size * Z_grad
        Z_soft = soft_threshold(Z_new, step_size * lam1)
        np.fill_diagonal(Z_soft, 0.0)
        Z = Z_soft

        # Update E
        T = X - X @ Z + (1.0 / mu) * Y
        E = soft_threshold(T, lam3 / mu)

        # Update Y
        Y = Y + mu * (X - X @ Z - E)

        # Check residual
        res = la.norm(X - X @ Z - E, 'fro')
        if res < 1e-5:
            break

    return Z, E

# =============== 3) Build & Solve ENSC ================
def run_offline_ensc(
    input_csv="music_beat_sync_features.csv",
    output_csv="ensc_results.csv",
    feature_cols=["mfcc_1", "zcr", "rms"]
):
    print("Loading beat-level data...")
    df = load_beat_sync_data(input_csv).sort_values(by=["artist","title","beat_index"])

    # Build data matrix X (d x N)
    X_list = []
    track_id_list = []

    for _, row in df.iterrows():
        vec = row[feature_cols].values.astype(float)
        X_list.append(vec)
        track_id_list.append((row["artist"], row["title"]))

    X_array = np.nan_to_num(np.array(X_list))  # shape (N, d)
    N, d = X_array.shape
    X = X_array.T  # shape (d, N)

    # L2 normalize columns
    col_norms = np.linalg.norm(X, axis=0, keepdims=True) + 1e-9
    X = X / col_norms

    print("Running simplified ENSC solver...")
    Z, _ = ensc_solver(X, lam1=0.1, lam2=0.05, lam3=0.1, max_iter=10)
    print("Done solver.")

    # Build affinity matrix
    W = np.abs(Z) + np.abs(Z.T)

    # Spectral embedding
    row_sum = np.sum(W, axis=1)
    D = np.diag(row_sum)
    L = D - W
    eigenvals, eigenvects = np.linalg.eig(L)
    idx_sorted = np.argsort(eigenvals.real)
    e2 = eigenvects[:, idx_sorted[1]].real
    e3 = eigenvects[:, idx_sorted[2]].real
    coords_2d = np.vstack([e2, e3]).T  # shape (N, 2)

    # Map beat-level coords => track-level coords
    df_coords = pd.DataFrame({
        "artist": [a for (a, _) in track_id_list],
        "title":  [t for (_, t) in track_id_list],
        "x_beat": coords_2d[:, 0],
        "y_beat": coords_2d[:, 1]
    })

    grouped = df_coords.groupby(["artist","title"], as_index=False).agg({
        "x_beat": "mean",
        "y_beat": "mean"
    })
    grouped.rename(columns={"x_beat": "ensc_x", "y_beat": "ensc_y"}, inplace=True)

    print(f"Saving embedding to {output_csv} ...")
    grouped.to_csv(output_csv, index=False)
    print("All done.")

# =============== 4) MAIN (if run directly) ================
if __name__ == "__main__":
    run_offline_ensc(
        input_csv="music_beat_sync_features.csv",
        output_csv="ensc_results.csv",
        feature_cols=["mfcc_1","zcr","rms"]
    )
