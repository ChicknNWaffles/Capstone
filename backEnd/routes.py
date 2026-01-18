from flask import Flask, render_template

app = Flask(__name__)

# this route is a placeholder for boilerplate.
# replace with whatever routes we need for our
# functionality to communicate properly
@app.route('/', methods = ['POST', 'GET'])
def root():
    return render_template("temp.html")


if __name__ == "__main__":
    app.run()
