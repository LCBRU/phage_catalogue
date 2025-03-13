from sqlalchemy import select
from lbrc_flask.database import db

from phage_catalogue.model.uploads import Upload


def upload_search_query(search_data):
    return select(Upload)


def upload_save(data):
    u: Upload = Upload(filename=data['sample_file'].filename)

    db.session.add(u)
    db.session.flush()

    u.local_filepath.parent.mkdir(parents=True, exist_ok=True)
    data['sample_file'].save(u.local_filepath)

    process_upload(u)

    db.session.commit()


def process_upload(upload: Upload):
    upload.validate()

    if not upload.is_error:
        upload.status = Upload.STATUS__AWAITING_PROCESSING

    db.session.add(upload)
    db.session.commit()
