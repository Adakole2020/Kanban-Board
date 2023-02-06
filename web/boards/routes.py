from flask import render_template, url_for, redirect, Blueprint, flash, request, Response
from flask_login import login_user,logout_user, current_user, login_required
from web.models import Task, User, Board, BoardParticipant, BoardRolesEnum, TaskStateEnum
from web.boards.forms import (TaskForm, BoardForm, ParticipantForm)
from web import db

boards = Blueprint('boards', __name__)

@boards.route('/update_task', methods = ["POST"])
@login_required
def update_task():
    task_id = request.form["id"]
    new_state = request.form["state"]
    refr_task = Task.query.get(task_id)
    if refr_task:
        refr_task.state = new_state
        db.session.commit()
        return Response("Update has been made", status = 200)
    else:
        abort(401)
    
@boards.route('/remove_task', methods = ["POST"])
@login_required
def remove_task():
    task_id = request.form["id"]
    refr_task = Task.query.get(task_id)
    if refr_task:
        db.session.delete(refr_task)
        db.session.commit()
        flash("Task has successfully been deleted!!", "success")
        return Response("That task has been deleted", status = 200)
    else:
        flash("No valid task ID was supplied!!", "danger")
        abort(401)


@boards.route("/new_board", methods = ["GET", "POST"])
@login_required
def new_board():
    form = BoardForm()
    if form.validate_on_submit():
        board_name = form.name.data
        board_description = form.description.data
        board_participants = form.participants.entries           
        new_board = Board(name = board_name, description = board_description)
        db.session.add(new_board)
        db.session.flush()
        participants_list = [BoardParticipant(board_id = new_board.id, participant_id = current_user.id,
                                              role = BoardRolesEnum.ADMIN)] + [BoardParticipant(board_id = new_board.id, participant_id = int(participant.username.data),
                                                                                                role = participant.role.data) for participant in board_participants if int(participant.username.data) != current_user.id] 
        db.session.add_all(participants_list)
        db.session.commit()
        flash("Your board has now been created!!", "success")
        return redirect(url_for('boards.board', board_id = new_board.id))
    elif request.method == "GET":
        return render_template("new_board.html", form = form, templateParticipant = ParticipantForm(prefix = "participants-_-"))
    else:
        return render_template("new_board.html", form = form, templateParticipant = ParticipantForm(prefix = "participants-_-")), 400

@boards.route("/task/<int:board_id>", methods = ["POST"])
@login_required
def task(board_id):
    form = TaskForm()
    pres_board = Board.query.get_or_404(board_id)
    form.assignees.choices = [(str(user.participant_id), user.participant.username) for user in pres_board.participants]
    if form.validate_on_submit():
        tid = form.tid.data
        task_name = form.name.data
        task_content = form.content.data
        task_state = form.state.data
        task_assignees = form.assignees.data
        assignees_list = [User.query.get(int(assignee)) for assignee in task_assignees]
        assignees_list = [assignee for assignee in assignees_list if assignee is not None]
        roleCheck = BoardParticipant.query.get_or_404((board_id, current_user.id))
        if roleCheck.role.value <= 1:
            abort (403)
        if tid == "":
            new_task = Task(board_id = board_id, name = task_name, content = task_content, state = task_state, assignees = assignees_list)
            db.session.add(new_task)
            db.session.commit()  
            flash("The task has been created!!", "success")
        else:
            task = Task.query.get(int(tid))
            if task:
                task.name = task_name
                task.content = task_content
                task.state = task_state
                task.assignees = assignees_list
                db.session.commit()
                flash("The task has been updated!!", "success")
    return redirect(url_for('boards.board', board_id = board_id))
        
        
    
@boards.route("/board/<int:board_id>", methods = ['GET', 'POST'])
@login_required
def board(board_id):
    boardForm = BoardForm()
    templateParticipant = ParticipantForm(prefix = "participants-_-")
    pres_board = Board.query.get_or_404(board_id)
    role_check = BoardParticipant.query.get((board_id, current_user.id))
    if role_check is None:
       abort (403) 
    if boardForm.validate_on_submit():
        if role_check.role < 3:
            abort(403)
        pres_board.name = boardForm.name.data
        pres_board.description = boardForm.description.data
        board_participants = boardForm.participants.entries
        pres_entries = pres_board.participants
        for entry in pres_entries:
            db.session.delete(entry)
        db.session.commit()
        new_participants = [BoardParticipant(board_id = pres_board.id, participant_id = current_user.id, role = BoardRolesEnum.ADMIN)] + list(set([BoardParticipant(board_id = pres_board.id, participant_id = int(participant.username.data), role = participant.role.data) for participant in board_participants if int(participant.username.data) != current_user.id]))
        db.session.add_all(new_participants)
        db.session.commit()
        flash("Your board has been updated!", "success")
        return redirect(url_for("boards.board", board_id = board_id))
    elif request.method == "GET":    
        boardForm = BoardForm(name = pres_board.name, description = pres_board.description, participants = [{"username": participant.participant_id, "role": participant.role.value} for participant in pres_board.participants if participant.participant_id != current_user.id])
    taskForm = TaskForm()
    tasks = [task.to_dict() for task in pres_board.tasks]
    name = pres_board.name
    for task in tasks:
        task["assignees"] = [assignee["id"] for assignee in task["assignees"]]
    todo = [task for task in tasks if task['state'] == "Requested"]
    doing = [task for task in tasks if task['state'] == "In Progress"]
    done = [task for task in tasks if task['state'] == "Completed"]
    taskForm.assignees.choices = [(str(user.participant_id), user.participant.username) for user in pres_board.participants]
    return render_template('board_page.html', todo = todo, doing = doing, done = done, taskForm = taskForm, boardForm = boardForm, role = role_check.role, board_id = board_id, templateParticipant = templateParticipant)