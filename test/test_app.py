import unittest
from web import create_app, bcrypt, db
from web.models import Task, User, Board, BoardParticipant, BoardRolesEnum, TaskStateEnum
import re
import web.config.config as configModule
from furl import furl
    
    
    
class AuthManager():
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password
        
    def __enter__(self):
        rv = self.client.get('/login')
        self.response = self.client.post('/login', data=dict(
        username=self.username,
        password=self.password
        ), follow_redirects=True)
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.get("/logout")
        
class DbContext():
    def __init__(self):
        pass
    def __enter__(self):
        hashed_password = bcrypt.generate_password_hash("Test123").decode('utf-8')
        self.new_user1 = User(username="Adakole", email="test@minerva.edu", password=hashed_password)
        self.new_user2 = User(username="Samuel", email = "cs162tests@minerva.kgi.edu", password=hashed_password)
        self.new_user3 = User(username="cs162tests", email = "test@uni.minerva.edu", password=hashed_password)
        db.session.add(self.new_user1)
        db.session.add(self.new_user2)
        db.session.add(self.new_user3)
        db.session.flush()
        self.new_board1 = Board(name = "Test Board", description = "This is a board aimed at testing the base functionality")
        self.new_board2 = Board(name = "Test Board 2", description = "This is a board aimed at testing the base functionality again")
        db.session.add(self.new_board1)
        db.session.add(self.new_board2)
        db.session.flush()
        self.new_task1 = Task(board_id = self.new_board1.id, name = "Test backend add task 1", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
        self.new_task2 = Task(board_id = self.new_board2.id, name = "Test backend add task 2", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
        self.new_task3 = Task(board_id = self.new_board1.id, name = "Test backend add task 3", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
        self.new_task4 = Task(board_id = self.new_board2.id, name = "Test backend add task 4", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
        self.new_task5 = Task(board_id = self.new_board1.id, name = "Test backend add task 5", state = TaskStateEnum.TODO, content = "Tested the backend service for adding tasks")
        db.session.add_all([self.new_task1, self.new_task2, self.new_task3, self.new_task4, self.new_task5])
        db.session.commit()
        self.participant_1 = BoardParticipant(board_id = self.new_board1.id, participant_id = self.new_user1.id, role = BoardRolesEnum.ADMIN)
        self.participant_2 = BoardParticipant(board_id = self.new_board2.id, participant_id = self.new_user1.id, role = BoardRolesEnum.EDITOR)
        self.participant_3 = BoardParticipant(board_id = self.new_board2.id, participant_id = self.new_user3.id, role = BoardRolesEnum.ADMIN)
        self.participant_4 = BoardParticipant(board_id = self.new_board2.id, participant_id = self.new_user2.id, role = BoardRolesEnum.VIEWONLY)
        db.session.add_all([self.participant_1, self.participant_2, self.participant_3, self.participant_4])
        db.session.commit()
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        db.drop_all()
        
        
def new_board(client, name, participants, description):
    rv = client.get('/new_board')
    return client.post('/new_board', data=dict(
        name=name,
        participants=participants,
        description = description
    ), follow_redirects=True)
        
def task(client, board_id, name, participants, description, tid = ""):
    return client.post('/task/{board_id}', data=dict(
        name=name,
        tid = tid,
        participants=participants,
        description = description
    ), follow_redirects=True) 
        
def board(client, id, method, name = None, participants = [], description = None):
    rv = client.get('/board/{id}')
    if method == "GET":
        return rv
    return client.post('/board/id', data=dict(
        name=name,
        participants=participants,
        description = description
    ), follow_redirects=True)
        

        
        
def register(client, username, email, password1, password2):
    rv = client.get('/register')
    return client.post('/register', data=dict(
        username=username,
        email=email,
        password = password1, 
        confirm_password = password2,
    ), follow_redirects=True)
    
        
class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class = configModule.TestConfig())
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.ctx.pop()
        self.client = None
        
    
    
    def test_backend_board_creation(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                self.assertEqual(contextDB.new_board1.to_dict(), {'participants': [
                    {'participant': {'username': 'Adakole', 'email': 'test@minerva.edu', 'id': 1}, 'board_id': 1, 'participant_id': 1}], 
                                                                  'description': 'This is a board aimed at testing the base functionality', 'name': 'Test Board', 'tasks': [{'assignees': [], 'name': 'Test backend add task 1', 'state': 'Requested', 'board_id': 1, 'content': 'Tested the backend service for adding tasks', 'id': 1}, {'assignees': [], 'name': 'Test backend add task 3', 'state': 'Requested', 'board_id': 1, 'content': 'Tested the backend service for adding tasks', 'id': 3}, {'assignees': [], 'name': 'Test backend add task 5', 'state': 'Requested', 'board_id': 1, 'content': 'Tested the backend service for adding tasks', 'id': 5}], 'id': 1})
                self.assertEqual(contextDB.new_board2.to_dict(), {'participants': [{'participant': {'username': 'Adakole', 'email': 'test@minerva.edu', 'id': 1}, 'board_id': 2, 'participant_id': 1}, {'participant': {'username': 'Samuel', 'email': 'cs162tests@minerva.kgi.edu', 'id': 2}, 'board_id': 2, 'participant_id': 2}, {'participant': {'username': 'cs162tests', 'email': 'test@uni.minerva.edu', 'id': 3}, 'board_id': 2, 'participant_id': 3}], 'description': 'This is a board aimed at testing the base functionality again', 'name': 'Test Board 2', 'tasks': [{'assignees': [], 'name': 'Test backend add task 2', 'state': 'Requested', 'board_id': 2, 'content': 'Tested the backend service for adding tasks', 'id': 2}, {'assignees': [], 'name': 'Test backend add task 4', 'state': 'Requested', 'board_id': 2, 'content': 'Tested the backend service for adding tasks', 'id': 4}], 'id': 2})
            
            
            
    def test_backend_user_creation(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                users = User.query.all()
                users = [user.to_dict()["email"] for user in users]
                self.assertEqual(users, ['test@minerva.edu', 'cs162tests@minerva.kgi.edu', 'test@uni.minerva.edu'])
                self.assertEqual(contextDB.new_user1.to_dict()["email"], 'test@minerva.edu')
                self.assertEqual(contextDB.new_user2.to_dict()["email"], 'cs162tests@minerva.kgi.edu')
                self.assertEqual(contextDB.new_user3.to_dict()["email"], 'test@uni.minerva.edu')
    
    def test_backend_task_creation(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                tasks = [task.to_dict() for task in Task.query.all()]
                self.assertEqual(tasks, [{'assignees': [], 'board_id': 1, 'id': 1, 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'name': 'Test backend add task 1'}, 
                 {'assignees': [], 'board_id': 2, 'id': 2, 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'name': 'Test backend add task 2'}, 
                 {'assignees': [], 'board_id': 1, 'id': 3, 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'name': 'Test backend add task 3'}, 
                 {'assignees': [], 'board_id': 2, 'id': 4, 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'name': 'Test backend add task 4'}, 
                 {'assignees': [], 'board_id': 1, 'id': 5, 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'name': 'Test backend add task 5'}])

    def test_board_participant_connection(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                self.assertEqual(contextDB.participant_1.to_dict(), {'participant_id': 1, 'participant': {'email': 'test@minerva.edu', 'username': 'Adakole', 'id': 1}, 'board_id': 1})
                self.assertEqual(contextDB.participant_2.to_dict(), {'board_id': 2, 'participant_id': 1, 'participant': {'email': 'test@minerva.edu', 'username': 'Adakole', 'id': 1}})
                self.assertEqual(contextDB.participant_3.to_dict(), {'board_id': 2, 'participant_id': 3, 'participant': {'email': 'test@uni.minerva.edu', 'username': 'cs162tests', 'id': 3}})
                self.assertEqual(contextDB.participant_4.to_dict(), {'board_id': 2, 'participant_id': 2, 'participant': {'email': 'cs162tests@minerva.kgi.edu', 'username': 'Samuel', 'id': 2}})
                self.assertEqual(contextDB.participant_1.role.value, 3)
                self.assertEqual(contextDB.participant_2.role.value, 2)
                self.assertEqual(contextDB.participant_3.role.value, 3)
                self.assertEqual(contextDB.participant_4.role.value, 1)

            
            
    def test_board_task_connection(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                self.assertEqual(contextDB.new_task1.to_dict(), {'id': 1, 'name': 'Test backend add task 1', 'assignees': [], 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'board_id': 1})
                self.assertEqual(contextDB.new_task2.to_dict(), {'id': 2, 'name': 'Test backend add task 2', 'assignees': [], 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'board_id': 2})
                self.assertEqual(contextDB.new_task3.to_dict(), {'id': 3, 'name': 'Test backend add task 3', 'assignees': [], 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'board_id': 1})
                self.assertEqual(contextDB.new_task4.to_dict(), {'id': 4, 'name': 'Test backend add task 4', 'assignees': [], 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'board_id': 2})
                self.assertEqual(contextDB.new_task5.to_dict(), {'id': 5, 'name': 'Test backend add task 5', 'assignees': [], 'content': 'Tested the backend service for adding tasks', 'state': 'Requested', 'board_id': 1})
                board1_tasks = [task.to_dict()["name"] for task in contextDB.new_board1.tasks]
                board2_tasks = [task.to_dict()["name"] for task in contextDB.new_board2.tasks]
                self.assertEqual(board1_tasks, ['Test backend add task 1', 'Test backend add task 3', 'Test backend add task 5'])
                self.assertEqual(board2_tasks, ['Test backend add task 2', 'Test backend add task 4'])
            
    def test_addDrop_update(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    response = self.client.post("/update_task", data={"id": 1, "state": "In Progress"})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual("Update has been made", response.get_data(as_text=True))
                    form = TaskForm.query.get(1)
                    self.assertEqual(form, None)
                    self.assertEqual(form.state.value, "In Progress")
        
    def test_remove_update(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    response = self.client.post("/remove_task", data={"id": 1})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual("Update has been made", response.get_data(as_text=True))
                    form = TaskForm.query.get(1)
                    self.assertEqual(form, None)
    
    def test_bad_user_login(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.cam", "Test123") as auth:
                    test_login1 = auth.response
                with AuthManager(self.client, "test@minerva.c0m", "Test123") as auth:
                    test_login2 = auth.response
                self.assertEqual(test_login1.data, 401)
                self.assertEqual(test_login2.data, 401)
        
    def test_good_user_login(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@uni.minerva.edu", "Test123") as auth:
                    test_login1 = auth.response
                with AuthManager(self.client, "cs162tests@minerva.kgi.edu", "Test123") as auth:
                    test_login2 = auth.response
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_login3 = auth.response
                self.assertEqual(test_login1.data, 200)
                self.assertEqual(test_login2.data, 200)
                self.assertEqual(test_login3.data, 200)
        
    def test_bad_register(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                test_register1 = register(self.client, 'adakole1', "finale@uni.minerva.edu", "test123", "Test123");
                test_register2 = register(self.client, 'adakole', "finale@uni.minerva.edu", "testing123", "tester123");
                self.assertIn(b'Already Have An Account?', test_register1.data)
                self.assertIn(b'Already Have An Account?', test_register2.data)
                
                
    def test_good_register(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                test_register1 = register(self.client, 'adakole123', "finale@uni.minerva.edu", "Test123", "Test123");
                test_register2 = register(self.client, 'samuel123', "finale123@uni.minerva.edu", "testing123", "tester123");
                self.assertIn(b'Need An Account?', test_register1.data)
                self.assertIn(b'Need An Account?', test_register2.data)
        
        
    def test_new_board(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_new_board1 = new_board(self.client, "test board in 1", [], None)
                    test_new_board2 = new_board(self.client, "test board in 2", [], "A board to show new board capabilities")
                    test_new_board3 = new_board(self.client, None, [], "A board to show new board capabilities")
                    self.assertIn(b'Confirm New Board', test_new_board1.data)
                    self.assertIn(b'Edit Board', test_new_board2.data)
                    self.assertIn(b'Confirm New Board', test_new_board3.data)
                
    def test_new_task(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_new_task1 = task(self.client, 1, "Test add task once", [], "Tested the add task service", tid = "")
                    test_new_task2 = task(self.client, 2, "Test add task twice", [], 'Tested the add task service again', tid = "")
                    test_new_task3 = task(self.client, 2, "Test add task thrice", [], None, tid = "")
                    self.assertEqual(test_new_task1.data, "/board/1")
                    self.assertEqual(test_new_task2.data, "/board/2")
                    self.assertEqual(test_new_task3.data, "/board/2")
                    self.assertEqual(test_new_task1.status, 200)
                    self.assertEqual(test_new_task2.status, 200)
                    self.assertEqual(test_new_task2.status, 200)
                    self.assertNotEqual(Task.query.filter_by(name = "Test add task once").first(), None)
                    self.assertNotEqual(Task.query.filter_by(name = "Test add task twice").first(), None)
                    self.assertEqual(Task.query.filter_by(name = "Test add task thrice").first(), None)
                    
                    
                    
    def test_update_task(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_update_task1 = task(self.client, 1, "Test update task to me once", [], "Tested the update task service", tid = 1)
                    test_update_task2 = task(self.client, 2, "Test update task to me twice", [], 'Tested the update task service again', tid = 2)
                    test_update_task3 = task(self.client, 2, "Test update task to me thrice", [], "", tid = 3)
                    self.assertEqual(test_update_task1.data, "/board/1")
                    self.assertEqual(test_update_task1.data, "/board/2")
                    self.assertEqual(test_update_task1.status_code, 200)
                    self.assertEqual(test_update_task1.status_code, 200)
                    self.assertNotEqual(Task.query.filter_by(name = "Test update task to me once").first(), None)
                    self.assertNotEqual(Task.query.filter_by(name = "Test update task to me twice").first(), None)
                    self.assertEqual(Task.query.filter_by(name = "Test update task to me thrice").first(), None)
                    self.assertEqual(Task.query.get(1).name, "Test update task to me once")
                    self.assertEqual(Task.query.get(2).name, "Test update task to me twice")
                    self.assertNotEqual(Task.query.get(3).name, "Test update task to me thrice")
                    
                    
    def test_get_board(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_get_board1 = board(self.client, 1, "GET")
                    test_get_board2 = board(self.client, 2, "GET")
                    test_get_board3 = board(self.client, 3, "GET")
                    test_get_board4 = board(self.client, 12, "GET")
                    self.assertEqual(test_get_board1.data, "/board/1")
                    self.assertEqual(test_get_board2.data, "/board/2")
                    self.assertEqual(test_get_board1.status_code, 200)
                    self.assertEqual(test_get_board2.status_code, 200)
                    self.assertEqual(test_get_board3.status_code, 404)
                    self.assertEqual(test_get_board4.status_code, 404)
                    
    def test_update_board(self):
        with self.app.app_context():
            with DbContext() as contextDB:
                with AuthManager(self.client, "test@minerva.edu", "Test123") as auth:
                    test_update_board1 = board(self.client, 1, "POST", "Test updated board once", [], "This is a test board to show the updated copy")
                    test_update_board2 = board(self.client, 2, "POST", "Test updated board twice", [], "This is a test board to show the updated copy")
                    test_update_board3 = board(self.client, 3, "POST", "Test updated board thrice", [], "This is a test board to show the updated copy")
                    self.assertEqual(test_update_board1.data, "/board/1")
                    self.assertEqual(test_update_board1.status_code, 200)
                    self.assertEqual(test_update_board2.status_code, 403)
                    self.assertEqual(test_update_board3.status_code, 404)
                    self.assertNotEqual(Board.query.filter_by(name = "Test updated board once").first(), None)
                    self.assertEqual(Board.query.filter_by(name = "Test updated board twice").first(), None)
                    self.assertEqual(Board.query.filter_by(name = "Test updated board thrice").first(), None)
                    self.assertEqual(Board.query.get(1).name, "Test update task to me once")
            
        

if __name__ == "__main__":
    unittest.main()