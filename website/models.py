from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Task(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000))
    due_date = db.Column(db.DateTime, nullable = False)
    category = db.Column(db.String(50), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = "CASCADE"), nullable=False)
    notify_for_1_day = db.Column(db.Boolean, default = False)
    notify_for_3_days = db.Column(db.Boolean, default = False)

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def __init__(self, title, description, due_date, category, user_id):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.category = category
        self.user_id = user_id

    def __repr__(self):
        return f"<Task(cid={self.cid}, title='{self.title}', user_id={self.user_id})>"
    
    def to_dict(self):
        task_dict = {
        'id': self.cid,
        'title': self.title,
        'description': self.description,
        'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S'),
        'category': self.category,
        'user_id': self.user_id,
        'created_at' : self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'completed' : self.completed
        #'updated_at' : self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        if self.updated_at:
            task_dict['updated_at:'] = self.updated_at.strftime('%Y-%m-%d %H:%M:S')
        else:
            task_dict['updated_at:'] = "Not Updated!"

        return task_dict

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255))
    tasks = db.relationship("Task", backref='owner', passive_deletes=True)
    

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password