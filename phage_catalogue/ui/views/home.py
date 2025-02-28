from .. import blueprint
from flask import render_template, request, url_for
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db
from sqlalchemy import select
from lbrc_flask.security import User
from wtforms import HiddenField, StringField
from wtforms.validators import Length
from lbrc_flask.forms import FlashingForm
from lbrc_flask.response import refresh_response


class EditUserForm(FlashingForm):
    id = HiddenField('id')
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])


@blueprint.route("/")
def index():
    search_form = SearchForm(formdata=request.args, search_placeholder='Search email addresses')

    q = select(User)

    if search_form.search.data:
        q = q.filter(User.email.like(f'%{search_form.search.data}%'))

    users = db.paginate(
        select=q,
        page=search_form.page.data,
        per_page=5,
        error_out=False,
    )

    return render_template(
        "ui/index.html",
        users=users,
        search_form=search_form,
    )


@blueprint.route("/another")
def another():
    return render_template("ui/another.html")


@blueprint.route("/dialog")
def dialog():
    return render_template("ui/dialog.html")


@blueprint.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    user = db.get_or_404(User, id)

    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.add(user)
        db.session.commit()
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=f"Edit User {user.full_name}",
        form=form,
        url=url_for('ui.edit', id=id),
    )
