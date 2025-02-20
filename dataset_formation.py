from pybaseball import statcast, playerid_reverse_lookup
import pandas as pd

# Create a lookup dictionary for player names
def create_player_lookup():
    player_data = playerid_reverse_lookup(range(1000000), key_type='mlbam')  # Large range to fetch all players
    player_data['name_first'] = player_data['name_first'].str.capitalize()
    player_data['name_last'] = player_data['name_last'].str.capitalize()
    player_data['full_name'] = player_data['name_last'] + "," + player_data['name_first']
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

def get_pitcher_name(pitcher_id):
    return PLAYER_LOOKUP.get(pitcher_id, "Unkown Player")

def get_fielder_name(fielder_id):
    return PLAYER_LOOKUP.get(fielder_id, "Unkown Player")
    
def request(start_dt, end_dt):
    """Fetch Statcast data and process batter names and depth values."""
    df = statcast(start_dt=start_dt, end_dt=end_dt)

    if df.empty:
        print("No data found for this given range")
        return df ## Returns an empty dataframe

    required_columns = ['batter', 'stand', 'if_fielding_alignment', 'of_fielding_alignment','pitcher', 'fielder_2','fielder_3','fielder_4','fielder_5','fielder_6','fielder_7','fielder_8','fielder_9', 'woba_value', 'woba_denom', 'iso_value']

    if not all(col in df.columns for col in required_columns):
        print("Warning: Some expected columns are missing.")
        return df  

    df_filtered = df[required_columns].copy()
    df_filtered['pitcher'] = df_filtered['pitcher'].apply(get_pitcher_name)

    filter_cols = ['fielder_2','fielder_3','fielder_4','fielder_5','fielder_6','fielder_7','fielder_8','fielder_9']

    # Map batter ID to player name
    df_filtered['batter_name'] = df_filtered['batter'].apply(get_batter_name)
    #df_filtered['pitcher_name'] = df_filtered['pitcher'].apply(get_pitcher_name)
    """
    df_filtered['fielder_2'] = df_filtered['fielder_2'].apply(get_fielder_name)
    df_filtered['fielder_3'] = df_filtered['fielder_3'].apply(get_fielder_name)
    df_filtered['fielder_4'] = df_filtered['fielder_4'].apply(get_fielder_name)
    df_filtered['fielder_5'] = df_filtered['fielder_5'].apply(get_fielder_name)
    df_filtered['fielder_6'] = df_filtered['fielder_6'].apply(get_fielder_name)
    df_filtered['fielder_7'] = df_filtered['fielder_7'].apply(get_fielder_name)
    df_filtered['fielder_8'] = df_filtered['fielder_8'].apply(get_fielder_name)
    df_filtered['fielder_9'] = df_filtered['fielder_9'].apply(get_fielder_name)
    """
    for col in filter_cols:
        df_filtered[col] = df_filtered[col].apply(get_fielder_name)

    # Assign numerical depth values based on alignments
    df_filtered['if_fielding_depth'] = df_filtered['if_fielding_alignment'].map(INFIELD_DEPTH_MAP).fillna(0).astype(int)
    df_filtered['of_fielding_depth'] = df_filtered['of_fielding_alignment'].map(OUTFIELD_DEPTH_MAP).fillna(0).astype(int)

    df_filtered = df_filtered.rename(columns={"woba_value":"wOBA", "woba_denom":"wOBA_Denom", "iso_value":"ISO"})

    # Remove duplicates
    df_filtered = df_filtered.drop_duplicates(subset=['batter'])

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
    start_dt = "2022-04-07"
    end_dt = "2024-09-29"

    df = request(start_dt=start_dt, end_dt=end_dt)

    if df.empty:
        print("No data returned. Try adjusting the date range.")
    else:
        print(df.head())  # Display sample output
        write_df_to_file(df, "data", 'csv')

if __name__ == '__main__':
    main()
