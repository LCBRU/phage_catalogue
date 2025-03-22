from copy import deepcopy
from flask import current_app
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from lbrc_flask.column_data import ColumnDefinition, ColumnsDefinition, ExcelData
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, select
from werkzeug.utils import secure_filename

from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, Phage, Specimen


class Upload(AuditMixin, CommonMixin, db.Model):
    STATUS__AWAITING_PROCESSING = 'Awaiting Processing'
    STATUS__PROCESSED = 'Processed'
    STATUS__ERROR = 'Error'

    STATUS_NAMES = [
        STATUS__AWAITING_PROCESSING,
        STATUS__PROCESSED,
        STATUS__ERROR,
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default='')
    errors: Mapped[str] = mapped_column(Text, default='')

    @property
    def local_filepath(self):
        return current_app.config["FILE_UPLOAD_DIRECTORY"] / secure_filename(f"{self.id}_{self.filename}")

    def validate(self):
        spreadsheet = ExcelData(self.local_filepath)
        upload_column_definition = UploadColumnDefinition()

        errors = upload_column_definition.validation_errors(spreadsheet)

        if errors:
            self.errors = "\n".join(errors)
            self.status = Upload.STATUS__ERROR

    @property
    def is_error(self):
        return self.status == Upload.STATUS__ERROR

    def bacteria_data(self):
        spreadsheet = BacteriumFullColumnDefinition()

        return spreadsheet.translated_data(ExcelData(self.local_filepath))

    def phages_data(self):
        spreadsheet = PhageFullColumnDefinition()

        return spreadsheet.translated_data(ExcelData(self.local_filepath))


class UploadColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(BacteriumOnlyColumnDefinition().column_definition)
        result.extend(PhageOnlyColumnDefinition().column_definition)

        return result

    def validation_errors(self, spreadsheet):
        errors = []

        errors.extend(self.column_validation_errors(spreadsheet))
        if not errors:
            errors.extend(self._both_phage_and_bacterium_errors(spreadsheet))
            errors.extend(self._not_enough_columns_errors(spreadsheet))
            errors.extend(BacteriumFullColumnDefinition().data_validation_errors(spreadsheet))
            errors.extend(PhageFullColumnDefinition().data_validation_errors(spreadsheet))

        return errors

    def _not_enough_columns_errors(self, spreadsheet):
        result = []

        for i, (baceterium, phage) in enumerate(zip(
            BacteriumFullColumnDefinition().rows_with_all_fields(spreadsheet),
            PhageFullColumnDefinition().rows_with_all_fields(spreadsheet),
            ), 1):
            if not(phage or baceterium):
                result.append(f"Row {i}: does not contain enough information")

        return result

    def _both_phage_and_bacterium_errors(self, spreadsheet):
        result = []

        for i, (bacterium, phage) in enumerate(zip(
            BacteriumOnlyColumnDefinition().rows_with_any_fields(spreadsheet),
            PhageOnlyColumnDefinition().rows_with_any_fields(spreadsheet),
            ), 1):
            if bacterium and phage:
                result.append(f"Row {i}: contains columns for both bacteria and phages")
        
        return result
    

class SpecimenColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            ColumnDefinition(
                name='key',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
                allow_null=True,
            ),
            ColumnDefinition(
                name='freezer',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
            ),
            ColumnDefinition(
                name='drawer',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
            ),
            ColumnDefinition(
                name='box_number',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            ColumnDefinition(
                name='position',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=20,
            ),
            ColumnDefinition(
                name='description',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
            ColumnDefinition(
                name='project',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            ColumnDefinition(
                name='date',
                type=ColumnDefinition.COLUMN_TYPE_DATE,
                translated_name='sample_date',
            ),
            ColumnDefinition(
                name='storage method',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='storage_method',
            ),
            ColumnDefinition(
                name='name',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
            ColumnDefinition(
                name='staff member',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                translated_name='staff_member',
            ),
            ColumnDefinition(
                name='notes',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
        ]


class BacteriumOnlyColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            ColumnDefinition(
                name='bacterial species',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='species',
            ),
            ColumnDefinition(
                name='strain',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            ColumnDefinition(
                name='media',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='medium',
            ),
            ColumnDefinition(
                name='plasmid name',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='plasmid',
            ),
            ColumnDefinition(
                name='resistance marker',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='resistance_marker',
            ),
        ]


class PhageOnlyColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            ColumnDefinition(
                name='phage id',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='phage_identifier',
            ),
            ColumnDefinition(
                name='host species',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
                translated_name='host',
            ),
        ]


class SpecimenFullColumnDefinition(ColumnsDefinition):
    def __init__(self, cls, bacterial_species_name):
        self.cls = cls
        self.bacterial_species_name = bacterial_species_name
    
    def data_validation_errors(self, spreadsheet):
        errors = []

        errors.extend(super().data_validation_errors(spreadsheet))
        errors.extend(self._key_errors(spreadsheet))
        errors.extend(self._bacterial_species_errors(spreadsheet))

        return errors
    
    def _key_errors(self, spreadsheet):
        errors = []

        for i, row in enumerate(self.iter_filtered_data(spreadsheet), 1):
            if key := row.get('key'):
                existing = db.session.get(Specimen, key)

                if existing is None:
                    errors.append(f"Row {i}: Key does not exist")
                
                if not isinstance(existing, self.cls):
                    errors.append(f"Row {i}: Key is for the wrong type of specimen")

        return errors

    def _bacterial_species_errors(self, spreadsheet):
        errors = []

        for i, row in enumerate(self.iter_filtered_data(spreadsheet), 1):
            if bacterial_species_name := row.get(self.bacterial_species_name):
                existing = db.session.execute(select(BacterialSpecies).where(BacterialSpecies.name == bacterial_species_name)).scalar_one_or_none()

                if existing is None:
                    errors.append(f"Row {i}: {self.bacterial_species_name.title()} does not exist")

        return errors

        

class BacteriumFullColumnDefinition(SpecimenFullColumnDefinition):
    def __init__(self):
        super().__init__(Bacterium, bacterial_species_name='bacterial species')

    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(BacteriumOnlyColumnDefinition().column_definition)

        return result

    def data_validation_errors(self, spreadsheet):
        errors = []

        errors.extend(super().data_validation_errors(spreadsheet))
        errors.extend(self._bacterial_species_errors(spreadsheet))

        return errors


class PhageFullColumnDefinition(SpecimenFullColumnDefinition):
    def __init__(self):
        super().__init__(Phage, bacterial_species_name='host species')

    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(PhageOnlyColumnDefinition().column_definition)

        return result
