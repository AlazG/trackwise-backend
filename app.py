# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Create Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trackwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='todo')
    archived = db.Column(db.Boolean, default=False)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# CLI command to create tables
@app.cli.command('create_tables')
def create_tables():
    """Create database tables."""
    db.create_all()
    print('Database tables created.')

# Routes

# Auth
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(name=data.get('name'), password=data.get('password')).first()
    if user:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'password': u.password} for u in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    user = User(name=data['name'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

# Tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.filter_by(archived=False).all()
    return jsonify([{'id': t.id, 'text': t.text, 'status': t.status, 'archived': t.archived} for t in tasks])

@app.route('/api/tasks/archived', methods=['GET'])
def get_archived_tasks():
    tasks = Task.query.filter_by(archived=True).all()
    return jsonify([{'id': t.id, 'text': t.text, 'status': t.status, 'archived': t.archived} for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    task = Task(text=data['text'], status=data.get('status', 'todo'))
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id, 'text': task.text, 'status': task.status})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    task.text = data.get('text', task.text)
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify({'id': task.id, 'text': task.text, 'status': task.status})

@app.route('/api/tasks/<int:task_id>/archive', methods=['PUT'])
def archive_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.archived = True
    db.session.commit()
    return jsonify({'id': task.id, 'archived': task.archived})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

# Inventory
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    items = InventoryItem.query.all()
    return jsonify([{'id': i.id, 'name': i.name, 'quantity': i.quantity} for i in items])

@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.get_json()
    item = InventoryItem(name=data['name'], quantity=data['quantity'])
    db.session.add(item)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name, 'quantity': item.quantity})

@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.get_json()
    item = InventoryItem.query.get_or_404(item_id)
    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    db.session.commit()
    return jsonify({'id': item.id, 'name': item.name, 'quantity': item.quantity})

@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    item = InventoryItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
