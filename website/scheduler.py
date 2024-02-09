from .views import send_notification_1_day,send_notification_3_days
from flask_login import current_user
from .models import Task
from sqlalchemy import and_
from datetime import datetime,timedelta
import time

current_datetime = datetime.now()

base_query = Task.query.filter(and_(Task.user_id == current_user.id ,Task.due_date > current_datetime))

all_tasks = base_query.all()
def run_scheduler():
    while True:
        try:
            for task in all_tasks:
                if not task.notify_for_3_day and task.due_date - current_datetime <= timedelta(days = 3):
                    send_notification_3_days(task)
                    task.notify_for_3_day = True
                    if not task.notify_for_1_day and task.due_date - current_datetime <= timedelta(days= 1):
                        send_notification_1_day(task)
                        task.notify_for_1_day = True
            time.sleep(300)
        except Exception as e:
            print(f"error {e}")
    