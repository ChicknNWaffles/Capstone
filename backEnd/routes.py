from asyncio.windows_events import NULL
from flask import Flask, render_template, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="../frontEnd/templates", static_folder="../frontEnd/static")

app.secret_key = 'asdfasldgkjadkljaklsdjkljskldajksdjfkajsdkjafsdfasdf'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/Capstone'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# to make an account
class RegisterAccount(db.Model):
    username = db.Column(db.String(100), primary_key = True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods = ['POST', 'GET'])
def editorPage():
    if request.method == "GET":
        projName = session.get("projName", "unknown")
        return render_template("editor.html", projectName = projName)
    

# testing for adding database
# @app.route('/', methods = ['GET'])
# def getRegisterAccount():
#     return jsonify({"Hello":"World"})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000')
