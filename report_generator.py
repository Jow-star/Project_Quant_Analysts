import pandas as pd
from datetime import datetime
from data_fetcher import get_stock_price
from config import ASSETS

def generate_daily_report():
    report = []
    for asset in ASSETS:
        price_info = get_stock_price(asset)
        report.append({
            "Asset": asset,
            "Current": price_info["current"],
            "High": price_info["high"],
            "Low": price_info["low"]
        })
    df = pd.DataFrame(report)
    filename = f"report_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(filename, index=False)
    # return filename

