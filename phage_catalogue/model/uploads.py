from copy import deepcopy
from functools import cached_property
from pathlib import Path
from flask import current_app
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from lbrc_flask.validators import is_integer, parse_date_or_none
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from werkzeug.utils import secure_filename
from itertools import compress, islice, takewhile
from openpyxl import load_workbook


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
        spreadsheet = Spreadsheet(self.local_filepath)
        upload_column_definition = UploadColumnDefinition()

        errors = upload_column_definition.validation_errors(spreadsheet)

        if errors:
            self.errors = "\n".join(errors)
            self.status = Upload.STATUS__ERROR

    def _consistency_errors(self, bacteria_row_filter, phage_row_filter):
        result = []

        for i, (bacterium, phage) in enumerate(zip(bacteria_row_filter, phage_row_filter), 1):
            if bacterium and phage:
                result.append(f"Row {i}: contains columns for both bacteria and phages")
            elif not bacterium and not phage:
                result.append(f"Row {i}: does not contain enough information")
        
        return result

    @property
    def is_error(self):
        return self.status == Upload.STATUS__ERROR


class ColumnDefinition():
    COLUMN_TYPE_STRING = 'str'
    COLUMN_TYPE_INTEGER = 'int'
    COLUMN_TYPE_DATE = 'date'

    @property
    def column_definition(self):
        return []
    
    @property
    def column_names(self):
        return [d['name'] for d in self.column_definition]

    def definition_for_column_name(self, name):
        for d in self.column_definition:
            if d['name'] == name:
                return d


class UploadColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(BacteriumOnlyColumnDefinition().column_definition)
        result.extend(PhageOnlyColumnDefinition().column_definition)

        return result

    def validation_errors(self, spreadsheet):
        errors = set()

        upload_validator = SpreadsheetValidator(spreadsheet, self)
        bactetria_validator = SpreadsheetValidator(spreadsheet, BacteriumFullColumnDefinition())
        phage_validator = SpreadsheetValidator(spreadsheet, PhageFullColumnDefinition())

        errors = errors.union(upload_validator.column_validation_errors())
        errors = errors.union(self._consistency_errors(bactetria_validator.row_filter, phage_validator.row_filter))
        errors = errors.union(bactetria_validator.data_validation_errors())
        errors = errors.union(phage_validator.data_validation_errors())

        return errors

    def _consistency_errors(self, bacteria_row_filter, phage_row_filter):
        result = []

        for i, (bacterium, phage) in enumerate(zip(bacteria_row_filter, phage_row_filter), 1):
            if bacterium and phage:
                result.append(f"Row {i}: contains columns for both bacteria and phages")
            elif not bacterium and not phage:
                result.append(f"Row {i}: does not contain enough information")
        
        return result


class SpecimenColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        return [
            dict(
                name='key',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
                allow_null=True,
            ),
            dict(
                name='freezer',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
            ),
            dict(
                name='drawer',
                type=ColumnDefinition.COLUMN_TYPE_INTEGER,
            ),
            dict(
                name='box_number',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='position',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=20,
            ),
            dict(
                name='description',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
            dict(
                name='project',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='date',
                type=ColumnDefinition.COLUMN_TYPE_DATE,
            ),
            dict(
                name='storage method',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='name',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
            dict(
                name='notes',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
            ),
        ]


class BacteriumOnlyColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        return [
            dict(
                name='bacterial species',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='strain',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='media',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='plasmid name',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='resistance marker',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
        ]


class BacteriumFullColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(BacteriumOnlyColumnDefinition().column_definition)

        return result

class PhageOnlyColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        return [
            dict(
                name='phage id',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            dict(
                name='host species',
                type=ColumnDefinition.COLUMN_TYPE_STRING,
                max_length=100,
            ),
        ]


class PhageFullColumnDefinition(ColumnDefinition):
    @property
    def column_definition(self):
        result = deepcopy(SpecimenColumnDefinition().column_definition)
        result.extend(PhageOnlyColumnDefinition().column_definition)

        return result


class Spreadsheet():
    def __init__(self, filepath: Path, header_rows: int = 1):
        self.filepath: Path = filepath
        self.header_rows: int = header_rows

    def worksheet(self):
        wb = load_workbook(filename=self.filepath, read_only=True)
        return wb.active

    @cached_property
    def column_names(self):
        rows = self.worksheet().values
        first_row = next(rows)

        result = [c.lower() for c in takewhile(lambda x: x, first_row)]

        return result

    def iter_rows(self):
        for r in self.worksheet().values:
            yield dict(zip(self.column_names, r))

    def iter_data(self):
        for r in islice(self.iter_rows(), self.header_rows, None):
            yield r


class SpreadsheetValidator:
    def __init__(self, spreadsheet: Spreadsheet, column_definition: ColumnDefinition):
        self.spreadsheet: Spreadsheet = spreadsheet
        self.column_definition: ColumnDefinition = column_definition
        self.row_filter: list[bool] = self.rows_with_fields_for_definition()
    
    def validation_errors(self):
        errors = []

        errors.extend(self.column_validation_errors())
        errors.extend(self.data_validation_errors())

        return errors

    def column_validation_errors(self):
        missing_columns = set(self.column_definition.column_names) - set(self.spreadsheet.column_names)
        return map(lambda x: f"Missing column '{x}'", missing_columns)

    def data_validation_errors(self):
        result = []

        rows = compress(self.spreadsheet.iter_data(), self.row_filter)

        for i, row in enumerate(rows, 1):
            row_errors = self._field_errors_for_def(row)
            result.extend(map(lambda e: f"Row {i}: {e}", row_errors))

        return result
    
    def rows_with_fields_for_definition(self):
        result = []

        for row in self.spreadsheet.iter_data():
            result.append(self._has_fields_for_definition(row))

        return result

    def _has_fields_for_definition(self, row: dict):
        for col_def in self.column_definition.column_definition:
            if not col_def.get('allow_null', False):
                if len(str(row.get(col_def['name']) or '').strip()) == 0:
                    return False
        
        return True
    
    def _field_errors_for_def(self, row: dict):
        result = []
        for col_def in self.column_definition.column_definition:
            if col_def['name'] in row:
                result.extend(self._field_errors(row, col_def))
        
        return result
    
    def _field_errors(self, row, col_def):
        result = []

        value = row[col_def['name']]

        allows_nulls = col_def.get('allow_null', False)
        if not allows_nulls:
            is_null = value is None or str(value).strip() == ''
            if is_null:
                result.append("Data is mising")

        match col_def['type']:
            case ColumnDefinition.COLUMN_TYPE_STRING:
                result.extend(self._is_invalid_string(value, col_def))
            case ColumnDefinition.COLUMN_TYPE_INTEGER:
                result.extend(self._is_invalid_interger(value, col_def))
            case ColumnDefinition.COLUMN_TYPE_DATE:
                result.extend(self._is_invalid_date(value, col_def))
        
        return map(lambda e: f"{col_def['name']}: {e}", result)

    def _is_invalid_string(self, value, col_def):
        if value is None:
            return []

        if max_length := col_def.get('max_length', None):
            if len(value) > max_length:
               return [f"Text is longer than {max_length} characters"]

        return []

    def _is_invalid_interger(self, value, col_def):
        if value is None:
            return []

        if not is_integer(value):
            return ["Invalid value"]
        
        return []

    def _is_invalid_date(self, value, col_def):
        if value is None:
            return []

        if parse_date_or_none(value) is None:
            return ["Invalid value"]
        
        return []
