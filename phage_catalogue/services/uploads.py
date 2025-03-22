from sqlalchemy import select
from lbrc_flask.database import db

from phage_catalogue.model.uploads import Upload
from phage_catalogue.services.specimens import specimen_bacteria_save, specimen_phages_save


def upload_search_query(search_data=None):
    q = select(Upload)

    search_data = search_data or []

    if x := search_data.get('search'):
        for word in x.split():
            q = q.where(Upload.filename.like(f"%{word}%"))

    return q


def upload_save(data):
    u: Upload = Upload(filename=data['sample_file'].filename)

    db.session.add(u)
    db.session.flush()

    u.local_filepath.parent.mkdir(parents=True, exist_ok=True)
    data['sample_file'].save(u.local_filepath)

    upload_process(u)

    db.session.commit()


def upload_process(upload: Upload):
    upload.validate()

    if not upload.is_error:
        specimen_bacteria_save(upload.bacteria_data())
        specimen_phages_save(upload.phages_data())
        upload.status = Upload.STATUS__AWAITING_PROCESSING

    db.session.add(upload)
    db.session.commit()
