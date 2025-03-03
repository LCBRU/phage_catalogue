from phage_catalogue.services.uploads import uploads_search_query
from .. import blueprint
from flask import render_template, request
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db


@blueprint.route("/uploads/")
def uploads_index():
    search_form = SearchForm(formdata=request.args, search_placeholder='Search uploads')

    q = uploads_search_query(search_form.data)

    uploads = db.paginate(select=q)

    return render_template(
        "ui/uploads/index.html",
        uploads=uploads,
        search_form=search_form,
    )
