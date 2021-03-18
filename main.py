from flask import Flask, render_template
from data import db_session


app = Flask(__name__)

@app.route('/')
@app.route('/weblearn')
def index():
    return render_template("template.html")

if __name__ == '__main__':
    db_session.global_init("db/base_date.db")
    app.run(port=8080, host='127.0.0.1')
