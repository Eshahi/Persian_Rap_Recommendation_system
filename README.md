# Persian Rap Recommendation System

A music recommendation system for Persian rap tracks, built with Python and Django REST Framework.

The project analyzes extracted audio and embedding features from Persian rap songs, then recommends similar tracks based on distance between song-level representations.

---

## Overview

**Persian Rap Recommendation System** is designed to help users discover similar Persian rap songs by comparing feature representations of tracks.

The system uses precomputed CSV datasets containing beat-level audio features and song-level embedding coordinates, then exposes recommendation results through API endpoints.

The backend provides endpoints for:

- Listing available songs
- Fetching details for a selected song
- Returning the top recommended similar tracks
- Returning beat-level feature data for visualization or analysis

---

## Features

- Persian rap song recommendation
- Song similarity search using embedding distance
- Beat-level feature retrieval for selected tracks
- REST API built with Django REST Framework
- CSV-based data pipeline
- Simple and extensible project structure
- Support for frontend or dashboard integration

---

## Tech Stack

- Python
- Django
- Django REST Framework
- Pandas
- NumPy
- SQLite
- django-cors-headers

---

## Recommendation Method

The recommendation logic is based on song-level embedding coordinates stored in `ensc_results.csv`.

For a selected song, the system:

1. Finds the selected song by `artist` and `title`
2. Reads its embedding coordinates: `ensc_x` and `ensc_y`
3. Computes Euclidean distance between the selected song and all other songs
4. Sorts songs by distance
5. Returns the top 3 most similar tracks, excluding the selected song itself

---

## Dataset Files

The project expects the following CSV files:

```text
music_beat_sync_features.csv
ensc_results.csv
```

### `music_beat_sync_features.csv`

Contains beat-level audio features for each song. The backend uses this file to return detailed per-beat data for a selected track.

Expected fields include:

```text
artist
title
beat_index
rms
zcr
mfcc_1
...
```

### `ensc_results.csv`

Contains song-level embedding coordinates used for recommendation.

Expected fields:

```text
artist
title
ensc_x
ensc_y
```

Example:

```csv
artist,title,ensc_x,ensc_y
hichkas,ekhtelaf,-0.00289729917283443,0.000083749776252772
bahram,Beshno,0.000059872633909127825,0.000050027743951834335
```

---

## Project Structure

```text
Persian_Rap_Recommendation_system/
│
├── backend/
│   ├── backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── musicapp/
│   │   ├── analysis_utils.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   └── manage.py
│
├── music_beat_sync_features.csv
├── ensc_results.csv
├── .gitignore
└── README.md
```

---

## API Endpoints

Base path:

```text
/api/music/
```

### Get All Songs

```http
GET /api/music/songs/
```

Returns the list of available songs.

Example response:

```json
[
  {
    "artist": "hichkas",
    "title": "ekhtelaf"
  },
  {
    "artist": "bahram",
    "title": "Beshno"
  }
]
```

### Get Song Details and Recommendations

```http
GET /api/music/song-detail/?artist=<artist>&title=<title>
```

Example request:

```http
GET /api/music/song-detail/?artist=hichkas&title=ekhtelaf
```

Example response:

```json
{
  "artist": "hichkas",
  "title": "ekhtelaf",
  "recommended": [
    {
      "artist": "pishro",
      "title": "Kalafegi"
    },
    {
      "artist": "bahram",
      "title": "Daagh"
    },
    {
      "artist": "sorena",
      "title": "Teryagh"
    }
  ],
  "beat_data": [
    {
      "artist": "hichkas",
      "title": "ekhtelaf",
      "beat_index": 0,
      "rms": 0.12,
      "zcr": 0.04,
      "mfcc_1": -83.5
    }
  ]
}
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Eshahi/Persian_Rap_Recommendation_system.git
cd Persian_Rap_Recommendation_system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

```bash
# macOS / Linux
source venv/bin/activate
```

```bash
# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

If the project includes a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages manually:

```bash
pip install django djangorestframework django-cors-headers pandas numpy
```

### 4. Move into the Backend Directory

```bash
cd backend
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The backend should now be available at:

```text
http://127.0.0.1:8000/
```

---

## Usage

After starting the Django server, test the API in your browser or with `curl`.

### List Songs

```bash
curl http://127.0.0.1:8000/api/music/songs/
```

### Get Recommendations

```bash
curl "http://127.0.0.1:8000/api/music/song-detail/?artist=hichkas&title=ekhtelaf"
```

---

## Example Python Usage

```python
import requests

artist = "hichkas"
title = "ekhtelaf"

url = "http://127.0.0.1:8000/api/music/song-detail/"
params = {
    "artist": artist,
    "title": title
}

response = requests.get(url, params=params)
data = response.json()

print("Selected song:", data["artist"], "-", data["title"])

print("\nRecommended songs:")
for song in data["recommended"]:
    print(f"- {song['artist']} - {song['title']}")
```

---

## Core Logic

The main recommendation functions are located in:

```text
backend/musicapp/analysis_utils.py
```

Important functions:

```python
list_songs()
```

Returns all available songs from the beat-level feature dataset.

```python
get_beat_data(artist, title)
```

Returns beat-level feature rows for a selected song.

```python
find_top_3_similar(cur_artist, cur_title)
```

Finds the top 3 most similar songs based on distance between `ensc_x` and `ensc_y` coordinates.

---

## CORS Configuration

The backend is configured to allow requests from:

```text
http://localhost:3000
```

This makes it suitable for use with a local frontend application, such as React, Next.js, or another dashboard interface.

---

## Notes

- Audio files are not necessarily included in the repository.
- Large music files should not be committed to GitHub.
- Keep local music folders, virtual environments, and generated files out of version control.
- The current recommendation method uses precomputed embeddings. Improving embedding quality will directly improve recommendation quality.

---

## Future Improvements

- Add a frontend interface for browsing songs and recommendations
- Add user-based recommendation history
- Support collaborative filtering
- Improve audio feature extraction
- Add lyric-based similarity using NLP
- Add search and filtering by artist
- Add Docker support
- Add automated tests for API endpoints
- Add deployment instructions
- Add a proper `requirements.txt`
- Add model/data documentation

---

## Contributing

Contributions are welcome.

To contribute:

1. Fork the repository
2. Create a new branch

```bash
git checkout -b feature/your-feature-name
```

3. Make your changes
4. Commit your work

```bash
git commit -m "Add your feature"
```

5. Push to your branch

```bash
git push origin feature/your-feature-name
```

6. Open a pull request

---

## License

No license file is currently specified in the repository.

If you plan to make this project open source, add a license such as MIT, Apache-2.0, or GPL depending on your intended usage.

---

## Author

Developed by [Eshahi](https://github.com/Eshahi).

---

## Acknowledgments

- Persian rap artists and music community
- Open-source Python ecosystem
- Django and Django REST Framework
- Pandas and NumPy for data processing
