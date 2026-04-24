// frontend/src/App.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import SongList from "./components/SongList";
import SongDetail from "./components/SongDetail";
import "./App.css";

function App() {
  const [songs, setSongs] = useState([]);
  const [selected, setSelected] = useState({artist: "", title: ""});

  // Load song list
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/music/songs/")
        .then(res => {
          setSongs(res.data);
          if(res.data.length > 0){
            setSelected(res.data[0]);  // default selection
          }
        })
        .catch(err => console.log(err));
  }, []);

  const handleSelectSong = (artist, title) => {
    setSelected({artist, title});
  };

  return (
      <div className="App">
        <h1>Music Dashboard (Django + React)</h1>
        <div style={{ display: "flex" }}>
          <div style={{ width: "25%", borderRight: "1px solid #ccc" }}>
            <SongList
                songs={songs}
                selected={selected}
                onSelect={handleSelectSong}
            />
          </div>
          <div style={{ width: "75%", padding: "1rem" }}>
            <SongDetail artist={selected.artist} title={selected.title} />
          </div>
        </div>
      </div>
  );
}

export default App;
