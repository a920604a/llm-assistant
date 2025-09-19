from pipeline import daily_papers_flow
from prefect.schedules import Cron

# 建立 Interval schedule
# 建立 Interval schedule
# 每天 06:00 台北時間 (等於 UTC 22:00)
interval_schedule = Cron("0 22 * * *", timezone="UTC")


# 建議建立一個 Flow wrapper，把 Firebase 初始化放在這裡
daily_papers_flow.serve(
    schedule=interval_schedule,
    parameters={"top_k": 3},
)
