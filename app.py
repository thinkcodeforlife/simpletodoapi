from flask import Flask, request
from flask_restful import Resource, Api, fields, marshal

from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import ToDoModel, UserModel

api = Api(app)


# ==================================================
user_fields =  {
    "name": fields.String,
    "email": fields.String
}

def get_users():
    return UserModel.get_all_users()

class UserEndPoint(Resource):
    def get(self, user_id):
        requested_user = UserModel.get_one_user(user_id)
        return {"requested_user": marshal(requested_user, user_fields)}

    def put(self, user_id):
        new_user_obj = {
            "name": request.form['name'],
            "email": request.form['email'],
            "password": request.form['password']
        }
        new_user = UserModel(new_user_obj)
        print("new_user:", new_user)
        new_user.save()
        return {"new_user": marshal(new_user, user_fields)}

api.add_resource(UserEndPoint, '/api/v1/users/<string:user_id>')


# ==================================================
user_todo_list = {
    "id": fields.Integer,
    "todo": fields.String
}

user_todos_fields =  {
    "name": fields.String,
    "email": fields.String,
    "todos": fields.List(fields.Nested(user_todo_list))
}


class UserTodos(Resource):
    def get(self, user_id):
        user_todos = UserModel.get_user_todos(user_id)
        print("user_todos:", user_todos)
        return {"user": marshal(user_todos, user_todos_fields)}

api.add_resource(UserTodos, '/api/v1/users/<string:user_id>/todos')


# ==================================================
class UserList(Resource):
    def get(self):
        users = get_users()
        return {"users": marshal(users, user_fields)}

api.add_resource(UserList, '/api/v1/users')


# ==================================================
todo_fields =  {
    "id": fields.Integer,
    "todo": fields.String,
    "owner_id": fields.Integer
}

def get_todos():
    return ToDoModel.get_all_todos()


class TodoSimple(Resource):
    def get(self, todo_id):
        requested_todo = ToDoModel.get_one_todo(todo_id)
        print("requested_todo:", requested_todo)
        return {"requested_todo": marshal(requested_todo, todo_fields)}

    def put(self, todo_id):
        print("request.form:", request.form)
        print("todo form:", request.form['todo'])
        new_todo_obj = {
            "todo": request.form['todo'],
            "owner_id": request.form['owner_id']
        }
        new_todo = ToDoModel(new_todo_obj)
        print("new_todo:", new_todo)
        new_todo.save()
        return {"new_todo": marshal(new_todo, todo_fields)}

api.add_resource(TodoSimple, '/api/v1/todos/<string:todo_id>')


# ==================================================
# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        todos = get_todos()
        return {"todos": marshal(todos, todo_fields)}

api.add_resource(TodoList, '/api/v1/todos')


# ==================================================
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')


# ==================================================
if __name__ == '__main__':
    app.run()