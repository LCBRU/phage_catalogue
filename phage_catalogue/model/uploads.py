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

    @classmethod
    def column_definitions(self):
        defs = BacteriumData().column_definition()
        defs.update(PhageData().column_definition())

        return defs

    @classmethod
    def column_names(self):
        return Upload.column_definitions().keys()

    @property
    def local_filepath(self):
        return current_app.config["FILE_UPLOAD_DIRECTORY"] / secure_filename(f"{self.id}_{self.filename}")

    def validate(self):
        errors = set()

        spreadsheet = Spreadsheet(self.local_filepath)

        bacteria_data = BacteriumData()
        phage_data = PhageData()

        bacteria_row_filter = spreadsheet.rows_with_fields_for_definition(bacteria_data.column_definition())
        phage_row_filter = spreadsheet.rows_with_fields_for_definition(phage_data.column_definition())

        errors = errors.union(spreadsheet._column_validation_errors(bacteria_data.column_definition()))
        errors = errors.union(spreadsheet._column_validation_errors(phage_data.column_definition()))
        errors = errors.union(self._consistency_errors(bacteria_row_filter, phage_row_filter))

        errors = errors.union(spreadsheet._data_validation_errors(
            column_definition=bacteria_data.column_definition(),
            row_filter=bacteria_row_filter,
        ))

        errors = errors.union(spreadsheet._data_validation_errors(
            column_definition=phage_data.column_definition(),
            row_filter=phage_row_filter,
        ))

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


class SpecimenData():
    def column_definition(self):
        return {
            'key': dict(
                name='key',
                type=Spreadsheet.COLUMN_TYPE_INTEGER,
                allow_null=True,
            ),
            'freezer': dict(
                name='freezer',
                type=Spreadsheet.COLUMN_TYPE_INTEGER,
            ),
            'drawer': dict(
                name='drawer',
                type=Spreadsheet.COLUMN_TYPE_INTEGER,
            ),
            'box_number': dict(
                name='box_number',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'position': dict(
                name='position',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=20,
            ),
            'description': dict(
                name='description',
                type=Spreadsheet.COLUMN_TYPE_STRING,
            ),
            'project': dict(
                name='project',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'date': dict(
                name='date',
                type=Spreadsheet.COLUMN_TYPE_DATE,
            ),
            'storage method': dict(
                name='storage method',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'name': dict(
                name='name',
                type=Spreadsheet.COLUMN_TYPE_STRING,
            ),
            'notes': dict(
                name='notes',
                type=Spreadsheet.COLUMN_TYPE_STRING,
            ),
        }
    
    def column_names(self):
        return self.column_definition().keys()


class BacteriumData(SpecimenData):
    def column_definition(self):
        result = {
            'bacterial species': dict(
                name='bacterial species',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'strain': dict(
                name='strain',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'media': dict(
                name='media',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'plasmid name': dict(
                name='plasmid name',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'resistance marker': dict(
                name='resistance marker',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
        }
        result.update(super().column_definition())
        return result


class PhageData(SpecimenData):
    def column_definition(self):
        result = {
            'phage id': dict(
                name='phage id',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
            'host species': dict(
                name='host species',
                type=Spreadsheet.COLUMN_TYPE_STRING,
                max_length=100,
            ),
        }
        result.update(super().column_definition())
        return result


class Spreadsheet():
    COLUMN_TYPE_STRING = 'str'
    COLUMN_TYPE_INTEGER = 'int'
    COLUMN_TYPE_DATE = 'date'

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

    def validate(self, column_definition: dict, row_filter: list[bool]):
        errors = []

        errors.extend(self._column_validation_errors(column_definition))
        errors.extend(self._data_validation_errors(column_definition, row_filter))

        return errors

    def _column_validation_errors(self, column_definition: dict):
        missing_columns = set(column_definition.keys()) - set(self.column_names)
        return map(lambda x: f"Missing column '{x}'", missing_columns)

    def _data_validation_errors(self, column_definition: dict, row_filter: list[bool]):
        result = []

        rows = compress(self.iter_data(), row_filter)

        for i, row in enumerate(rows, 1):
            row_errors = self._field_errors_for_def(row, column_definition)
            result.extend(map(lambda e: f"Row {i}: {e}", row_errors))

        return result
    
    def rows_with_fields_for_definition(self, column_definition: dict):
        result = []

        for row in self.iter_data():
            result.append(self._has_fields_for_definition(row, column_definition))

        return result

    def _has_fields_for_definition(self, row: dict, column_definition: dict):
        for col_name, col_def in column_definition.items():
            if not col_def.get('allow_null', False):
                if len(str(row.get(col_name) or '').strip()) == 0:
                    return False
        
        return True
    
    def _field_errors_for_def(self, row: dict, column_definition: dict):
        result = []
        for col_name, col_def in column_definition.items():
            if col_name in row:
                result.extend(self._field_errors(row, col_name, col_def))
        
        return result
    
    def _field_errors(self, row, column_name, col_def):
        result = []

        value = row[column_name]

        allows_nulls = col_def.get('allow_null', False)
        if not allows_nulls:
            is_null = value is None or str(value).strip() == ''
            if is_null:
                result.append("Data is mising")

        match col_def['type']:
            case Spreadsheet.COLUMN_TYPE_STRING:
                result.extend(self._is_invalid_string(value, col_def))
            case Spreadsheet.COLUMN_TYPE_INTEGER:
                result.extend(self._is_invalid_interger(value, col_def))
            case Spreadsheet.COLUMN_TYPE_DATE:
                result.extend(self._is_invalid_date(value, col_def))
        
        return map(lambda e: f"{column_name}: {e}", result)

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
