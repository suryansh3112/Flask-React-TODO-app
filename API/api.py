from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    todos = db.relationship("Todo", backref='author', lazy=True)

    def __init__(self, email, password, first_name, last_name, phone):
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    @classmethod
    def find_by_email(cls, email):

        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, idx):

        return cls.query.get(idx)

    def __repr__(self):
        return f'<User {self.email} >'

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.user_id}>'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.find_by_email(data['email']):

        return jsonify({'message': 'This email already exists.'}), 400

    user = User(email=data['email'], password=data['password'],
                first_name=data['first_name'], last_name=data['last_name'], phone=data['phone'])
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({'message': 'Something went wrong'}), 500

    return jsonify({'message': 'Successfully Registered'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.find_by_email(data['email'])

    if not user:
        return jsonify({'message': "No account with this email is registered."}), 400

    if user.verify_password(data['password']):
        access_token = create_access_token(
            identity=user.id, expires_delta=datetime.timedelta(minutes=15))
        return jsonify({'access_token': access_token, "user": user.email}), 200
    else:
        return jsonify({'message': "Wrong credentials"}), 400


@app.route('/get_info', methods=['GET'])
@jwt_required()
def get_info():
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)
    info = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone
    }
    return jsonify(info), 200


@app.route('/verify_token', methods=['GET'])
@jwt_required()
def verify_token():
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)

    return jsonify({"message": "verified", "user": user.email}), 200


def todo_serializer(todo):
    return{
        "id": todo.id,
        "content": todo.content
    }


@app.route('/api', methods=['GET'])
@jwt_required()
def api():
    user_id = get_jwt_identity()
    todos = User.query.get(user_id).todos
    return jsonify([*map(todo_serializer, todos)])


@app.route('/add', methods=['POST'])
@jwt_required()
def add():
    user_id = get_jwt_identity()
    data = request.get_json()
    todo = Todo(content=data['content'], user_id=user_id)
    db.session.add(todo)
    db.session.commit()

    return jsonify(todo_serializer(todo)), 201


@app.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    item = Todo.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return "Done", 200


@app.route('/update/<int:id>', methods=['PATCH'])
@jwt_required()
def update(id):
    content = request.get_json()['content']
    item = Todo.query.get(id)

    item.content = content
    db.session.commit()
    return jsonify(todo_serializer(item)), 200


if(__name__ == '__main__'):
    app.run(debug=True)
