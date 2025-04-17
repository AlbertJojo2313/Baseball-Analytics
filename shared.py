from pathlib import Path
import pandas as pd

app_dir = Path(__file__).parent
pbp = pd.read_parquet(app_dir / 'data/play_by_play.parquet').set_index(['batter_name_y', 'if_fielding_alignment', 'of_fielding_alignment']).sort_index()
batters = list(i[0] for i in list(set(pbp.index)))
batters.sort()

