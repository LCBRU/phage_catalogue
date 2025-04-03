from flask_wtf.file import FileRequired
from phage_catalogue.model.uploads import Upload
from phage_catalogue.security import ROLENAME_UPLOADER
from phage_catalogue.services.uploads import upload_save, upload_search_query
from .. import blueprint
from flask import render_template, request, url_for
from lbrc_flask.forms import SearchForm
from lbrc_flask.database import db
from lbrc_flask.forms import FlashingForm, FileField
from lbrc_flask.response import refresh_response
from flask_security.decorators import roles_accepted


class UploadForm(FlashingForm):
    sample_file = FileField(
        'Sample File',
        accept=['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        validators=[FileRequired()],
    )


@blueprint.route("/uploads/")
@roles_accepted(ROLENAME_UPLOADER)
def uploads_index():
    search_form = SearchForm(formdata=request.args, search_placeholder='Search upload filenames')

    q = upload_search_query(search_form.data)
    q = q.order_by(Upload.created_date.desc())

    uploads = db.paginate(select=q)

    return render_template(
        "ui/uploads/index.html",
        uploads=uploads,
        search_form=search_form,
    )


@blueprint.route("/uploads/upload", methods=['GET', 'POST'])
@roles_accepted(ROLENAME_UPLOADER)
def uploads_upload(id=None):
    form = UploadForm()
    title = f"Upload Sample File"

    if form.validate_on_submit():
        upload_save(form.data)
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=title,
        form=form,
        url=url_for('ui.uploads_upload', id=id),
    )
