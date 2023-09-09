import random
import pandas as pd
from datetime import datetime, timedelta

def generate_city_gmv(date):
    city_levels = ["一线城市", "二线城市", "三线城市", "四线城市", "五线城市"]
    gmv = [round(random.uniform(10000, 50000), 2) for _ in range(len(city_levels))]
    return pd.DataFrame({'日期': date, '城市线级': city_levels, 'GMV': gmv})
