# apps/ui/dataloader/data_loader.py

from dataloader.db_utils import run_query

def get_available_road_names(resolution: str):
    query = "SELECT DISTINCT road_name FROM road_traffic_stats_minute WHERE resolution = :resolution"
    return run_query(query, {"resolution": resolution})['road_name'].tolist()

def get_period_bounds(resolution: str, road_name: str):
    query = f"""
        SELECT MIN(period) AS min_period, MAX(period) AS max_period
        FROM road_traffic_stats_{resolution}
        WHERE road_name = :road_name
    """
    df = run_query(query, {"road_name": road_name})
    return df["min_period"][0].to_pydatetime(), df["max_period"][0].to_pydatetime()

def load_traffic_data(resolution: str, road_name: str, start_date, end_date):
    query = f"""
        SELECT period, road_name, average_speed, average_travel_time
        FROM road_traffic_stats_{resolution}
        WHERE road_name = :road_name
        AND period BETWEEN :start AND :end
        ORDER BY period
    """
    return run_query(query, {
        "road_name": road_name,
        "start": start_date,
        "end": end_date
    })
