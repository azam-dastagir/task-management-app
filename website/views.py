from flask import Blueprint
from flask import request,jsonify
from .models import Task
from . import db, app, mail
from flask_login import login_required,current_user
from datetime import datetime,timedelta
from flask_mail import Message
from sqlalchemy import and_
import time


current_datetime = datetime.now()


views = Blueprint('views',__name__)

@views.route('/view_tasks', methods = ['POST','GET'])
@login_required
def view_task():
    user_id = current_user.id
    get_overdues = request.args.get('get_overdues')
    get_dues = request.args.get('get_dues')
    category = request.args.get('category')

    base_query = Task.query.filter_by(user_id = user_id)
    
    if get_overdues and category or get_overdues:
        base_query = Task.query.filter(and_(Task.user_id == user_id, Task.due_date < current_datetime))
        all_tasks = base_query.all()
        if category:
            categorised_overdue_tasks = []
            for task in all_tasks:
                if task.category == category:
                    categorised_overdue_tasks.append(task)
            sorted_tasks = sorted(categorised_overdue_tasks, key = lambda task: task.due_date)
            tasks_as_dict = [task.to_dict() for task in sorted_tasks]
            return jsonify(tasks_as_dict)
        
        sorted_tasks = sorted(all_tasks, key = lambda task : task.due_date )
        tasks_as_dict = [overdue_task.to_dict() for overdue_task in sorted_tasks]
        return jsonify(tasks_as_dict)
    
    if get_dues and category or get_dues:
        base_query = Task.query.filter(and_(Task.user_id == user_id ,Task.due_date > current_datetime))
        all_tasks = base_query.all()
        if category:
            categorised_due_tasks = []
            for task in all_tasks:
                if task.category == category:
                    categorised_due_tasks.append(task)
            sorted_tasks = sorted(categorised_due_tasks, key = lambda task:task.due_date)
            tasks_as_dict = [task.to_dict() for task in sorted_tasks]
            return jsonify(tasks_as_dict)

        sorted_tasks = sorted(all_tasks, key = lambda task : task.due_date )

        tasks_as_dict = [task.to_dict() for task in sorted_tasks]
        return jsonify(tasks_as_dict)
    
    if category:
        base_query = Task.query.filter_by(user_id = user_id,category = category)
        all_tasks = base_query.all()
        sorted_tasks = sorted(all_tasks, key = lambda task : task.due_date )

        tasks_as_dict = [task.to_dict() for task in sorted_tasks]
        return jsonify(tasks_as_dict)
    
    all_tasks = base_query.all()
    sorted_tasks = sorted(all_tasks, key = lambda task : task.due_date )
    tasks_as_dict = [task.to_dict() for task in sorted_tasks]
    return jsonify(tasks_as_dict)


    '''
    if get_overdues:
        overdue_tasks = []
        current_datetime = datetime.now()
        for task in all_tasks:
           # due_date_datetime = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S')
            if task.due_date < current_datetime:
                overdue_tasks.append(task)
        tasks_as_dict = [overdue_task.to_dict() for overdue_task in overdue_tasks]
        return jsonify(tasks_as_dict)
        
    if get_dues:
        due_tasks = []
        current_datetime = datetime.now()
        for task in all_tasks:
            if task.due_date > current_datetime:
                due_tasks.append(task)

        tasks_in_order = sorted(due_tasks, key = lambda task : task.due_date)



        tasks_as_dict = [due_task.to_dict() for due_task in tasks_in_order]
        return jsonify(tasks_as_dict)
        '''
    


@views.route('/update_task/<int:task_id>', methods=['POST','PUT'])
@login_required
def update_task(task_id):
    try:
        # Fetch the task by ID and user ID
        user_id = current_user.id
        task = Task.query.filter_by(cid=task_id, user_id=user_id).first()

        if not task:
            return jsonify({"message": "Task not found"}), 404

        # Get data from the request
        due_date = request.form.get('due_date')
        description = request.form.get('description')

        # Update task fields if data is provided
        if due_date is not None:
            task.due_date = due_date

        if description is not None:
            task.description = description

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "Task updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
    

def send_notification_3_days(task):
    email = current_user.email
    message = Message('Task due soon',
                          recipients=[email],
                          sender= app.config['MAIL_DEFAULT_SENDER'])
    message.body = f"Your task '{task.title}' is due in 3 days, Don't forget to complete it"
    mail.send(message)

def send_notification_1_day(task):
    email = current_user.email
    message = Message('Task due soon',
                          recipients=[email],
                          sender= app.config['MAIL_DEFAULT_SENDER'])
    message.body = f"Your task '{task.title}' is due in 1 day, Don't forget to complete it"
    mail.send(message)



@views.route('/add_task',methods = ['GET','POST'])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date =  request.form.get('due_date')
    category =  request.form.get('category')
    user_id =  current_user.id

    new_task = Task(title=title, description=description, due_date=due_date, category=category, user_id=user_id)

    db.session.add(new_task)
    db.session.commit()
    send_notification_1_day(new_task)

    return "New Task Added!"

@views.route('/run_scheduler')
def start_scheduler():
    code = request.args.get('code')
    base_query = Task.query.filter(and_(Task.user_id == current_user.id ,Task.due_date > current_datetime))
    all_tasks = base_query.all()
    if code:
        try:
            for task in all_tasks:
                if not task.notify_for_3_days and task.due_date - current_datetime <= timedelta(days = 3):
                    send_notification_3_days(task)
                    task.notify_for_3_days = True
                    db.session.commit()
                if not task.notify_for_1_day and task.due_date - current_datetime <= timedelta(days= 1):
                    send_notification_1_day(task)
                    task.notify_for_1_day = True
                    db.session.commit()
            print("scheduler is sent mails now going to sleep")
            #time.sleep(300)
        except Exception as e:
            print(f"error {e}")
        return "Task Done"
        
    