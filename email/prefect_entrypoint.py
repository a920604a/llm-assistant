from pipeline import daily_papers_flow
from prefect.schedules import Cron

# 建立 Interval schedule
# 建立 Interval schedule
# 每天 06:00 台北時間 (等於 UTC 22:00)
interval_schedule = Cron("0 22 * * *", timezone="UTC")


# 使用 flow.serve 註冊 flow 並套用 schedule
daily_papers_flow.serve(
    schedule=interval_schedule,
    parameters={"top_k": 3},
)
