from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField,FloatField

class Edit(FlaskForm):
    rating = FloatField("Rating")
    review = StringField("Review")
    submit = SubmitField("Update")