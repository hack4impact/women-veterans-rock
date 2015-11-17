from flask import url_for
from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectMultipleField,
    TextAreaField,
    DateField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, InputRequired, Optional
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    first_name = StringField('First name', validators=[
        DataRequired(),
        Length(1, 64)
    ])
    last_name = StringField('Last name', validators=[
        DataRequired(),
        Length(1, 64)
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', 'Passwords must match')
    ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to '
                                  '<a href="{}">log in</a> instead?)'
                                  .format(url_for('account.login')))


class RequestResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()])
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[DataRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(Form):
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('password2', 'Passwords must match.')
    ])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[
        DataRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[DataRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(Form):
    email = EmailField('New email', validators=[
        DataRequired(),
        Length(1, 64),
        Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class EditProfileForm(Form):
    first_name = StringField('First name', validators=[
        InputRequired(),
        Length(1, 64)
    ])
    last_name = StringField('Last name', validators=[
        InputRequired(),
        Length(1, 64)
    ])
    ''' This will not be hardcoded in the future,
        should be populated on the backend
        and changeable by admin '''
    affiliation_options = [
        ('1', 'Veteran'),
        ('2', 'Active Duty'),
        ('3', 'National Guard'),
        ('4', 'Reservist'),
        ('5', 'Spouse'),
        ('6', 'Dependent'),
        ('7', 'Family Member'),
        ('7', 'Supporter'),
        ('8', 'Other')]
    affiliation = SelectMultipleField(
        'Affiliation',
        choices=affiliation_options)
    bio = TextAreaField('About Me')
    birthday = DateField(
        label='Birthday',
        description="YYYY-MM-DD",
        format="%Y-%m-%d", validators=[ Optional() ])
    facebook_link = StringField('Facebook Profile', description="https://",
        validators=[ URL(), Optional() ])
    linkedin_link = StringField('LinkedIn Profile', description="https://",
        validators=[ URL(), Optional() ])
    submit = SubmitField('Update profile')
