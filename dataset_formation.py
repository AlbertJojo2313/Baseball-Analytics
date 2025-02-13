from pybaseball import statcast, playerid_reverse_lookup
import pandas as pd

# Create a lookup dictionary for player names
def create_player_lookup():
    player_data = playerid_reverse_lookup(range(1000000), key_type='mlbam')  # Large range to fetch all players
    player_data['full_name'] = player_data['name_first'] + " " + player_data['name_last']
    return player_data.set_index('key_mlbam')['full_name'].to_dict()

PLAYER_LOOKUP = create_player_lookup()

# Define depth mappings for infield and outfield alignments
INFIELD_DEPTH_MAP = {
    "Standard": 1,
    "Shift": 2,
    "Shaded": 3,
    "Strategic infield alignment": 4
}

OUTFIELD_DEPTH_MAP = {
    "Standard": 1,
    "3 OF to one side of 2B": 2,
    "4th Outfielder": 3,
    "Strategic outfield alignment": 4
}

def get_batter_name(batter_id):
    """Retrieve player name using a preloaded dictionary."""
    return PLAYER_LOOKUP.get(batter_id, "Unknown Player")

def request(start_dt, end_dt):
    """Fetch Statcast data and process batter names and depth values."""
    df = statcast(start_dt=start_dt, end_dt=end_dt)

    required_columns = ['batter', 'if_fielding_alignment', 'of_fielding_alignment']
    if not all(col in df.columns for col in required_columns):
        print("Warning: Some expected columns are missing.")
        return df  

    df_filtered = df[required_columns].copy()

    # Map batter ID to player name
    df_filtered['batter_name'] = df_filtered['batter'].apply(get_batter_name)

    # Assign numerical depth values based on alignments
    df_filtered['if_fielding_depth'] = df_filtered['if_fielding_alignment'].map(INFIELD_DEPTH_MAP).fillna(0)
    df_filtered['of_fielding_depth'] = df_filtered['of_fielding_alignment'].map(OUTFIELD_DEPTH_MAP).fillna(0)

    # Remove duplicates
    df_filtered = df_filtered.drop_duplicates()

    return df_filtered

def write_df_to_file(df: pd.DataFrame, filename: str, fileformat: str = 'csv'):
    """Save DataFrame to a file in the specified format."""
    if df.empty:
        print("DataFrame is empty. No file written.")
        return

    file_format = fileformat.lower()
    output_file = f"{filename}.{file_format}"

    try:
        if file_format == 'csv':
            df.to_csv(output_file, index=False)
        elif file_format == 'excel':
            df.to_excel(output_file, engine='openpyxl', index=False)
        elif file_format == 'json':
            df.to_json(output_file, orient='records', indent=4)
        elif file_format == 'parquet':
            df.to_parquet(output_file, index=False)
        else:
            print(f"Unsupported file format '{file_format}'")
            return
        print(f"File successfully written: {output_file}")
    except Exception as e:
        print(f"Error writing the file: {e}")

def main():
    start_dt = "2024-06-01"
    end_dt = "2024-06-02"

    df = request(start_dt=start_dt, end_dt=end_dt)

    if df.empty:
        print("No data returned. Try adjusting the date range.")
    else:
        print(df.head())  # Display sample output
        write_df_to_file(df, "data", 'csv')

if __name__ == '__main__':
    main()
