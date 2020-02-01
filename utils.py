import os
import re
import glob
import datetime
import pandas as pd
import lyricsgenius
from tqdm import tqdm


def streaming_hist_to_csv(output=None, glb='data/StreamingHistory*.json'):
    streaming_hist_files = glob.glob(glb)

    hist_dfs = []
    for file in streaming_hist_files:
        df = pd.read_json(file)
        hist_dfs.append(df)

    stream_hist_df = pd.concat(hist_dfs)

    print(f'Shape read: {stream_hist_df.shape}')

    if not output:
        timestamp = datetime.datetime.utcnow()
        timestamp = timestamp.strftime('%y_%d_%m__%H_%M_%S')
        output = os.path.join('data', f'stream_hist_{timestamp}.csv')

    stream_hist_df.to_csv(output, index=False)


def _build_file_name(artist_name, track_name):
    artist_name = artist_name.replace("'", '').lower()
    track_name = track_name.replace("'", '').lower()
    artist_name = re.sub(r'\W', '_', artist_name)
    track_name = re.sub(r'\W', '_', track_name)

    return f'{track_name}_by_{artist_name}.json'


def get_genius_data(stream_hist_df, token, output='data/songs', playcount_min=5, max_songs=float('inf')):
    genius = lyricsgenius.Genius(token, verbose=False)

    cols = ['artistName', 'trackName']
    song_df = stream_hist_df[cols]
    song_df = song_df.groupby(cols).size()
    song_df = song_df.sort_values(ascending=False)
    song_df.name = 'play_count'
    song_df = song_df.reset_index()
    song_df = song_df[song_df['play_count'] >= playcount_min]

    max_iter = min([song_df.shape[0], max_songs])
    progress_iter = tqdm(song_df.iterrows(), total=max_iter)
    for i, row in progress_iter:
        file_name = _build_file_name(row['artistName'], row['trackName'])
        file_name = os.path.join(output, file_name)

        if i > max_songs:
            break

        if os.path.exists(file_name):
            continue

        try:
            song = genius.search_song(row['trackName'], row['artistName'])
        # noinspection PyBroadException
        except:
            continue

        if song:
            song.save_lyrics(file_name, sanitize=False, verbose=False)


if __name__ == '__main__':
    import json

    with open('api_keys.json', 'r') as f:
        API_KEYS = json.load(f)

    # streaming_hist_to_csv()

    files = glob.glob('data/stream_hist_*.csv')
    hist_df = pd.concat(pd.read_csv(f) for f in files)

    get_genius_data(hist_df,
                    token=API_KEYS['genius']['token'],
                    # max_songs=20,
                    )
