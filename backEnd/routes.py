from asyncio.windows_events import NULL
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__, template_folder="../frontEnd/templates", static_folder="../frontEnd/static")

app.secret_key = 'asdfasldgkjadkljaklsdjkljskldajksdjfkajsdkjafsdfasdf'


@app.route('/', methods = ['POST', 'GET'])
def editorPage():
    if request.method == "GET":
        projName = session.get("projName", "unknownProject")
        commitNm = session.get("commitName", "unknownCommit")
        return render_template("editor.html", projectName = projName, commitName = commitNm)

@app.route('/login', methods = ['POST', 'GET'])
def loginPage():
    return render_template("login.html")

@app.route('/signup', methods = ['POST', 'GET'])
def signupPage():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000')
