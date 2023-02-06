from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, TextAreaField, HiddenField, SelectField, FormField, FieldList, Form
from wtforms.validators import DataRequired, Length
from web.models import User, TaskStateEnum, BoardRolesEnum

class TaskForm(FlaskForm):
    tid = HiddenField("id")
    name = StringField('Name', validators=[DataRequired()])
    state = SelectField('State', choices = [e.value for e in TaskStateEnum], validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    assignees = SelectMultipleField('Assignees')
    submit = SubmitField('Update with Task')

class ParticipantForm(Form):
    username = SelectField('Username', validators = [DataRequired()], choices = [(user.id, user.username) for user in User.query.all()])
    role = SelectField('Role', validators = [DataRequired()], choices = [(e.value, e.name) for e in BoardRolesEnum])
        
class BoardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    participants = FieldList(FormField(ParticipantForm))
    submit = SubmitField('Update Board')