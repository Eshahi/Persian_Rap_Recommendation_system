// frontend/src/components/SongDetail.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import ReactAudioPlayer from "react-audio-player";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

function SongDetail({ artist, title }) {
    const [recommended, setRecommended] = useState([]);
    const [beatData, setBeatData] = useState([]);
    const [loading, setLoading] = useState(false);

    // fetch from DRF endpoint
    useEffect(() => {
        if(!artist || !title) return;
        setLoading(true);
        axios.get("http://127.0.0.1:8000/api/music/song-detail/", {
            params: { artist, title }
        })
            .then(res => {
                setLoading(false);
                setRecommended(res.data.recommended || []);
                setBeatData(res.data.beat_data || []);
            })
            .catch(err => {
                setLoading(false);
                console.log(err);
            });
    }, [artist, title]);

    if(!artist || !title) return <div>Please select a song.</div>;
    if(loading) return <div>Loading...</div>;

    // We assume the actual MP3 is in /musics/<artist>/<title>.mp3
    // In a real production, you'd store the file path in the DB or an S3 URL, etc.
    const audioPath = `http://127.0.0.1:8000/musics/${artist}/${title}.mp3`;
    // or maybe from your Nginx or static config

    return (
        <div>
            <h2>{artist} - {title}</h2>
            {/* Audio playback */}
            <ReactAudioPlayer
                src={audioPath}
                controls
            />

            {/* Recommended tracks */}
            <h3>Recommended:</h3>
            {recommended && recommended.length > 0 ? (
                recommended.map((r, idx) => (
                    <div key={idx}>{r.artist} - {r.title}</div>
                ))
            ) : (
                <p>No similar tracks found.</p>
            )}

            {/* Plots: e.g. RMS line chart */}
            <h3>Beat-level RMS</h3>
            <LineChart width={600} height={300} data={beatData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <XAxis dataKey="beat_index" />
                <YAxis />
                <Tooltip />
                <CartesianGrid stroke="#ccc" />
                <Line type="monotone" dataKey="rms" stroke="#8884d8" />
            </LineChart>

            <h3>Beat-level ZCR</h3>
            <LineChart width={600} height={300} data={beatData}>
                <XAxis dataKey="beat_index" />
                <YAxis />
                <Tooltip />
                <CartesianGrid stroke="#ccc" />
                <Line type="monotone" dataKey="zcr" stroke="#82ca9d" />
            </LineChart>

            <h3>Beat-level MFCC_1</h3>
            <LineChart width={600} height={300} data={beatData}>
                <XAxis dataKey="beat_index" />
                <YAxis />
                <Tooltip />
                <CartesianGrid stroke="#ccc" />
                <Line type="monotone" dataKey="mfcc_1" stroke="#ff7300" />
            </LineChart>
        </div>
    );
}

export default SongDetail;
