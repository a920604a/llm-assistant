from datetime import datetime, timedelta

from arxiv_pipeline import arxiv_pipeline
from prefect.schedules import Cron

# 動態計算日期
today = datetime.utcnow()
date_to = today.strftime("%Y%m%d")
date_from = (today - timedelta(days=30)).strftime("%Y%m%d")  # 過去 30 天


# 建立 Interval schedule
# 每天 14:01 台北時間 (等於 UTC 06:01)
interval_schedule = Cron("5 6 * * *", timezone="UTC")


# 使用 flow.serve 註冊 flow 並套用 schedule
arxiv_pipeline.serve(
    schedule=interval_schedule,
    parameters={"date_from": date_from, "date_to": date_to, "max_results": 20},
)
