import pandas as pd
import numpy as np
import os

# Example: read from CSV
df_beats = pd.read_csv("music_beat_sync_features.csv")  # or absolute path
df_ensc = pd.read_csv("ensc_results.csv")

def list_songs():
    # Return a list of (artist, title) from df_beats
    grouped = df_beats.groupby(["artist","title"]).size().reset_index().iloc[:,:2]
    return [(row['artist'], row['title']) for _, row in grouped.iterrows()]

def get_beat_data(artist, title):
    sub = df_beats[(df_beats["artist"] == artist) & (df_beats["title"] == title)].copy()
    sub.sort_values(by="beat_index", inplace=True)
    return sub

def find_top_3_similar(cur_artist, cur_title):
    current = df_ensc[(df_ensc["artist"] == cur_artist) & (df_ensc["title"] == cur_title)]
    if current.empty:
        return []
    x0, y0 = current["ensc_x"].iloc[0], current["ensc_y"].iloc[0]
    df_ensc["dist"] = np.sqrt((df_ensc["ensc_x"]-x0)**2 + (df_ensc["ensc_y"]-y0)**2)
    sorted_df = df_ensc.sort_values("dist")
    top_4 = sorted_df.head(4)  # includes self
    top_3 = top_4[top_4["dist"]>1e-9].head(3)
    return list(zip(top_3["artist"], top_3["title"]))
