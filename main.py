from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, EmailField, TextAreaField
from wtforms.validators import DataRequired, URL, Email
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import smtplib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR CONFIG KEY'
ckeditor = CKEditor(app)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(1000), nullable=False)


class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author Name", validators=[DataRequired()])
    img_url = URLField("Banner Image URL", validators=[DataRequired(), URL()])

    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
    reload = SubmitField("Reload Post")


class ContactForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = EmailField("E-Mail Address", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = TextAreaField("Message", widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField("Send Message")


@app.route("/")
def home():
    posts = db.session.query(BlogPost).all()
    last_post = BlogPost.query.filter_by()
    return render_template("index.html", all_posts=posts, featured_post=posts[-1])


@app.route("/post/<int:post_id>")
def show_post(post_id):
    posts = db.session.query(BlogPost).all()
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post, all_posts=posts)


@app.route("/new-post", methods=["GET", "POST"])
def create_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("new-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("new-post.html", form=edit_form, is_edit=True)


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/about")
def about():
    posts = db.session.query(BlogPost).all()
    return render_template("about.html", all_posts=posts)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if request.method == "POST":
        data = request.form
        send_mail(data["name"], data["email"], data["subject"], data["message"])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", form=form, msg_sent=False)


def send_mail(name, email, subject, message):
    my_email = "YOUR EMAIL ADDRESS"
    password = "YOUR EMAIL PASSWORD"

    title = "You have a message! from Aytac's Blog"

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
            from_addr=my_email,
            to_addrs=my_email,
            msg=f"Subject:{title}\n\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage:{message}"
        )


@app.route("/widgets")
def widget():
    posts = db.session.query(BlogPost).all()
    return render_template("widgets.html", all_posts=posts, index=0)

if __name__ == "__main__":
    app.run(debug=True)

