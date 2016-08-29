from todo import app
from manage import login_manager
from documents import User


@login_manager.user_loader
def load_user(user_id):
    """This callback is used to reload the user object from the user ID
    stored in the session. It takes the unicode ID of a user, and returns the
    corresponding user object. Returns None if ID is not valid.
    """

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        if not next_is_valid(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)
