#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import librosa

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

#%% md
# get songs meaningful features
#
#%% md
# ## Run for get the csv file
#
#%%

def get_songs_by_artist(directory):
    songs = {}
    for artist in os.listdir(directory):
        artist_path = os.path.join(directory, artist)
        if os.path.isdir(artist_path):
            songs[artist] = []
            for file in os.listdir(artist_path):
                if file.endswith(".mp3"):
                    songs[artist].append(os.path.join(artist_path, file))
    return songs


#%%
def extract_audio_features(file_path):
    y, sr = librosa.load(file_path)
    features = {
        "duration": librosa.get_duration(y=y, sr=sr),
        "pitch": librosa.yin(y, fmin=50, fmax=300),
        "spectral_centroid": librosa.feature.spectral_centroid(y=y, sr=sr)[0],
        "loudness": librosa.feature.rms(y=y)[0],
        "mfcc": librosa.feature.mfcc(y=y, sr=sr),
        "zero_crossing_rate": librosa.feature.zero_crossing_rate(y)[0]
    }
    return features, y, sr

#%% md
# #### plot_audio_features function plot the graphs and save thier image
#%%
def plot_audio_features_for_title(df, title, output_dir="output_images"):
    # Filter the data for the specific title
    song_data = df[df['title'] == title]

    if song_data.empty:
        print(f"No data found for {title}.")
        return

    # Extract relevant features
    artist = song_data['artist'].iloc[0]
    pitch = song_data[['average_pitch', 'median_pitch', 'max_pitch', 'min_pitch']].iloc[0]
    spectral_centroid = song_data[['average_spectral_centroid', 'median_spectral_centroid']].iloc[0]
    loudness = song_data[['average_loudness', 'median_loudness', 'max_loudness', 'min_loudness']].iloc[0]
    tempo = song_data['tempo'].iloc[0]

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a new figure with 4 subplots
    fig, ax = plt.subplots(1, 4, figsize=(20, 5))

    # Plot Pitch Statistics
    ax[0].bar(pitch.index, pitch.values, color="blue")
    ax[0].set_title(f"Pitch Statistics - {title} by {artist}")
    ax[0].set_xlabel("Metric")
    ax[0].set_ylabel("Frequency (Hz)")

    # Plot Spectral Centroid Statistics
    ax[1].bar(spectral_centroid.index, spectral_centroid.values, color="green")
    ax[1].set_title(f"Spectral Centroid - {title} by {artist}")
    ax[1].set_xlabel("Metric")
    ax[1].set_ylabel("Frequency (Hz)")

    # Plot Loudness Statistics
    ax[2].bar(loudness.index, loudness.values, color="red")
    ax[2].set_title(f"Loudness Statistics - {title} by {artist}")
    ax[2].set_xlabel("Metric")
    ax[2].set_ylabel("Amplitude")

    # Plot Tempo
    ax[3].bar(["Tempo"], [tempo], color="purple")
    ax[3].set_title(f"Tempo - {title} by {artist}")
    ax[3].set_ylabel("BPM")

    # Save the plot
    plt.tight_layout()
    filename = f"{artist}_{title}.png".replace(" ", "_")
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path)

    plt.show()

    print(f"Saved plot as {save_path}")

    # Close the figure to free memory
    plt.close(fig)
#%% md
# #### run this function just for the first time
#%%
feature_data = []
songs_by_artist = get_songs_by_artist("musics")
for artist, files in songs_by_artist.items():
    for file_path in files:
        title = os.path.basename(file_path).replace(".mp3", "")

        features, y, sr = extract_audio_features(file_path)

        song_features = {
            "artist": artist,
            "title": title,
            "duration": features["duration"],
            "average_pitch": np.mean(features["pitch"]),
            "median_pitch": np.median(features["pitch"]),
            "max_pitch": np.max(features["pitch"]),
            "min_pitch": np.min(features["pitch"]),
            "average_spectral_centroid": np.mean(features["spectral_centroid"]),
            "median_spectral_centroid": np.median(features["spectral_centroid"]),
            "max_spectral_centroid": np.max(features["spectral_centroid"]),
            "min_spectral_centroid": np.min(features["spectral_centroid"]),
            "average_loudness": np.mean(features["loudness"]),
            "median_loudness": np.median(features["loudness"]),
            "max_loudness": np.max(features["loudness"]),
            "min_loudness": np.min(features["loudness"]),
            "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
            "average_zero_crossing_rate": np.mean(features["zero_crossing_rate"]),
            "median_zero_crossing_rate": np.median(features["zero_crossing_rate"]),
            "mfcc_mean_1": np.mean(features["mfcc"][0]),
            "mfcc_mean_2": np.mean(features["mfcc"][1]),
            "mfcc_mean_3": np.mean(features["mfcc"][2]),
        }

        feature_data.append(song_features)

df_features = pd.DataFrame(feature_data)
df_features.to_csv('music_features.csv', index=True, encoding='utf-8')
#%% md
# #### read data from csv files
#%%
df_features = pd.read_csv('music_features.csv')
#%%
df_features
#%%
df_features.dtypes

#%%
for title in df_features['title'].unique():
    plot_audio_features_for_title(df_features,title)
#%% md
# #### doing pca to reduce features and find difference between rappers
#%%
numeric_features = df_features.select_dtypes(include=[np.number]).drop(columns=["duration"])  # Exclude non-feature columns if any

# Standardize the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(numeric_features)

# Perform PCA
pca = PCA(n_components=2)
pca_features = pca.fit_transform(scaled_features)

# Add PCA results to DataFrame for easy plotting
df_features['PCA1'] = pca_features[:, 0]
df_features['PCA2'] = pca_features[:, 1]

# Plot PCA result
plt.figure(figsize=(10, 6))
sns.scatterplot(x='PCA1', y='PCA2', hue='artist', data=df_features, palette="Set1")
plt.title("PCA of Audio Features by Artist")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend(title="Artist")
plt.show()

#%% md
# Violin plot for feature Distributions
#%%
# Violin plot for average_pitch by artist
plt.figure(figsize=(12, 6))
sns.violinplot(x="artist", y="average_pitch", data=df_features, palette="Set2",legend=False)
plt.title("Distribution of Average Pitch by Artist")
plt.show()

# Violin plot for average_spectral_centroid by artist
plt.figure(figsize=(12, 6))
sns.violinplot(x="artist", y="average_spectral_centroid", data=df_features, palette="Set2",legend=False)
plt.title("Distribution of Average Spectral Centroid by Artist")
plt.show()

# Violin plot for average_loudness by artist
plt.figure(figsize=(12, 6))
sns.violinplot(x="artist", y="average_loudness", hue="artist", data=df_features, palette="Set2", legend=False)
plt.title("Distribution of Average Loudness by Artist")
plt.show()

#%% md
# Correlation Heatmaps for Each Artist
#%%
for artist in df_features['artist'].unique():
    artist_data = df_features[df_features['artist'] == artist].select_dtypes(include=[np.number])
    plt.figure(figsize=(10, 8))
    sns.heatmap(artist_data.corr(), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(f"Feature Correlation Heatmap for {artist}")
    plt.show()

#%% md
# Pair Plot for Selected Features
#%%
# Selecting key features for pair plot
selected_features = ["average_pitch", "average_spectral_centroid", "average_loudness", "tempo"]

sns.pairplot(df_features, vars=selected_features, hue="artist", palette="Set1", markers=["o", "s", "D"])
plt.suptitle("Pair Plot of Audio Features by Artist", y=1.02)
plt.show()

#%% md
# ## Extracting Audio Features Per Beat
# #### It is needed for chroma and ATM
#%%
def extract_audio_features_per_beat(file_path):
    """
    Load audio, compute beat-synchronous MFCC, Chroma, Zero-Crossing, RMS (loudness),
    and optional tempogram as a simple ATM approximation.
    Returns:
      A dict of { 'mfcc': 2D array, 'chroma': 2D array, 'tempogram': 2D array, etc. }
      and also the beat_times in seconds.
    """
    y, sr = librosa.load(file_path)

    # 1) Beat Tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # 2) Frame-Based Features
    # -- MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=12)
    # -- Chroma
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=12)
    # -- Zero-Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y)
    # -- RMS (loudness)
    rms = librosa.feature.rms(y=y)
    # (Optional) Tempogram to approximate ATMs
    #   This is not a full ATM model, but captures modulations
    tempogram = librosa.feature.tempogram(y=y, sr=sr)

    # 3) Sync to Beats (Aggregate frames within each beat)
    # librosa.util.sync returns a new 2D array with shape = (feature_dim, number_of_beats)
    mfcc_beat_sync = librosa.util.sync(mfcc, beat_frames, aggregate=np.mean)
    chroma_beat_sync = librosa.util.sync(chroma, beat_frames, aggregate=np.mean)
    zcr_beat_sync = librosa.util.sync(zcr, beat_frames, aggregate=np.mean)
    rms_beat_sync = librosa.util.sync(rms, beat_frames, aggregate=np.mean)
    tempogram_beat_sync = librosa.util.sync(tempogram, beat_frames, aggregate=np.mean)

    # 4) Return data
    return {
        'mfcc': mfcc_beat_sync,
        'chroma': chroma_beat_sync,
        'zcr': zcr_beat_sync,
        'rms': rms_beat_sync,
        'tempogram': tempogram_beat_sync,   # optional
        'beat_times': beat_times,
        'tempo': tempo,
        'sr': sr
    }
#%% md
# ## Build Beat Level Dataframe
# #### Building a Single DataFrame with One Row Per Beat
#%%
def build_beat_level_dataframe(artist, title, features_dict):
    """
    Given the beat-synchronous feature dict from extract_audio_features_per_beat(),
    build a DataFrame with each row = 1 beat.
    Columns include: artist, title, beat_index, time_in_sec,
                     mfcc_1..mfcc_12, chroma_1..chroma_12, zcr, rms, tempogram, ...
    """
    beat_times = features_dict['beat_times']
    num_beats = len(beat_times)

    # Prepare data storage
    rows = []

    # For each beat index
    for i in range(num_beats):
        beat_time = beat_times[i]  # in seconds

        # MFCC shape = (12, num_beats). We'll pick out the i-th column for each dimension
        mfcc_values = features_dict['mfcc'][:, i]  # shape (12,)
        chroma_values = features_dict['chroma'][:, i]  # shape (12,)
        zcr_value = features_dict['zcr'][:, i].mean()  # or just [0, i] if shape is (1, num_beats)
        rms_value = features_dict['rms'][:, i].mean()

        # Tempogram is optional: shape (something, num_beats)
        tempogram_values = features_dict['tempogram'][:, i]

        row_data = {
            'artist': artist,
            'title': title,
            'beat_index': i,
            'time_in_sec': beat_time,
            'tempo': features_dict['tempo']
        }

        # Add MFCCs as separate columns: mfcc_1..mfcc_12
        for mfcc_i, val in enumerate(mfcc_values, start=1):
            row_data[f'mfcc_{mfcc_i}'] = val

        # Add Chroma: chroma_1..chroma_12
        for c_i, val in enumerate(chroma_values, start=1):
            row_data[f'chroma_{c_i}'] = val

        # Add ZCR, RMS
        row_data['zcr'] = zcr_value
        row_data['rms'] = rms_value

        # (Optional) Add Tempogram bins
        for t_i, val in enumerate(tempogram_values, start=1):
            row_data[f'tempogram_{t_i}'] = val

        rows.append(row_data)

    # Convert to a DataFrame
    df_beat_level = pd.DataFrame(rows)
    return df_beat_level
#%%
all_beat_dfs = []

songs_by_artist = get_songs_by_artist("musics")
for artist, files in songs_by_artist.items():
    for file_path in files:
        title = os.path.basename(file_path).replace(".mp3", "")

        features_dict = extract_audio_features_per_beat(file_path)

        df_beat_level = build_beat_level_dataframe(artist, title, features_dict)

        all_beat_dfs.append(df_beat_level)

# Final single DataFrame
df_all_beat_songs = pd.concat(all_beat_dfs, ignore_index=True)

df_all_beat_songs.to_csv('music_beat_sync_features.csv', index=False)

#%%
df_all_beat_songs
#%% md
# ## Visualize new synchronous-beat features
#%%
def plot_beat_features(df, artist_name, title):
    """
    Create a multi-subplot figure showing RMS, ZCR, and MFCC_1
    over beat indices for the specified artist and title.
    """

    # Filter and sort data
    song_data = df[(df['artist'] == artist_name) & (df['title'] == title)]
    if song_data.empty:
        print(f"No data found for {artist_name} - {title}")
        return

    song_data = song_data.sort_values(by='beat_index')

    # Create figure with 3 subplots (rows), sharing the x-axis
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

    # Overall title (above all subplots)
    fig.suptitle(f"Beat-Level Feature Curves for {title} by {artist_name}", fontsize=14, y=0.98)

    # -- Subplot 1: RMS
    axes[0].plot(song_data['beat_index'], song_data['rms'],
                 color='tab:blue', label='RMS')
    axes[0].set_ylabel("RMS")
    axes[0].grid(True)

    # -- Subplot 2: ZCR
    axes[1].plot(song_data['beat_index'], song_data['zcr'],
                 color='tab:orange', label='ZCR')
    axes[1].set_ylabel("ZCR")
    axes[1].grid(True)

    # -- Subplot 3: MFCC_1
    axes[2].plot(song_data['beat_index'], song_data['mfcc_1'],
                 color='tab:green', label='MFCC_1')
    axes[2].set_ylabel("MFCC_1")
    axes[2].grid(True)

    # Common x-label
    axes[-1].set_xlabel("Beat Index")

    plt.tight_layout()
    plt.show()
#%%
plot_beat_features(df_all_beat_songs,'bahram','Beshno')
#%%
plot_beat_features(df_all_beat_songs,'pishro','Divoone 2')

#%% md
# #### normalized plot
#%%
def plot_beat_features_standardized(df, artist_name, title):
    song_data = df[(df['artist'] == artist_name) & (df['title'] == title)]
    if song_data.empty:
        print(f"No data found for {artist_name} - {title}")
        return

    song_data = song_data.sort_values(by='beat_index')

    # Select just the columns of interest
    features_array = song_data[['rms','zcr','mfcc_1']].values
    # Standardize
    scaler = StandardScaler()
    features_std = scaler.fit_transform(features_array)

    # features_std[:,0] = RMS (standardized), etc.
    rms_std = features_std[:, 0]
    zcr_std = features_std[:, 1]
    mfcc1_std = features_std[:, 2]

    plt.figure(figsize=(12, 6))
    plt.plot(song_data['beat_index'], rms_std, label='RMS (std)', )
    plt.plot(song_data['beat_index'], zcr_std, label='ZCR (std)', )
    plt.plot(song_data['beat_index'], mfcc1_std, label='MFCC_1 (std)',)

    plt.title(f"Standardized Beat-Level Features for {title} by {artist_name}")
    plt.xlabel("Beat Index")
    plt.ylabel("Standardized Value")
    plt.legend()
    plt.grid(True)
    plt.show()
#%%
plot_beat_features_standardized(df_all_beat_songs,'bahram','Beshno')

#%%
