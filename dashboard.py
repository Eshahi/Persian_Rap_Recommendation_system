import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import base64
import matplotlib.pyplot as plt

@st.cache_data
def load_beats(csv_path="music_beat_sync_features.csv"):
    df = pd.read_csv(csv_path)
    return df

@st.cache_data
def load_ensc(csv_path="ensc_results.csv"):
    df = pd.read_csv(csv_path)
    return df

def list_songs(df_beats):
    grouped = df_beats.groupby(["artist","title"]).size().reset_index().iloc[:,:2]
    return [f"{row['artist']}::{row['title']}" for _, row in grouped.iterrows()]

def get_beat_data(df_beats, artist, title):
    sub = df_beats[(df_beats["artist"] == artist) & (df_beats["title"] == title)].copy()
    sub.sort_values(by="beat_index", inplace=True)
    return sub

def find_top_3_similar(df_ensc, cur_artist, cur_title):
    current = df_ensc[(df_ensc["artist"] == cur_artist) & (df_ensc["title"] == cur_title)]
    if current.empty:
        return []
    x0, y0 = current["ensc_x"].iloc[0], current["ensc_y"].iloc[0]
    df_ensc["dist"] = np.sqrt((df_ensc["ensc_x"] - x0)**2 + (df_ensc["ensc_y"] - y0)**2)
    sorted_df = df_ensc.sort_values("dist")
    top_4 = sorted_df.head(4)  # includes self
    top_3 = top_4[top_4["dist"] > 1e-9].head(3)
    return [(row["artist"], row["title"]) for _, row in top_3.iterrows()]

def read_audio_as_base64(file_path):
    """Utility to read binary MP3 and return base64-encoded string."""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def main():
    st.title("Music Dashboard: Real-Time Plot Animation")

    # --- 1) Load data ---
    df_beats = load_beats("music_beat_sync_features.csv")
    df_ensc = load_ensc("ensc_results.csv")
    if df_beats.empty or df_ensc.empty:
        st.error("No data loaded. Check CSV files.")
        return

    # --- 2) Song selection ---
    songs = list_songs(df_beats)
    if not songs:
        st.error("No songs in the beat CSV.")
        return

    if "selected_song" not in st.session_state:
        st.session_state["selected_song"] = songs[0]

    selected_song = st.selectbox(
        "Choose a song:",
        options=songs,
        index=songs.index(st.session_state["selected_song"])
        if st.session_state["selected_song"] in songs
        else 0
    )

    if selected_song != st.session_state["selected_song"]:
        st.session_state["selected_song"] = selected_song
        st.session_state["live_running"] = False
        st.session_state["live_beat_index"] = 0

    # --- 3) Initialize session state ---
    if "live_running" not in st.session_state:
        st.session_state["live_running"] = False
    if "live_beat_index" not in st.session_state:
        st.session_state["live_beat_index"] = 0

    # --- 4) Playback controls ---
    if st.button("Play", key="play_btn"):
        # Start the animation + attempt autoplay
        st.session_state["live_running"] = True

    # --- 5) Now Playing: Audio + Similar Tracks ---
    artist, title = st.session_state["selected_song"].split("::")
    st.subheader(f"Now Playing: {artist} - {title}")

    song_path = os.path.join("musics", artist, f"{title}.mp3")
    if os.path.exists(song_path):
        # Attempt "autoplay" if live_running is True; otherwise normal player
        if st.session_state["live_running"]:
            b64_mp3 = read_audio_as_base64(song_path)
            audio_html = f"""
            <audio autoplay controls>
              <source src="data:audio/mp3;base64,{b64_mp3}" type="audio/mpeg">
              Your browser does not support the audio element.
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        else:
            st.audio(song_path)
    else:
        st.warning("Audio file not found locally.")

    top_3 = find_top_3_similar(df_ensc, artist, title)
    st.write("**Recommended**:")
    if top_3:
        for (a, t) in top_3:
            label = f"{a}::{t}"
            if st.button(f"→ {a} - {t}", key=f"rec_{a}_{t}"):
                st.session_state["live_running"] = False
                st.session_state["live_beat_index"] = 0
                st.session_state["selected_song"] = label
                st.rerun()  # Switch track immediately
    else:
        st.write("No similar tracks found.")

    # --- 6) Beat-level data for "live" animation ---
    song_df = get_beat_data(df_beats, artist, title)
    if song_df.empty:
        st.warning("No beat-level data for this track.")
        return

    i = st.session_state["live_beat_index"]
    if i >= len(song_df):
        i = 0
        st.session_state["live_beat_index"] = 0
        st.session_state["live_running"] = False
        st.info("Reached end of track data. Resetting...")

    # We'll animate 3 rolling line plots: RMS, ZCR, MFCC_1
    window_size = 30
    start_i = max(0, i - window_size)
    df_window = song_df.iloc[start_i : i + 1]

    col1, col2, col3 = st.columns(3)

    with col1:
        fig_rms, ax_rms = plt.subplots(figsize=(3,3))
        ax_rms.plot(df_window["beat_index"], df_window["rms"], color="blue")
        ax_rms.set_title("RMS")
        ax_rms.set_xlabel("Beat Index")
        st.pyplot(fig_rms)
        plt.close(fig_rms)

    with col2:
        fig_zcr, ax_zcr = plt.subplots(figsize=(3,3))
        ax_zcr.plot(df_window["beat_index"], df_window["zcr"], color="green")
        ax_zcr.set_title("ZCR")
        ax_zcr.set_xlabel("Beat Index")
        st.pyplot(fig_zcr)
        plt.close(fig_zcr)

    with col3:
        fig_mfcc, ax_mfcc = plt.subplots(figsize=(3,3))
        ax_mfcc.plot(df_window["beat_index"], df_window["mfcc_1"], color="orange")
        ax_mfcc.set_title("MFCC_1")
        ax_mfcc.set_xlabel("Beat Index")
        st.pyplot(fig_mfcc)
        plt.close(fig_mfcc)

    # --- 7) Automatic animation loop ---
    if st.session_state["live_running"]:
        if i < len(song_df):
            st.session_state["live_beat_index"] += 1
            time.sleep(0.3)
            st.rerun()
        else:
            st.session_state["live_running"] = False
            # Keep beat index as-is or reset, your choice
            st.session_state["live_beat_index"] = 0

    # --- 8) 2D ENSC Plot (Scatter) ---
    st.write("**2D ENSC Embedding**")
    fig_c, ax_c = plt.subplots(figsize=(5,4))
    ax_c.scatter(
        df_ensc["ensc_x"], df_ensc["ensc_y"],
        c="gray", alpha=0.6, s=40, label="All Tracks"
    )
    track_row = df_ensc[(df_ensc["artist"] == artist) & (df_ensc["title"] == title)]
    if not track_row.empty:
        ax_c.scatter(
            track_row["ensc_x"], track_row["ensc_y"],
            c="red", s=100, edgecolors="black", label="Current Track"
        )
    ax_c.set_title("ENSC Embedding")
    ax_c.set_xlabel("ensc_x")
    ax_c.set_ylabel("ensc_y")
    ax_c.legend()
    st.pyplot(fig_c)
    plt.close(fig_c)

    # --- 9) Full-length curves (no animation) ---
    st.write("**Full-length Curves**")
    fig_f, axes = plt.subplots(3, 1, figsize=(8,6), sharex=True)
    axes[0].plot(song_df["beat_index"], song_df["rms"], color="blue")
    axes[0].set_ylabel("RMS")
    axes[1].plot(song_df["beat_index"], song_df["zcr"], color="green")
    axes[1].set_ylabel("ZCR")
    axes[2].plot(song_df["beat_index"], song_df["mfcc_1"], color="orange")
    axes[2].set_ylabel("MFCC_1")
    axes[2].set_xlabel("Beat Index")
    plt.tight_layout()
    st.pyplot(fig_f)
    plt.close(fig_f)

if __name__ == "__main__":
    main()
