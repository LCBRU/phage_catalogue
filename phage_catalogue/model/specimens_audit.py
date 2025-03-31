from datetime import date, datetime
from lbrc_flask.database import db
from lbrc_flask.model import CommonMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text


class SpecimenAudit(CommonMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    specimen_id: Mapped[int] = mapped_column()
    type: Mapped[str] = mapped_column(String(20), index=True)

    __mapper_args__ = {
        "polymorphic_on": type,
    }

    freezer: Mapped[int] = mapped_column()
    drawer: Mapped[int] = mapped_column()
    position: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text)
    sample_date: Mapped[date] = mapped_column()

    box_number: Mapped[str] = mapped_column(String(100))
    project: Mapped[str] = mapped_column(String(100))
    storage_method: Mapped[str] = mapped_column(String(100))
    staff_member: Mapped[str] = mapped_column(String(100))

    audit_action: Mapped[str] = mapped_column(String(200))
    audit_updated_date: Mapped[datetime] = mapped_column()
    audit_updated_by: Mapped[str] = mapped_column(String(200))


class BacteriumAudit(SpecimenAudit):
    __mapper_args__ = {
        "polymorphic_identity": 'Bacterium',
    }

    species: Mapped[str] = mapped_column(String(100), nullable=True)
    strain: Mapped[str] = mapped_column(String(100), nullable=True)
    medium: Mapped[str] = mapped_column(String(100), nullable=True)
    plasmid: Mapped[str] = mapped_column(String(100), nullable=True)
    resistance_marker: Mapped[str] = mapped_column(String(100), nullable=True)


class PhageAudit(SpecimenAudit):
    __mapper_args__ = {
        "polymorphic_identity": 'Phage',
    }

    phage_identifier: Mapped[str] = mapped_column(String(100), nullable=True)
    host: Mapped[str] = mapped_column(String(100), nullable=True)
