from flask import render_template, redirect, request, url_for, flash, abort
from flask.ext.login import (
    login_required,
    login_user,
    logout_user,
    current_user
)
from . import account
from .. import db
from ..email import send_email
from ..models import User, ZIPCode, AffiliationTag
from .forms import (
    LoginForm,
    RegistrationForm,
    CreatePasswordForm,
    ChangePasswordForm,
    ChangeEmailForm,
    RequestResetPasswordForm,
    ResetPasswordForm,
    EditProfileForm,
)


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        zip_code = ZIPCode.create_zip_code(form.zip_code.data)
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data,
                    zip_code_id=zip_code.id)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'account/email/confirm', user=user, token=token)
        flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        return redirect(url_for('main.index'))
    return render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            send_email(user.email,
                       'Reset Your Password',
                       'account/email/reset_password',
                       user=user,
                       token=token,
                       next=request.args.get('next'))
        flash('A password reset link has been sent to {}.'
              .format(form.email.data),
              'warning')
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email,
                       'Confirm Your New Email',
                       'account/email/change_email',
                       user=current_user,
                       token=token)
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'account/email/confirm', user=current_user, token=token)
    flash('A new confirmation link has been sent to {}.'.
          format(current_user.email),
          'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        flash('Your account has been confirmed.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/join-from-invite/<int:user_id>/<token>',
               methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated():
        flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
            form = CreatePasswordForm()
            if form.validate_on_submit():
                new_user.password = form.password.data
                db.session.add(new_user)
                db.session.commit()
                flash('Your password has been set. After you log in, you can '
                      'go to the "Your Account" page to review your account '
                      'information and settings.', 'success')
                return redirect(url_for('account.login'))
            return render_template('account/join_invite.html', form=form)
    else:
        flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        send_email(new_user.email,
                   'You Are Invited To Join',
                   'account/email/invite',
                   user=new_user,
                   user_id=new_user.id,
                   token=token)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated() \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')


@account.route('/profile')
@login_required
def profile_current():
    """Display the current logged in User's profile."""
    return redirect(url_for('account.profile', user_id=current_user.id))


@account.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    """Display a user's profile."""
    user = User.query.get(user_id)
    if user is None:
        abort(404)
    is_current = user.id == current_user.id
    return render_template('account/profile.html', user=user,
                           is_current=is_current)


@account.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """User can edit their own profile."""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.birthday = form.birthday.data
        current_user.bio = form.bio.data
        # Remove current affiliation tags.
        current_user.tags = [tag for tag in current_user.tags
                             if tag.type != "AffiliationTag"]

        # Add new affiliation tags.
        for affiliation_tag_id in form.affiliations.data:
            affiliation_tag = AffiliationTag.query.get(affiliation_tag_id)
            current_user.tags.append(affiliation_tag)

        db.session.add(current_user)
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('account.profile', user_id=current_user.id))
    else:
        # Populating form with current user profile information.
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.birthday.data = current_user.birthday
        form.bio.data = current_user.bio
        for affiliation_tag in current_user.tags:
            if affiliation_tag.type == "AffiliationTag":
                form.affiliations.default.append(str(affiliation_tag.id))

    return render_template(
        'account/edit_profile.html',
        user=current_user,
        form=form,
        affiliations=AffiliationTag.query.order_by(AffiliationTag.name).all())


@account.route('/donate')
@login_required
def donate():
    """Display donate page with PayPal link."""
    return render_template('account/donate.html')
