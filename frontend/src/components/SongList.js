// frontend/src/components/SongList.js
import React from "react";

function SongList({ songs, selected, onSelect }) {
    return (
        <div>
            <h2>Song List</h2>
            {songs.map((s, idx) => {
                const isActive = (s.artist === selected.artist && s.title === selected.title);
                return (
                    <div
                        key={idx}
                        onClick={() => onSelect(s.artist, s.title)}
                        style={{
                            cursor: "pointer",
                            backgroundColor: isActive ? "#ddd" : "transparent",
                            marginBottom: "5px",
                            padding: "5px"
                        }}
                    >
                        {s.artist} - {s.title}
                    </div>
                );
            })}
        </div>
    );
}

export default SongList;
