from flask import Flask, render_template

app = Flask(__name__)

@app.route("/boot")
def bootstrap():
    return render_template ("boot.html")


@app.route("/about")
def name():
    name="Aman"
    return render_template ("about.html", name2=name)


app.run()