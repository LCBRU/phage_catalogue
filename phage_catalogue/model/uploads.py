from copy import deepcopy
from flask import current_app
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from lbrc_flask.column_data import ColumnsDefinition, ExcelData, IntegerColumnDefinition, StringColumnDefinition, DateColumnDefinition, ColumnsDefinitionValidationMessage
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
            self.errors = "\n".join([e.full_message for e in errors])
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
                result.append(ColumnsDefinitionValidationMessage(
                    type=ColumnsDefinitionValidationMessage.TYPE__ERROR,
                    row=i,
                    message="does not contain enough information"
                ))

        return result

    def _both_phage_and_bacterium_errors(self, spreadsheet):
        result = []

        for i, (bacterium, phage) in enumerate(zip(
            BacteriumOnlyColumnDefinition().rows_with_any_fields(spreadsheet),
            PhageOnlyColumnDefinition().rows_with_any_fields(spreadsheet),
            ), 1):
            if bacterium and phage:
                result.append(ColumnsDefinitionValidationMessage(
                    type=ColumnsDefinitionValidationMessage.TYPE__ERROR,
                    row=i,
                    message="contains columns for both bacteria and phages"
                ))
        
        return result
    

class SpecimenColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            IntegerColumnDefinition(
                name='key',
                allow_null=True,
            ),
            IntegerColumnDefinition(
                name='freezer',
            ),
            IntegerColumnDefinition(
                name='drawer',
            ),
            StringColumnDefinition(
                name='box_number',
                max_length=100,
            ),
            StringColumnDefinition(
                name='position',
                max_length=20,
            ),
            StringColumnDefinition(
                name='description',
            ),
            StringColumnDefinition(
                name='project',
                max_length=100,
            ),
            DateColumnDefinition(
                name='date',
                translated_name='sample_date',
            ),
            StringColumnDefinition(
                name='storage method',
                max_length=100,
                translated_name='storage_method',
            ),
            StringColumnDefinition(
                name='name',
            ),
            StringColumnDefinition(
                name='staff member',
                translated_name='staff_member',
            ),
            StringColumnDefinition(
                name='notes',
            ),
        ]


class BacteriumOnlyColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            StringColumnDefinition(
                name='bacterial species',
                max_length=100,
                translated_name='species',
            ),
            StringColumnDefinition(
                name='strain',
                max_length=100,
            ),
            StringColumnDefinition(
                name='media',
                max_length=100,
                translated_name='medium',
            ),
            StringColumnDefinition(
                name='plasmid name',
                max_length=100,
                translated_name='plasmid',
            ),
            StringColumnDefinition(
                name='resistance marker',
                max_length=100,
                translated_name='resistance_marker',
            ),
        ]


class PhageOnlyColumnDefinition(ColumnsDefinition):
    @property
    def column_definition(self):
        return [
            StringColumnDefinition(
                name='phage id',
                max_length=100,
                translated_name='phage_identifier',
            ),
            StringColumnDefinition(
                name='host species',
                max_length=100,
                translated_name='host',
            ),
        ]


class SpecimenFullColumnDefinition(ColumnsDefinition):
    def __init__(self, cls, bacterial_species_name):
        super().__init__()
        self.cls = cls
        self.bacterial_species_name = bacterial_species_name
    
    def row_filter(self, spreadsheet):
        return self.rows_with_all_fields(spreadsheet)

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
                    errors.append(ColumnsDefinitionValidationMessage(
                    type=ColumnsDefinitionValidationMessage.TYPE__ERROR,
                    row=i,
                    message="Key does not exist"
                ))
                
                if not isinstance(existing, self.cls):
                    errors.append(ColumnsDefinitionValidationMessage(
                        type=ColumnsDefinitionValidationMessage.TYPE__ERROR,
                        row=i,
                        message="Key is for the wrong type of specimen"
                    ))

        return errors

    def _bacterial_species_errors(self, spreadsheet):
        errors = []

        for i, row in enumerate(self.iter_filtered_data(spreadsheet), 1):
            if bacterial_species_name := row.get(self.bacterial_species_name):
                existing = db.session.execute(select(BacterialSpecies).where(BacterialSpecies.name == bacterial_species_name)).scalar_one_or_none()

                if existing is None:
                    errors.append(ColumnsDefinitionValidationMessage(
                        type=ColumnsDefinitionValidationMessage.TYPE__ERROR,
                        row=i,
                        message=f"{self.bacterial_species_name.title()} does not exist"
                    ))

        return errors

        

class BacteriumFullColumnDefinition(SpecimenFullColumnDefinition):
    def __init__(self):
        super().__init__(Bacterium, bacterial_species_name='bacterial species')

    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(BacteriumOnlyColumnDefinition().column_definition)

        return result


class PhageFullColumnDefinition(SpecimenFullColumnDefinition):
    def __init__(self):
        super().__init__(Phage, bacterial_species_name='host species')

    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(PhageOnlyColumnDefinition().column_definition)

        return result
