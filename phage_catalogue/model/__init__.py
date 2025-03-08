from datetime import date
from functools import cached_property
from flask import current_app
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text
from werkzeug.utils import secure_filename
from itertools import takewhile
from openpyxl import load_workbook

class Upload(AuditMixin, CommonMixin, db.Model):
    COLUMN_NAME__KEY = 'key'
    COLUMN_NAME__FREEZER = 'freezer'
    COLUMN_NAME__DRAWER = 'drawer'
    COLUMN_NAME__BOX_NUMBER = 'box_number'
    COLUMN_NAME__POSITION = 'position'
    COLUMN_NAME__BACTERIAL_SPECIES = 'bacterial species'
    COLUMN_NAME__STRAIN = 'strain'
    COLUMN_NAME__MEDIA = 'media'
    COLUMN_NAME__PLASMID = 'plasmid name'
    COLUMN_NAME__RESISTANCE_MARKER = 'resistance marker'
    COLUMN_NAME__PHAGE_ID = 'phage id'
    COLUMN_NAME__HOST_SPECIES = 'host species'
    COLUMN_NAME__DESCRIPTION = 'description'
    COLUMN_NAME__PROJECT = 'project'
    COLUMN_NAME__DATE = 'date'
    COLUMN_NAME__STORAGE_METHOD = 'storage method'
    COLUMN_NAME__NAME = 'name'
    COLUMN_NAME__NOTES = 'notes'

    STATUS__AWAITING_PROCESSING = 'Awaiting Processing'
    STATUS__PROCESSED = 'Processed'
    STATUS__ERROR = 'Error'

    STATUS_NAMES = [
        STATUS__AWAITING_PROCESSING,
        STATUS__PROCESSED,
        STATUS__ERROR,
    ]

    COLUMN_NAMES = [
        COLUMN_NAME__KEY,
        COLUMN_NAME__FREEZER,
        COLUMN_NAME__DRAWER,
        COLUMN_NAME__BOX_NUMBER,
        COLUMN_NAME__POSITION,
        COLUMN_NAME__BACTERIAL_SPECIES,
        COLUMN_NAME__STRAIN,
        COLUMN_NAME__MEDIA,
        COLUMN_NAME__PLASMID,
        COLUMN_NAME__RESISTANCE_MARKER,
        COLUMN_NAME__PHAGE_ID,
        COLUMN_NAME__HOST_SPECIES,
        COLUMN_NAME__DESCRIPTION,
        COLUMN_NAME__PROJECT,
        COLUMN_NAME__DATE,
        COLUMN_NAME__STORAGE_METHOD,
        COLUMN_NAME__NAME,
        COLUMN_NAME__NOTES,
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default='')
    errors: Mapped[str] = mapped_column(Text, default='')

    @property
    def local_filepath(self):
        return current_app.config["FILE_UPLOAD_DIRECTORY"] / secure_filename(f"{self.id}_{self.filename}")

    def worksheet(self):
        wb = load_workbook(filename=self.local_filepath, read_only=True)
        return wb.active

    @cached_property
    def column_names(self):
        rows = self.worksheet().iter_rows(min_row=1, max_row=1)
        first_row = next(rows)

        return [c.value.lower() for c in takewhile(lambda x: x.value, first_row)]

    @cached_property
    def first_data_row(self):
        def is_header(row):
            first_column = row[0].value.strip()
            return len(first_column) > 0 and first_column.isnumeric() == False

        return len([r for r in takewhile(is_header, self.worksheet())]) + 1

    def iter_rows(self):
        for r in self.worksheet().iter_rows(min_row=self.first_data_row, values_only=True):
            yield dict(zip(self.column_names, r))

    def validate(self):
        errors = []

        for missing_column in list(set(Upload.COLUMN_NAMES) - set(self.column_names)):
            errors.append(f"Missing column '{missing_column}'")

        if errors:
            self.errors = "\n".join(errors)
            self.status = Upload.STATUS__ERROR
    
    @property
    def is_error(self):
        return self.status == Upload.STATUS__ERROR


class Lookup(AuditMixin, CommonMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, unique=True)

    def __str__(self):
        return self.name

class BacterialSpecies(Lookup, db.Model):
    pass

class Strain(Lookup, db.Model):
    pass

class Medium(Lookup, db.Model):
    pass

class Plasmid(Lookup, db.Model):
    pass

class ResistanceMarker(Lookup, db.Model):
    pass

class PhageIdentifier(Lookup, db.Model):
    pass

class Project(Lookup, db.Model):
    pass

class StorageMethod(Lookup, db.Model):
    pass

class StaffMember(Lookup, db.Model):
    pass

class Specimen(AuditMixin, CommonMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20), index=True)

    __mapper_args__ = {
        "polymorphic_on": type,
    }

    freezer: Mapped[int] = mapped_column(index=True)
    draw: Mapped[int] = mapped_column(index=True)
    position: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str] = mapped_column(Text, index=True)
    notes: Mapped[str] = mapped_column(Text, index=True)
    sample_date: Mapped[date] = mapped_column(index=True)

    project_id: Mapped[int] = mapped_column(ForeignKey(Project.id), index=True, nullable=True)
    project: Mapped[Project] = relationship(foreign_keys=[project_id])
    storage_method_id: Mapped[int] = mapped_column(ForeignKey(StorageMethod.id), index=True, nullable=True)
    storage_method: Mapped[StorageMethod] = relationship(foreign_keys=[storage_method_id])
    staff_member_id: Mapped[int] = mapped_column(ForeignKey(StaffMember.id), index=True, nullable=True)
    staff_member: Mapped[StaffMember] = relationship(foreign_keys=[staff_member_id])

    @property
    def is_bacterium(self):
        return False

    @property
    def is_phage(self):
        return False


class Bacterium(Specimen):
    __mapper_args__ = {
        "polymorphic_identity": 'Bacterium',
    }

    species_id: Mapped[int] = mapped_column(ForeignKey(BacterialSpecies.id), index=True, nullable=True)
    species: Mapped[BacterialSpecies] = relationship(foreign_keys=[species_id])
    strain_id: Mapped[int] = mapped_column(ForeignKey(Strain.id), index=True, nullable=True)
    strain: Mapped[Strain] = relationship(foreign_keys=[strain_id])
    medium_id: Mapped[int] = mapped_column(ForeignKey(Medium.id), index=True, nullable=True)
    medium: Mapped[Medium] = relationship(foreign_keys=[medium_id])
    plasmid_id: Mapped[int] = mapped_column(ForeignKey(Plasmid.id), index=True, nullable=True)
    plasmid: Mapped[Plasmid] = relationship(foreign_keys=[plasmid_id])
    resistance_marker_id: Mapped[int] = mapped_column(ForeignKey(ResistanceMarker.id), index=True, nullable=True)
    resistance_marker: Mapped[ResistanceMarker] = relationship(foreign_keys=[resistance_marker_id])

    @property
    def is_bacterium(self):
        return True



class Phage(Specimen):
    __mapper_args__ = {
        "polymorphic_identity": 'Phage',
    }

    phage_identifier_id: Mapped[int] = mapped_column(ForeignKey(PhageIdentifier.id), index=True, nullable=True)
    phage_identifier: Mapped[PhageIdentifier] = relationship(foreign_keys=[phage_identifier_id])
    host_id: Mapped[int] = mapped_column(ForeignKey(BacterialSpecies.id), index=True, nullable=True)
    host: Mapped[BacterialSpecies] = relationship(foreign_keys=[host_id])

    @property
    def is_phage(self):
        return True
