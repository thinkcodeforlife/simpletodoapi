from flask import Flask, request, jsonify
from flask_restful import Resource, Api, fields, marshal

from flask_sqlalchemy import SQLAlchemy
import os

from flask_cors import CORS, cross_origin
# import logging


app = Flask(__name__)
cors = CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import ToDoModel, UserModel

api = Api(app, prefix="/api/v1")


from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

jwt = JWTManager(app)

# logging.getLogger('flask_cors').level = logging.DEBUG


@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.json.get('name', None)
        return jsonify({"msg": f"Hello {name}, from inside!"}), 200
    return "Hello"
    

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    name = request.json.get('name', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)
    if not name:
        return jsonify({"msg": "Missing user name parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400

    # if name != 'test' or password != 'test':
    #     return jsonify({"msg": "Bad user name or password"}), 401

    users = get_users()
    print(users)
    user_id = ""
    for user in users:
        print(user.name)
        print(user.email)
        print(user.id)
        if user.name == name and user.email == email and user.check_hash(password):
            print("u did it")
            user_id = user.id

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=name)
    return jsonify(user_id=user_id, access_token=access_token), 200


# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# ==================================================
# from flask_httpauth import HTTPBasicAuth


# auth = HTTPBasicAuth()


# @app.route('/token')
# @auth.login_required
# def get_auth_token():
#     token = UserModel.generate_auth_token()
#     return jsonify({ 'token': token.decode('ascii') })


# ==================================================
user_fields =  {
    "name": fields.String,
    "email": fields.String
}

def get_users():
    return UserModel.get_all_users()

class UserEndPoint(Resource):
    @jwt_required
    def get(self, user_id):
        requested_user = UserModel.get_one_user(user_id)
        return {"requested_user": marshal(requested_user, user_fields)}

    @jwt_required
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

api.add_resource(UserEndPoint, '/users/<string:user_id>')


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
    @jwt_required
    def get(self, user_id):
        user_todos = UserModel.get_user_todos(user_id)
        print("user_todos:", user_todos)
        return {"user": marshal(user_todos, user_todos_fields)}

api.add_resource(UserTodos, '/users/<string:user_id>/todos')


# ==================================================
class UserList(Resource):
    @jwt_required
    def get(self):
        users = get_users()
        return {"users": marshal(users, user_fields)}

api.add_resource(UserList, '/users')


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
        try:
            # todos = get_todos()
            # desired_todo = [todo for todo in todos if todo.id == int(request.form['id'])][0]
            # print("desired_todo:", desired_todo)
            # return {"edited_todo": marshal(desired_todo, todo_fields)}
            # ==================================
            requested_todo = ToDoModel.get_one_todo(request.form['id'])
            requested_todo.todo = request.form['todo']
            requested_todo.save()
            return {"edited_todo": marshal(requested_todo, todo_fields)}
        except:
            new_todo_obj = {
                "todo": request.form['todo'],
                "owner_id": request.form['owner_id']
            }
            new_todo = ToDoModel(new_todo_obj)
            print("new_todo:", new_todo)
            new_todo.save()
            return {"new_todo": marshal(new_todo, todo_fields)}

    def delete(self, todo_id):
        requested_todo = ToDoModel.get_one_todo(todo_id)
        db.session.delete(requested_todo)
        db.session.commit()
        return {"deleted_todo": marshal(requested_todo, todo_fields)}

api.add_resource(TodoSimple, '/todos/<string:todo_id>')


# ==================================================
# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        todos = get_todos()
        return {"todos": marshal(todos, todo_fields)}

api.add_resource(TodoList, '/todos')


# ==================================================
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')


# ==================================================
if __name__ == '__main__':
    app.run()