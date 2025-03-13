from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Lookup(AuditMixin, CommonMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, unique=True)

    def __str__(self):
        return self.name
