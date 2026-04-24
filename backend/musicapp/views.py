from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Song
from .serializers import SongSerializer
from .analysis_utils import list_songs, get_beat_data, find_top_3_similar
import pandas as pd

@api_view(['GET'])
def song_list(request):
    """
    List all songs. Either from the DB or from CSV logic in analysis_utils.
    """
    # If you prefer DB usage:
    # songs = Song.objects.all()
    # serializer = SongSerializer(songs, many=True)
    # return Response(serializer.data)

    # Otherwise, from CSV logic:
    raw_songs = list_songs()  # e.g. returns [(artist, title), ...]
    data = []
    for (artist, title) in raw_songs:
        data.append({
            "artist": artist,
            "title": title
        })
    return Response(data)


@api_view(['GET'])
def song_detail(request):
    """
    Returns data for a given song: recommended tracks + beat-level data.
    Expects query params: ?artist=...&title=...
    """
    artist = request.GET.get("artist")
    title = request.GET.get("title")

    if not artist or not title:
        return Response({"error": "artist and title are required"}, status=400)

    # 1) find top 3 recommended
    top_3 = find_top_3_similar(artist, title)
    recs = [{"artist": a, "title": t} for (a, t) in top_3]

    # 2) get beat-level data from analysis_utils
    beats_df = get_beat_data(artist, title)  # typically a pd.DataFrame

    # -- Ensure numeric columns for Recharts --
    # If your CSV has columns like 'rms', 'zcr', 'mfcc_1', etc.,
    # convert them to numeric. Adjust column names as needed.
    numeric_cols = ["rms", "zcr", "mfcc_1"]
    for col in numeric_cols:
        if col in beats_df.columns:
            beats_df[col] = pd.to_numeric(beats_df[col], errors="coerce")

    # 3) convert to list-of-dict for JSON
    beat_data = beats_df.to_dict(orient="records")

    return Response({
        "artist": artist,
        "title": title,
        "recommended": recs,
        "beat_data": beat_data
    })
