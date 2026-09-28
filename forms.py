from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import HiddenInput


class FocusForm(FlaskForm):
    name = StringField(
        "Focus Name",
        validators=[DataRequired(), Length(max=100)],
    )
    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(max=800)],
    )
    completion_time = StringField(
        "Estimated Completion Time",
        validators=[Optional(), Length(max=50)],
    )
    points = IntegerField(
        "Points",
        default=10,
        validators=[DataRequired(), NumberRange(min=1, max=9999)],
    )
    scope = SelectField(
        "Tree",
        choices=[
            ("yearly", "Yearly"),
            ("monthly", "Monthly"),
            ("weekly", "Weekly"),
            ("lifetime", "Lifetime"),
        ],
        validators=[DataRequired()],
    )
    parent_id = SelectField(
        "Prerequisite",
        coerce=int,
        choices=[(0, "None (root focus)")],
        validators=[Optional()],
    )
    icon = StringField(
        "Icon",
        widget=HiddenInput(),
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Add Focus")
