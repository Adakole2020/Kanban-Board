from web import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import enum
from sqlalchemy_serializer import SerializerMixin

class TaskStateEnum(enum.Enum):
    TODO = 'Requested'
    DOING = 'In Progress'
    DONE = 'Completed'
    
class BoardRolesEnum(enum.IntEnum):
    ADMIN = 3
    EDITOR = 2
    VIEWONLY = 1

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin, SerializerMixin):
    serialize_only = ('id', 'username', 'email')
    serialize_rules = ()
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), default = "default.svg")
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', secondary='taskToAssignee', back_populates='assignees')
    boards = db.relationship('BoardParticipant', back_populates = 'participant')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Board(db.Model, SerializerMixin):
    serialize_only = ('id', 'name', 'description', 'participants', 'tasks')
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(120), nullable = False)
    description = db.Column(db.String())
    participants = db.relationship('BoardParticipant', back_populates = 'board')
    tasks = db.relationship('Task', backref='board')

class Task(db.Model, SerializerMixin):
    serialize_only = ('id', 'board_id', 'name', 'state', 'content', 'assignees')
    serialize_rules = ()
    
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"))
    name = db.Column(db.String(120), nullable = False)
    state = db.Column(db.Enum(TaskStateEnum, values_callable=lambda x: [str(e.value) for e in TaskStateEnum]), nullable = False, default = TaskStateEnum.TODO)
    content = db.Column(db.String(), nullable = False)
    assignees = db.relationship('User', secondary='taskToAssignee', back_populates='tasks')
    
taskToAssignee = db.Table('taskToAssignee',
                    db.Column('task_id', db.Integer, db.ForeignKey("task.id"), primary_key = True),
                    db.Column('assignee_id', db.Integer, db.ForeignKey("user.id"), primary_key = True)) 
    
    
class BoardParticipant(db.Model, SerializerMixin):
    serialize_only = ('board_id', 'participant_id', 'participant')
    board_id = db.Column(db.Integer, db.ForeignKey("board.id"), primary_key = True)
    participant_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    role = db.Column(db.Enum(BoardRolesEnum, values_callable=lambda x: [str(e.value) for e in BoardRolesEnum]), nullable = False, default = BoardRolesEnum.VIEWONLY)
    board = db.relationship('Board', back_populates = 'participants')
    participant = db.relationship('User', back_populates = 'boards')
