from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
import os  
from werkzeug.utils import secure_filename
import math


#calling from config.json file
with open("templates/config.json", "r") as c:
    params =json.load(c)["params"]


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:111111@localhost/blog"
app.secret_key="my-secret-key"
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME= params['mail_user'],
    MAIL_PASSWORD= params['mail_pass']
)
mail=Mail(app)

# # configure the Mysql database, relative to the app instance folder
# local_server=True

# if local_server:
#     # app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/content"  #without using config.json file
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']    #using config.json file

# else:
#     # app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{username}.{password}@{servername}/{databasename}"  #without using config.json file
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']    #using config.json file

#initialize db variable
db=SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String, nullable=False)
    date =db.Column(db.DateTime)
    email = db.Column(db.String, nullable=False)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    tagline = db.Column(db.String, nullable=False)
    date =db.Column(db.DateTime)
    img_file = db.Column(db.String(50), nullable=False)

@app.route("/")
def home():
    # posts=Post.query.filter_by().all()[0:5]
    posts=Post.query.filter_by().all()


    last=math.ceil(len(posts)/int(params['no_of_post']))
    print("last page no: ", last)
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page=1

    page=int(page)
    posts=posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+int(params['no_of_post'])]
    if page ==1:
        prev="#"
        next="/?page="+str(page+1)
    elif page==last:
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)
    return render_template ("index.html", params=params, posts=posts, prev=prev, next=next)


@app.route("/login" ,methods=['GET','POST'])
def login():
    if ('user' in session and session['user'] == params['username']):
        posts=Post.query.all()
        return render_template ("dashboard.html", params=params, posts=posts)
    if request.method=="POST":
        username=request.form.get('username')   
        password=request.form.get('password')  
        if username==params['username'] and password==params['password']:
            session['user']=username
            posts=Post.query.all()          
            return render_template ("dashboard.html", params=params, posts=posts)              
    return render_template ("login.html", params=params)

@app.route("/logout")
def logout(): 
    session.pop('user')
    return redirect ('/login')


@app.route("/about")
def about():  
    return render_template ("about.html", params=params)


@app.route("/post/<string:post_slug>",methods=['GET'])
def post(post_slug):  
    post=Post.query.filter_by(slug=post_slug).first()
    return render_template ("post.html", params=params, post=post)

    
@app.route("/edit/<string:sno>" , methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['username']):
        if request.method == "POST":
            title=request.form.get('title')
            tagline=request.form.get('tagline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            print("This is title: ",title)
            # if sno=='0':
            #     print("Title: ", title)
            #     post=Post(title=title,slug=slug,date=date,tagline=tagline,img_file=img_file,content=content)
            #     db.session.add(post)
            #     db.session.commit()                 
            if sno != '0':
                post=Post.query.filter_by(sno=sno).first()
                post.title=title
                post.slug=slug
                post.tagline=tagline             
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect ('/edit/'+sno)
        post=Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)


    
@app.route("/add/<string:sno>" , methods=['GET','POST'])
def add(sno):
    if 'user' in session and session['user'] == params['username']:
        if request.method == 'POST':
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            print("This is title: ", title)
            if sno == '0':
                post = Post(title=title, slug=slug, date=date, tagline=tagline, img_file=img_file, content=content)
                db.session.add(post)             
                db.session.commit()
        return render_template ('add.html', params=params, sno=sno)
      

@app.route("/delete/<string:sno>" , methods=['GET','POST'])
def delete(sno): 
    if ('user' in session and session['user'] == params['username']):
        post=Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()   
    return redirect ('/login')
    
@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if "user" in session and session['user']==params['username']:
        if request.method=='POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"
        

@app.route("/contact", methods=['GET','POST'])
def contact():  
    if request.method == "POST":
        """Add entry to database"""
        name=request.form.get('name')
        email=request.form.get('email')
        phone_number=request.form.get('phone_number')
        message=request.form.get('message')  

        if not name or not email or not phone_number or not message:
            return "Please fill in all the required fields."


        entry=Contact(name=name, email=email, phone_number=phone_number,date=datetime.now(), message=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("Recieved Mail form "+name,
            sender=email, 
            recipients=[params['mail_user']], 
            body= message +"\n"+ phone_number
            ) 
        return redirect("/success")
    return render_template ("contact.html", params=params)


@app.route('/success')
def success():
    return "Form submitted successfully!"



app.run(debug=True)   