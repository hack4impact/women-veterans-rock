from flask import url_for
from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    DateField,
    SelectMultipleField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Length,
    Email,
    EqualTo,
    URL,
    InputRequired,
    Optional,
)
from wtforms import ValidationError
from ..models import User, AffiliationTag


class LoginForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    first_name = StringField('First name', validators=[
        InputRequired(),
        Length(1, 64)
    ])
    last_name = StringField('Last name', validators=[
        InputRequired(),
        Length(1, 64)
    ])
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()
    ])
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('password2', 'Passwords must match')
    ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    zip_code = StringField('ZIP Code', validators=[
        InputRequired(),
        Length(5, 5)
    ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to '
                                  '<a href="{}">log in</a> instead?)'
                                  .format(url_for('account.login')))


class RequestResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()])
    new_password = PasswordField('New password', validators=[
        InputRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[InputRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(Form):
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('password2', 'Passwords must match.')
    ])
    password2 = PasswordField('Confirm new password',
                              validators=[InputRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    new_password = PasswordField('New password', validators=[
        InputRequired(),
        EqualTo('new_password2', 'Passwords must match.')
    ])
    new_password2 = PasswordField('Confirm new password',
                                  validators=[InputRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(Form):
    email = EmailField('New email', validators=[
        InputRequired(),
        Length(1, 64),
        Email()])
    password = PasswordField('Password', validators=[InputRequired()])
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
    bio = TextAreaField('About Me')
    birthday = DateField(
        label='Birthday',
        description="YYYY-MM-DD",
        format="%Y-%m-%d", validators=[Optional()])
    facebook_link = StringField(
        'Facebook Profile',
        description="https://",
        validators=[URL(), Optional()]
    )
    linkedin_link = StringField(
        'LinkedIn Profile',
        description="https://",
        validators=[URL(), Optional()]
    )
    affiliations = SelectMultipleField(
        'Affiliations',
        default=[]
    )
    submit = SubmitField('Update profile')

    def __init__(self, *args):
        super(EditProfileForm, self).__init__(*args)
        self.affiliations.choices = (
            [(str(affiliation.id), str(affiliation.name))
             for affiliation in AffiliationTag.query.all()]
        )
