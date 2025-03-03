from sqlalchemy import select
from phage_catalogue.model import Upload


def uploads_search_query(search_data):
    return select(Upload)
