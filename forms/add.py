from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class Add(FlaskForm):
    title = StringField()
    submit = SubmitField()

