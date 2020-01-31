import os
import glob
import datetime
import pandas as pd


def streaming_hist_to_csv(output=None, glb='data/StreamingHistory*.json'):
    streaming_hist_files = glob.glob(glb)

    hist_dfs = []
    for f in streaming_hist_files:
        df = pd.read_json(f)
        hist_dfs.append(df)

    hist_df = pd.concat(hist_dfs)

    print(f'Shape read: {hist_df.shape}')

    if not output:
        timestamp = datetime.datetime.utcnow()
        timestamp = timestamp.strftime('%y_%d_%m__%H_%M_%S')
        output = os.path.join('data', f'stream_hist_{timestamp}.csv')

    hist_df.to_csv(output, index=False)


if __name__ == '__main__':
    streaming_hist_to_csv()
