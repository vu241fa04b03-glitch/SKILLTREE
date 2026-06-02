# 241fa04b19

from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
from models import db, Skill, Badge
import os
import json

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')

mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError('ERROR: MONGO_URI environment variable is required. Please set your MongoDB Atlas connection string.')

mongo_db = None
mongo_client = None
try:
    mongo_client = MongoClient(mongo_uri)
    mongo_db_name = os.getenv('MONGO_DB_NAME', 'skilltree')
    mongo_db = mongo_client[mongo_db_name]
    print(f'Connected to MongoDB : {mongo_db.name}')
except Exception as e:
    print(f'FATAL: MongoDB connection failed: {e}')
    raise

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skilltree.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins='*')

from routes.auth_routes import auth_bp
from routes.skill_routes import skill_bp
from routes.badge_routes import badge_bp

app.register_blueprint(auth_bp)
app.register_blueprint(skill_bp)
app.register_blueprint(badge_bp)


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


def generic_question_bank(skill_name):
    qlist = []
    for i in range(1,13):
        qlist.append({
            'type': 'short',
            'question': f'{skill_name} - Short question {i}: Give the short answer for this topic.',
            'answer': f'ans_{i}'
        })
    for i in range(13,19):
        correct = f'c{i}'
        choices = [correct, f'o{i}a', f'o{i}b', f'o{i}c']
        qlist.append({
            'type': 'mcq',
            'question': f'{skill_name} - MCQ {i}: Choose the best answer.',
            'choices': choices,
            'answer': correct
        })
    for i, idx in enumerate(range(19,21), start=1):
        qlist.append({
            'type': 'coding',
            'question': f'{skill_name} - Coding task {idx}: Write a small example demonstrating the concept.',
            'answer': f'// example answer {i}'
        })
    return qlist

def get_curated_questions(skill_name):
    banks = {
        'Python Basics': [
            {'type': 'short', 'question': 'What function prints text to the console in Python?', 'answer': 'print'},
            {'type': 'short', 'question': 'Which symbol starts a comment?', 'answer': '#'},
            {'type': 'short', 'question': 'What operator assigns a value to a variable?', 'answer': '='},
            {'type': 'short', 'question': 'What data type holds True or False?', 'answer': 'bool'},
            {'type': 'short', 'question': 'Which function returns the length of a string or list?', 'answer': 'len'},
            {'type': 'short', 'question': 'What keyword is used to define a function?', 'answer': 'def'},
            {'type': 'short', 'question': 'What is the value of True and False in Python?', 'answer': 'boolean'},
            {'type': 'short', 'question': 'What quote characters can define a string?', 'answer': "\" or '"},
            {'type': 'short', 'question': 'How do you write a list with elements 1, 2, and 3?', 'answer': '[1, 2, 3]'},
            {'type': 'short', 'question': 'What keyword is used to import modules?', 'answer': 'import'},
            {'type': 'short', 'question': 'What value does a function return when there is no return statement?', 'answer': 'None'},
            {'type': 'short', 'question': 'Which built-in converts a value to a string?', 'answer': 'str'},
            {'type': 'mcq', 'question': 'Which of these is a valid Python list?', 'choices': ['[1, 2, 3]', '{1,2,3}', '(1,2,3)', '<1,2,3>'], 'answer': '[1, 2, 3]'},
            {'type': 'mcq', 'question': 'What is the boolean value of an empty list?', 'choices': ['False', 'True', 'None', '0'], 'answer': 'False'},
            {'type': 'mcq', 'question': 'Which operator is used for exponentiation?', 'choices': ['*', '^', '**', '//'], 'answer': '**'},
            {'type': 'mcq', 'question': 'What does len("hello") return?', 'choices': ['4', '5', '6', '1'], 'answer': '5'},
            {'type': 'mcq', 'question': 'Which method adds an item to a list?', 'choices': ['append', 'push', 'add', 'insert'], 'answer': 'append'},
            {'type': 'mcq', 'question': 'Which keyword ends a loop immediately?', 'choices': ['stop', 'end', 'break', 'continue'], 'answer': 'break'},
            {'type': 'coding', 'question': 'Write a line of Python that prints Hello World.', 'answer': 'print("Hello World")'},
            {'type': 'coding', 'question': 'Write a Python list containing the numbers 1, 2 and 3.', 'answer': '[1, 2, 3]'}
        ],
        'Python Loops': [
            {'type': 'short', 'question': 'Which loop repeats while a condition is true?', 'answer': 'while'},
            {'type': 'short', 'question': 'Which loop iterates over each item in a sequence?', 'answer': 'for'},
            {'type': 'short', 'question': 'What function generates a sequence of numbers?', 'answer': 'range'},
            {'type': 'short', 'question': 'Which keyword skips to the next loop iteration?', 'answer': 'continue'},
            {'type': 'short', 'question': 'Which keyword exits a loop early?', 'answer': 'break'},
            {'type': 'short', 'question': 'What does range(3) produce?', 'answer': '0, 1, 2'},
            {'type': 'short', 'question': 'What does `for item in my_list` do?', 'answer': 'iterates over my_list'},
            {'type': 'short', 'question': 'What keyword can follow a loop to run if the loop completes normally?', 'answer': 'else'},
            {'type': 'short', 'question': 'What type of structure can be used in a for loop?', 'answer': 'iterable'},
            {'type': 'short', 'question': 'What does nested loop mean?', 'answer': 'a loop inside another loop'},
            {'type': 'short', 'question': 'What is the first value produced by range(1,4)?', 'answer': '1'},
            {'type': 'short', 'question': 'How many times does range(3) loop execute?', 'answer': '3'},
            {'type': 'mcq', 'question': 'Which keyword creates a loop in Python?', 'choices': ['loop', 'for', 'repeat', 'iterate'], 'answer': 'for'},
            {'type': 'mcq', 'question': 'What does continue do inside a loop?', 'choices': ['Exit loop', 'Skip current iteration', 'Restart program', 'Pause loop'], 'answer': 'Skip current iteration'},
            {'type': 'mcq', 'question': 'How many values does range(0,2) generate?', 'choices': ['1', '2', '3', '0'], 'answer': '2'},
            {'type': 'mcq', 'question': 'Which loop checks a condition before each iteration?', 'choices': ['for', 'while', 'do-while', 'until'], 'answer': 'while'},
            {'type': 'mcq', 'question': 'What does break do?', 'choices': ['Restart loop', 'End loop', 'Skip iteration', 'Ignore condition'], 'answer': 'End loop'},
            {'type': 'mcq', 'question': 'Which sequence will a for loop over `"abc"` produce?', 'choices': ['a,b,c', 'abc', '1,2,3', 'none'], 'answer': 'a,b,c'},
            {'type': 'coding', 'question': 'Write a Python for loop that prints numbers 0, 1 and 2.', 'answer': 'for i in range(3):\n    print(i)'},
            {'type': 'coding', 'question': 'Write a Python while loop that increments x until it reaches 5.', 'answer': 'while x < 5:\n    x += 1'}
        ],
        'Python Functions': [
            {'type': 'short', 'question': 'Which keyword defines a function?', 'answer': 'def'},
            {'type': 'short', 'question': 'What keyword sends a value back from a function?', 'answer': 'return'},
            {'type': 'short', 'question': 'What is a function parameter?', 'answer': 'input variable'},
            {'type': 'short', 'question': 'What is a function argument?', 'answer': 'passed value'},
            {'type': 'short', 'question': 'What does a function name do?', 'answer': 'identifies the function'},
            {'type': 'short', 'question': 'What keyword begins a lambda expression?', 'answer': 'lambda'},
            {'type': 'short', 'question': 'What is a docstring?', 'answer': 'documentation string'},
            {'type': 'short', 'question': 'What keyword defines default parameter values?', 'answer': 'def'},
            {'type': 'short', 'question': 'What is a return type?','answer':'the type of returned value'},
            {'type': 'short', 'question': 'How do you call a function named `greet`?','answer':'greet()'},
            {'type': 'short', 'question': 'What scope refers to variables inside a function?','answer':'local'},
            {'type': 'short', 'question': 'Which keyword makes a function accept any number of positional arguments?','answer':'*args'},
            {'type': 'mcq', 'question': 'Which syntax defines a function?', 'choices': ['function foo():', 'def foo():', 'func foo()', 'lambda foo:'], 'answer': 'def foo():'},
            {'type': 'mcq', 'question': 'What does return do?', 'choices': ['Stop function', 'Exit loop', 'Call function', 'Save variable'], 'answer': 'Stop function'},
            {'type': 'mcq', 'question': 'Which symbol begins a lambda function?', 'choices': ['def', '=>', 'lambda', '#'], 'answer': 'lambda'},
            {'type': 'mcq', 'question': 'How many arguments does def foo(a, b): take?', 'choices': ['1', '2', '3', '0'], 'answer': '2'},
            {'type': 'mcq', 'question': 'What is a callback?', 'choices': ['a function passed into another function', 'a comment', 'a loop', 'a variable'], 'answer': 'a function passed into another function'},
            {'type': 'mcq', 'question': 'Which keyword is used for keyword arguments?', 'choices': ['args', 'kwargs', 'return', 'yield'], 'answer': 'kwargs'},
            {'type': 'coding', 'question': 'Write a Python function named hello that prints Hello.', 'answer': 'def hello():\n    print("Hello")'},
            {'type': 'coding', 'question': 'Write a Python function that returns the sum of a and b.', 'answer': 'def add(a, b):\n    return a + b'}
        ],
        'Python OOP': [
            {'type': 'short', 'question': 'What keyword starts a class definition?', 'answer': 'class'},
            {'type': 'short', 'question': 'What does self represent?', 'answer': 'instance'},
            {'type': 'short', 'question': 'What special method initializes an object?', 'answer': '__init__'},
            {'type': 'short', 'question': 'What is inheritance?', 'answer': 'reuse of parent class'},
            {'type': 'short', 'question': 'What is a class attribute?', 'answer': 'attribute shared by all instances'},
            {'type': 'short', 'question': 'What is an instance attribute?', 'answer': 'attribute specific to one object'},
            {'type': 'short', 'question': 'What method is called when an object is printed?', 'answer': '__str__'},
            {'type': 'short', 'question': 'What keyword calls the parent class constructor?', 'answer': 'super()'},
            {'type': 'short', 'question': 'What is polymorphism?', 'answer': 'same interface different behavior'},
            {'type': 'short', 'question': 'What is encapsulation?', 'answer': 'hiding internal state'},
            {'type': 'short', 'question': 'What is a method?', 'answer': 'function inside class'},
            {'type': 'short', 'question': 'What does `isinstance(obj, Class)` check?', 'answer': 'type of object'},
            {'type': 'mcq', 'question': 'Which syntax creates a class?', 'choices': ['class Foo:', 'def Foo:', 'object Foo:', 'new Foo:'], 'answer': 'class Foo:'},
            {'type': 'mcq', 'question': 'Which keyword accesses the superclass?', 'choices': ['parent', 'super', 'base', 'self'], 'answer': 'super'},
            {'type': 'mcq', 'question': 'What does __init__ do?', 'choices': ['defines methods', 'initializes an instance', 'deletes object', 'prints object'], 'answer': 'initializes an instance'},
            {'type': 'mcq', 'question': 'What is an object?', 'choices': ['class definition', 'instance of class', 'function', 'module'], 'answer': 'instance of class'},
            {'type': 'mcq', 'question': 'Which concept allows different classes to use the same method name?', 'choices': ['inheritance', 'polymorphism', 'encapsulation', 'abstraction'], 'answer': 'polymorphism'},
            {'type': 'coding', 'question': 'Write a Python class named Person with an __init__ that accepts name.', 'answer': 'class Person:\n    def __init__(self, name):\n        self.name = name'},
            {'type': 'coding', 'question': 'Write a method greet in a class that prints Hello.', 'answer': 'def greet(self):\n        print("Hello")'}
        ],
        'HTML Basics': [
            {'type': 'short', 'question': 'What tag creates a hyperlink?', 'answer': 'a'},
            {'type': 'short', 'question': 'What is the tag for a paragraph?', 'answer': 'p'},
            {'type': 'short', 'question': 'What tag creates a heading level 1?', 'answer': 'h1'},
            {'type': 'short', 'question': 'What attribute sets the destination URL for a link?', 'answer': 'href'},
            {'type': 'short', 'question': 'What tag displays an image?', 'answer': 'img'},
            {'type': 'short', 'question': 'What attribute specifies alternative text for images?', 'answer': 'alt'},
            {'type': 'short', 'question': 'What tag creates an unordered list?', 'answer': 'ul'},
            {'type': 'short', 'question': 'What tag is used for a list item?', 'answer': 'li'},
            {'type': 'short', 'question': 'What tag starts a table row?', 'answer': 'tr'},
            {'type': 'short', 'question': 'What tag defines a table cell?', 'answer': 'td'},
            {'type': 'short', 'question': 'What tag contains the page title in the browser tab?', 'answer': 'title'},
            {'type': 'short', 'question': 'What tag creates a form?', 'answer': 'form'},
            {'type': 'mcq', 'question': 'What tag defines a link?', 'choices': ['<link>', '<a>', '<href>', '<url>'], 'answer': '<a>'},
            {'type': 'mcq', 'question': 'Which tag is semantic for main page content?', 'choices': ['<div>', '<section>', '<main>', '<span>'], 'answer': '<main>'},
            {'type': 'mcq', 'question': 'Which attribute sets the image source?', 'choices': ['src', 'href', 'alt', 'title'], 'answer': 'src'},
            {'type': 'mcq', 'question': 'Which tag defines a table header cell?', 'choices': ['<th>', '<tr>', '<td>', '<thead>'], 'answer': '<th>'},
            {'type': 'mcq', 'question': 'Which tag is used for an email input field?', 'choices': ['<input type="email">', '<input type="text">', '<textarea>', '<button>'], 'answer': '<input type="email">'},
            {'type': 'coding', 'question': 'Write an HTML anchor tag that links to https://example.com.', 'answer': '<a href="https://example.com">Link</a>'},
            {'type': 'coding', 'question': 'Write an HTML paragraph tag containing Hello.', 'answer': '<p>Hello</p>'}
        ],
        'CSS Basics': [
            {'type': 'short', 'question': 'Which property changes text color?', 'answer': 'color'},
            {'type': 'short', 'question': 'Which property changes background color?', 'answer': 'background-color'},
            {'type': 'short', 'question': 'Which property changes font size?', 'answer': 'font-size'},
            {'type': 'short', 'question': 'Which property sets margin around an element?', 'answer': 'margin'},
            {'type': 'short', 'question': 'Which property sets padding inside an element?', 'answer': 'padding'},
            {'type': 'short', 'question': 'Which property sets element width?', 'answer': 'width'},
            {'type': 'short', 'question': 'Which selector targets elements by class?', 'answer': '.'},
            {'type': 'short', 'question': 'Which selector targets elements by id?', 'answer': '#'},
            {'type': 'short', 'question': 'Which property sets the border style?', 'answer': 'border-style'},
            {'type': 'short', 'question': 'What is the box model made of?', 'answer': 'content, padding, border, margin'},
            {'type': 'short', 'question': 'What property centers text?', 'answer': 'text-align'},
            {'type': 'short', 'question': 'What property makes text bold?', 'answer': 'font-weight'},
            {'type': 'mcq', 'question': 'Which property changes the font family?', 'choices': ['font-style', 'font-family', 'font-weight', 'font-size'], 'answer': 'font-family'},
            {'type': 'mcq', 'question': 'Which value sets a blue background?', 'choices': ['blue', '#0000ff', 'rgb(0,0,255)', 'all of these'], 'answer': 'all of these'},
            {'type': 'mcq', 'question': 'Which property sets element display mode?', 'choices': ['display', 'position', 'float', 'visibility'], 'answer': 'display'},
            {'type': 'mcq', 'question': 'Which property sets a rounded border?', 'choices': ['border-radius', 'border-width', 'border-color', 'border-style'], 'answer': 'border-radius'},
            {'type': 'mcq', 'question': 'How do you select elements with class card?', 'choices': ['.card', '#card', 'card', '*card'], 'answer': '.card'},
            {'type': 'coding', 'question': 'Write a CSS rule to set body background to light gray.', 'answer': 'body { background-color: lightgray; }'},
            {'type': 'coding', 'question': 'Write a CSS rule to make paragraphs red.', 'answer': 'p { color: red; }'}
        ],
        'CSS Flexbox': [
            {'type': 'short', 'question': 'Which display value enables flexbox?', 'answer': 'flex'},
            {'type': 'short', 'question': 'Which property aligns items along the main axis?', 'answer': 'justify-content'},
            {'type': 'short', 'question': 'Which property aligns items along the cross axis?', 'answer': 'align-items'},
            {'type': 'short', 'question': 'Which property controls wrapping of flex items?', 'answer': 'flex-wrap'},
            {'type': 'short', 'question': 'Which property sets item order?', 'answer': 'order'},
            {'type': 'short', 'question': 'Which property lets an item grow?', 'answer': 'flex-grow'},
            {'type': 'short', 'question': 'Which property lets an item shrink?', 'answer': 'flex-shrink'},
            {'type': 'short', 'question': 'Which property sets the size of a flex item?', 'answer': 'flex-basis'},
            {'type': 'short', 'question': 'Which property aligns a single item on the cross axis?', 'answer': 'align-self'},
            {'type': 'short', 'question': 'Which property creates space between flex items?', 'answer': 'gap'},
            {'type': 'short', 'question': 'What does align-content do?', 'answer': 'aligns rows of items'},
            {'type': 'short', 'question': 'What is a flex container?', 'answer': 'element with display:flex'},
            {'type': 'mcq', 'question': 'Which value places items at the start of the main axis?', 'choices': ['flex-start', 'center', 'flex-end', 'space-between'], 'answer': 'flex-start'},
            {'type': 'mcq', 'question': 'Which value distributes items evenly with equal space around them?', 'choices': ['space-between', 'space-around', 'space-evenly', 'center'], 'answer': 'space-around'},
            {'type': 'mcq', 'question': 'Which property makes a flex container wrap items?', 'choices': ['flex-wrap', 'wrap', 'flex-flow', 'display'], 'answer': 'flex-wrap'},
            {'type': 'mcq', 'question': 'Which value makes items center vertically in a row?', 'choices': ['center', 'flex-end', 'space-between', 'flex-start'], 'answer': 'center'},
            {'type': 'mcq', 'question': 'Which property changes the direction of flex items?', 'choices': ['flex-direction', 'direction', 'align-items', 'justify-content'], 'answer': 'flex-direction'},
            {'type': 'coding', 'question': 'Write a CSS rule to make a container use flex layout.', 'answer': '.container { display: flex; }'},
            {'type': 'coding', 'question': 'Write a CSS rule to center items horizontally in flex.', 'answer': 'justify-content: center;'}
        ],
        'JavaScript Basics': [
            {'type': 'short', 'question': 'Which keyword declares a block-scoped variable?', 'answer': 'let'},
            {'type': 'short', 'question': 'Which method prints text to the JS console?', 'answer': 'console.log'},
            {'type': 'short', 'question': 'How do you write a string?', 'answer': '"hello"'},
            {'type': 'short', 'question': 'What is the type of true?', 'answer': 'boolean'},
            {'type': 'short', 'question': 'Which operator adds two numbers?', 'answer': '+'},
            {'type': 'short', 'question': 'What keyword defines a function?', 'answer': 'function'},
            {'type': 'short', 'question': 'How do you create an array with 3 items?', 'answer': '[1, 2, 3]'},
            {'type': 'short', 'question': 'What operator checks equality without type coercion?', 'answer': '==='},
            {'type': 'short', 'question': 'What keyword starts a conditional?', 'answer': 'if'},
            {'type': 'short', 'question': 'What symbol starts a single-line comment?', 'answer': '//' },
            {'type': 'short', 'question': 'What data type holds key/value pairs?', 'answer': 'object'},
            {'type': 'short', 'question': 'What method gets the length of a string?', 'answer': 'length'},
            {'type': 'mcq', 'question': 'Which is a valid JS variable declaration?', 'choices': ['var x = 1;', 'let x = 1;', 'const x = 1;', 'all of these'], 'answer': 'all of these'},
            {'type': 'mcq', 'question': 'Which value is falsey in JS?', 'choices': ['""', '0', 'null', 'all of these'], 'answer': 'all of these'},
            {'type': 'mcq', 'question': 'What does typeof [] return?', 'choices': ['array', 'object', 'list', 'string'], 'answer': 'object'},
            {'type': 'mcq', 'question': 'Which symbol starts an arrow function?', 'choices': ['=>', '->', '=>', '=>'], 'answer': '=>'},
            {'type': 'mcq', 'question': 'Which array method adds an item to the end?', 'choices': ['push', 'pop', 'shift', 'unshift'], 'answer': 'push'},
            {'type': 'coding', 'question': 'Write JS code to log Hello to the console.', 'answer': 'console.log("Hello");'},
            {'type': 'coding', 'question': 'Write a JS array with items a, b, c.', 'answer': '["a", "b", "c"]'}
        ],
        'JavaScript Functions': [
            {'type': 'short', 'question': 'How do you define a named function?', 'answer': 'function foo() {}'},
            {'type': 'short', 'question': 'What keyword returns a value from a function?', 'answer': 'return'},
            {'type': 'short', 'question': 'What is a callback?', 'answer': 'a function passed as an argument'},
            {'type': 'short', 'question': 'What does arrow syntax use after parameters?', 'answer': '=>'},
            {'type': 'short', 'question': 'What is the word for extra parameters collected into an array?', 'answer': 'rest'},
            {'type': 'short', 'question': 'Which object contains arguments inside a function?', 'answer': 'arguments'},
            {'type': 'short', 'question': 'What is closure?', 'answer': 'function remembers outer scope'},
            {'type': 'short', 'question': 'What keyword creates a function expression?', 'answer': 'const'},
            {'type': 'short', 'question': 'What is a pure function?', 'answer': 'same output for same input'},
            {'type': 'short', 'question': 'What is function hoisting?', 'answer': 'function definition moves to top'},
            {'type': 'short', 'question': 'What does bind do?', 'answer': 'sets this value'},
            {'type': 'short', 'question': 'What is an IIFE?', 'answer': 'immediately invoked function expression'},
            {'type': 'mcq', 'question': 'Which syntax defines an arrow function?', 'choices': ['() => {}', 'function() {}', 'def => {}', 'lambda() {}'], 'answer': '() => {}'},
            {'type': 'mcq', 'question': 'Which keyword returns from a function?', 'choices': ['return', 'break', 'continue', 'yield'], 'answer': 'return'},
            {'type': 'mcq', 'question': 'Which method calls a function after a delay?', 'choices': ['setTimeout', 'setInterval', 'delay', 'wait'], 'answer': 'setTimeout'},
            {'type': 'mcq', 'question': 'Which term describes a function inside an object?', 'choices': ['method', 'arrow', 'property', 'array'], 'answer': 'method'},
            {'type': 'mcq', 'question': 'What does callback mean?', 'choices': ['function passed to another function', 'function returned by a function', 'function name', 'function argument'], 'answer': 'function passed to another function'},
            {'type': 'coding', 'question': 'Write an arrow function named add that returns a+b.', 'answer': 'const add = (a, b) => a + b;'},
            {'type': 'coding', 'question': 'Write a function that takes name and logs Hello name.', 'answer': 'function greet(name) { console.log(`Hello ${name}`); }'}
        ],
        'SQL Basics': [
            {'type': 'short', 'question': 'Which keyword retrieves data from a table?', 'answer': 'SELECT'},
            {'type': 'short', 'question': 'Which keyword adds new rows?', 'answer': 'INSERT'},
            {'type': 'short', 'question': 'Which keyword removes rows?', 'answer': 'DELETE'},
            {'type': 'short', 'question': 'Which keyword updates existing rows?', 'answer': 'UPDATE'},
            {'type': 'short', 'question': 'Which clause filters rows?', 'answer': 'WHERE'},
            {'type': 'short', 'question': 'Which clause sorts results?', 'answer': 'ORDER BY'},
            {'type': 'short', 'question': 'Which function counts rows?', 'answer': 'COUNT'},
            {'type': 'short', 'question': 'Which keyword creates a table?', 'answer': 'CREATE TABLE'},
            {'type': 'short', 'question': 'What is a primary key?', 'answer': 'unique identifier'},
            {'type': 'short', 'question': 'What is a foreign key?', 'answer': 'reference to another table'},
            {'type': 'short', 'question': 'Which clause groups rows?', 'answer': 'GROUP BY'},
            {'type': 'short', 'question': 'Which keyword removes a table?', 'answer': 'DROP TABLE'},
            {'type': 'mcq', 'question': 'Which SQL command reads data?', 'choices': ['SELECT', 'INSERT', 'UPDATE', 'DELETE'], 'answer': 'SELECT'},
            {'type': 'mcq', 'question': 'Which clause is used to sort results?', 'choices': ['GROUP BY', 'ORDER BY', 'WHERE', 'HAVING'], 'answer': 'ORDER BY'},
            {'type': 'mcq', 'question': 'Which function calculates an average?', 'choices': ['SUM', 'COUNT', 'AVG', 'MAX'], 'answer': 'AVG'},
            {'type': 'mcq', 'question': 'Which keyword selects distinct values?', 'choices': ['UNIQUE', 'DISTINCT', 'DIFFERENT', 'SEPARATE'], 'answer': 'DISTINCT'},
            {'type': 'mcq', 'question': 'Which clause filters grouped results?', 'choices': ['WHERE', 'HAVING', 'ORDER BY', 'LIMIT'], 'answer': 'HAVING'},
            {'type': 'coding', 'question': 'Write a SELECT query for all columns from customers.', 'answer': 'SELECT * FROM customers;'},
            {'type': 'coding', 'question': 'Write an INSERT query to add a new row to users.', 'answer': 'INSERT INTO users (name) VALUES ("Alice");'}
        ]
    }
    return banks.get(skill_name, generic_question_bank(skill_name))

with app.app_context():
    db.create_all()
    if Skill.query.count() == 0:
        skills = [
        Skill(
            name='Python Basics',
            description='Learn Python variables, data types, and print statements.',
            category='Python',
            level=1,
            xp_reward=20,
            assignment_question=json.dumps(get_curated_questions('Python Basics')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='Python Loops',
            description='Understand for loops and while loops in Python.',
            category='Python',
            level=2,
            xp_reward=30,
            assignment_question=json.dumps(get_curated_questions('Python Loops')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='Python Functions',
            description='Define and call functions. Understand parameters and return values.',
            category='Python',
            level=3,
            xp_reward=40,
            assignment_question=json.dumps(get_curated_questions('Python Functions')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='Python OOP',
            description='Object-oriented programming: classes, objects, inheritance.',
            category='Python',
            level=4,
            xp_reward=50,
            assignment_question=json.dumps(get_curated_questions('Python OOP')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='HTML Basics',
            description='Learn HTML tags, headings, paragraphs, and links.',
            category='Web',
            level=1,
            xp_reward=15,
            assignment_question=json.dumps(get_curated_questions('HTML Basics')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='CSS Basics',
            description='Style HTML elements using CSS properties.',
            category='Web',
            level=2,
            xp_reward=25,
            assignment_question=json.dumps(get_curated_questions('CSS Basics')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='CSS Flexbox',
            description='Use flexbox to create responsive layouts.',
            category='Web',
            level=3,
            xp_reward=35,
            assignment_question=json.dumps(get_curated_questions('CSS Flexbox')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='JavaScript Basics',
            description='Variables, data types, and console output in JavaScript.',
            category='JavaScript',
            level=1,
            xp_reward=20,
            assignment_question=json.dumps(get_curated_questions('JavaScript Basics')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='JavaScript Functions',
            description='Define functions, use arrow functions and callbacks.',
            category='JavaScript',
            level=2,
            xp_reward=30,
            assignment_question=json.dumps(get_curated_questions('JavaScript Functions')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        Skill(
            name='SQL Basics',
            description='Learn SELECT, INSERT, UPDATE, and DELETE queries.',
            category='Database',
            level=1,
            xp_reward=25,
            assignment_question=json.dumps(get_curated_questions('SQL Basics')),
            assignment_answer='',
            prerequisite_skill_id=None
        ),
        ]
        
        db.session.add_all(skills)
        db.session.flush()
        
        py_basics = Skill.query.filter_by(name='Python Basics').first()
        py_loops = Skill.query.filter_by(name='Python Loops').first()
        py_funcs = Skill.query.filter_by(name='Python Functions').first()
        py_oop = Skill.query.filter_by(name='Python OOP').first()
        html = Skill.query.filter_by(name='HTML Basics').first()
        css = Skill.query.filter_by(name='CSS Basics').first()
        flex = Skill.query.filter_by(name='CSS Flexbox').first()
        js = Skill.query.filter_by(name='JavaScript Basics').first()
        js_fn = Skill.query.filter_by(name='JavaScript Functions').first()
        
        py_loops.prerequisite_skill_id = py_basics.id
        py_funcs.prerequisite_skill_id = py_loops.id
        py_oop.prerequisite_skill_id = py_funcs.id
        css.prerequisite_skill_id = html.id
        flex.prerequisite_skill_id = css.id
        js_fn.prerequisite_skill_id = js.id
        
        db.session.flush()
        
        badges = [
            Badge(name='Python Starter', description='Completed Python Basics', icon='🐍', skill_id=py_basics.id, xp_required=0),
            Badge(name='Loop Master', description='Completed Python Loops', icon='🔄', skill_id=py_loops.id, xp_required=0),
            Badge(name='Function Wizard', description='Completed Python Functions', icon='🧙', skill_id=py_funcs.id, xp_required=0),
            Badge(name='OOP Champion', description='Mastered Object-Oriented Python', icon='🏆', skill_id=py_oop.id, xp_required=0),
            Badge(name='Web Builder', description='Completed HTML Basics', icon='🌐', skill_id=html.id, xp_required=0),
            Badge(name='Style Artist', description='Completed CSS Basics', icon='🎨', skill_id=css.id, xp_required=0),
            Badge(name='Flex Master', description='Mastered CSS Flexbox', icon='📐', skill_id=flex.id, xp_required=0),
            Badge(name='JS Learner', description='Completed JavaScript Basics', icon='⚡', skill_id=js.id, xp_required=0),
            Badge(name='JS Function Pro', description='Mastered JavaScript Functions', icon='🚀', skill_id=js_fn.id, xp_required=0),
            Badge(name='Data Whiz', description='Completed SQL Basics', icon='🗄️', skill_id=Skill.query.filter_by(name='SQL Basics').first().id, xp_required=0),
        ]
        db.session.add_all(badges)
        db.session.commit()
    print('Seed data inserted.')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('DEBUG', 'True') == 'True', port=port)
