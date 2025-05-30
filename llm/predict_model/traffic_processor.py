import pandas as pd


def process_traffic_status(status_str):
    """ transform traffic_status_list column into numerical features"""
    if pd.isna(status_str):
        status_str = "{}"

    status_str = status_str.strip('{}')
    statuses = [s.strip() for s in status_str.split(',') if s.strip()]

    if not statuses:  # if the list is empty after treatment
        return pd.Series({
            'freeFlow_ratio': 0,
            'heavy_ratio': 0,
            'congested_ratio': 0,
            'unknown_ratio': 1,  # all unknown statuses
            'status_count': 0
        })

    status_counts = pd.Series(statuses).value_counts()
    total = len(statuses)

    features = {
        'freeFlow_ratio': status_counts.get('freeFlow', 0) / total,
        'heavy_ratio': status_counts.get('heavy', 0) / total,
        'congested_ratio': status_counts.get('congested', 0) / total,
        'unknown_ratio': status_counts.get('unknown', 0) / total,
        'status_count': total
    }
    return pd.Series(features)
