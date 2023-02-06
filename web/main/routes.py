from flask import render_template, url_for, redirect, Blueprint, flash
from flask_login import current_user
from web import db, bcrypt
from web.models import Task, User, Board, BoardParticipant, BoardRolesEnum, TaskStateEnum
main = Blueprint('main', __name__)


@main.before_app_first_request
def create_data():
    db.drop_all()
    db.create_all()
    hashed_password = bcrypt.generate_password_hash("Test123").decode('utf-8')
    new_user1 = User(username="Adakole", email="test@minerva.edu", password=hashed_password)
    new_user2 = User(username="Samuel", email = "cs162tests@minerva.kgi.edu", password=hashed_password)
    new_user3 = User(username="cs162tests", email = "test@uni.minerva.edu", password=hashed_password)
    db.session.add(new_user1)
    db.session.add(new_user2)
    db.session.add(new_user3)
    db.session.flush()
    new_board1 = Board(name = "Test Board", description = "This is a board aimed at testing the base functionality")
    new_board2 = Board(name = "Test Board 2", description = "This is a board aimed at testing the base functionality again")
    db.session.add(new_board1)
    db.session.add(new_board2)
    db.session.flush()
    new_task1 = Task(board_id = new_board1.id, name = "Test backend add task 1", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
    new_task2 = Task(board_id = new_board2.id, name = "Test backend add task 2", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
    new_task3 = Task(board_id = new_board1.id, name = "Test backend add task 3", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
    new_task4 = Task(board_id = new_board2.id, name = "Test backend add task 4", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
    new_task5 = Task(board_id = new_board1.id, name = "Test backend add task 5", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
    db.session.add_all([new_task1, new_task2, new_task3, new_task4, new_task5])
    db.session.commit()
    participant_1 = BoardParticipant(board_id = new_board1.id, participant_id = new_user1.id, role = BoardRolesEnum.ADMIN)
    participant_2 = BoardParticipant(board_id = new_board2.id, participant_id = new_user1.id, role = BoardRolesEnum.EDITOR)
    participant_3 = BoardParticipant(board_id = new_board2.id, participant_id = new_user3.id, role = BoardRolesEnum.ADMIN)
    participant_4 = BoardParticipant(board_id = new_board2.id, participant_id = new_user2.id, role = BoardRolesEnum.VIEWONLY)
    db.session.add_all([participant_1, participant_2, participant_3, participant_4])
    db.session.commit()
    

@main.route('/', methods = ["GET", "POST"])
def home():
    if current_user.is_authenticated:
        boards = [board.board for board in current_user.boards]
        length = len(boards)
        return render_template("index.html", boards = boards, length = length)
    else:
        flash("Login is required to view the homepage.", "info")
        return redirect(url_for('users.login'))