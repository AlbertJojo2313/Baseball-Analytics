from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent
pbp = pd.read_parquet(app_dir / 'data/play_by_play.parquet').set_index(['batter', 'if_fielding_alignment', 'of_fielding_alignment'])
batters = dict(zip([str(i[0]) for i in set(pbp.index)], list(pbp['batter_name_y'])))
