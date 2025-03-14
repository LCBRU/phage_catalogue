from functools import cached_property
from flask import current_app
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from lbrc_flask.validators import is_integer, parse_date_or_none
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from werkzeug.utils import secure_filename
from itertools import takewhile
from openpyxl import load_workbook


class Upload(AuditMixin, CommonMixin, db.Model):
    CLASS_SPECIMEN = 'specimen'
    CLASS_BACTERIUM = 'bacterium'
    CLASS_PHAGE = 'phage'

    COLUMNS = {
        'key': dict(
            type='int',
            allow_null=True,
            cls=CLASS_SPECIMEN,
        ),
        'freezer': dict(
            type='int',
            cls=CLASS_SPECIMEN,
        ),
        'drawer': dict(
            type='int',
            cls=CLASS_SPECIMEN,
        ),
        'box_number': dict(
            type='str',
            cls=CLASS_SPECIMEN,
            max_length=100,
        ),
        'position': dict(
            type='str',
            max_length=20,
            cls=CLASS_SPECIMEN,
        ),
        'bacterial species': dict(
            type='str',
            max_length=100,
            cls=CLASS_BACTERIUM,
        ),
        'strain': dict(
            type='str',
            max_length=100,
            cls=CLASS_BACTERIUM,
        ),
        'media': dict(
            type='str',
            max_length=100,
            cls=CLASS_BACTERIUM,
        ),
        'plasmid name': dict(
            type='str',
            max_length=100,
            cls=CLASS_BACTERIUM,
        ),
        'resistance marker': dict(
            type='str',
            max_length=100,
            cls=CLASS_BACTERIUM,
        ),
        'phage id': dict(
            type='str',
            max_length=100,
            cls=CLASS_PHAGE,
        ),
        'host species': dict(
            type='str',
            max_length=100,
            cls=CLASS_PHAGE,
        ),
        'description': dict(
            type='str',
            cls=CLASS_SPECIMEN,
        ),
        'project': dict(
            type='str',
            max_length=100,
            cls=CLASS_SPECIMEN,
        ),
        'date': dict(
            type='date',
            cls=CLASS_SPECIMEN,
        ),
        'storage method': dict(
            type='str',
            max_length=100,
            cls=CLASS_SPECIMEN,
        ),
        'name': dict(
            type='str',
            cls=CLASS_SPECIMEN,
        ),
        'notes': dict(
            type='str',
            cls=CLASS_SPECIMEN,
        ),
    }

    STATUS__AWAITING_PROCESSING = 'Awaiting Processing'
    STATUS__PROCESSED = 'Processed'
    STATUS__ERROR = 'Error'

    STATUS_NAMES = [
        STATUS__AWAITING_PROCESSING,
        STATUS__PROCESSED,
        STATUS__ERROR,
    ]

    COLUMN_NAMES = set(COLUMNS.keys())

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
        rows = self.worksheet().values
        first_row = next(rows)

        result = [c.lower() for c in takewhile(lambda x: x, first_row)]

        return result

    def iter_rows(self):
        for r in self.worksheet().values:
            values = dict(zip(self.column_names, r))
            yield values

    def iter_data(self):
        for r in self.iter_rows():
            if self._is_data_row(r):
                yield r

    def _is_data_row(self, row):
        return 'key' in row.keys() and (row.get('key', None) is None or is_integer(row['key']))

    def validate(self):
        errors = []

        errors.extend(self._column_validation_errors())
        errors.extend(self._data_validation_errors())

        if errors:
            self.errors = "\n".join(errors)
            self.status = Upload.STATUS__ERROR

    def _column_validation_errors(self):
        missing_columns = Upload.COLUMN_NAMES - set(self.column_names)
        return map(lambda x: f"Missing column '{x}'", missing_columns)

    def _data_validation_errors(self):
        result = []

        for i, row in enumerate(self.iter_data(), 1):
            if self._is_ambigous_row(row):
                result.append(f"Row {i}: contains columns for both bacteria and phages")
            elif self._neither_phage_nor_bacterium(row):
                result.append(f"Row {i}: does not contain enough information")
            elif self._has_bacterium_fields(row):
                for e in self._bacterium_errors(row):
                    result.append(f"Row {i}: {e}")
            elif self._has_phage_fields(row):
                for e in self._phage_errors(row):
                    result.append(f"Row {i}: {e}")

        return result
    
    def _is_ambigous_row(self, row):
        return self._has_bacterium_fields(row) and self._has_phage_fields(row)

    def _neither_phage_nor_bacterium(self, row):
        has_complete_set_of_fields = self._has_specimen_fields(row) and (self._has_bacterium_fields(row) or self._has_phage_fields(row))
        return not has_complete_set_of_fields

    def _has_specimen_fields(self, row):
        return self._has_fields_for_class(row, Upload.CLASS_SPECIMEN)

    def _has_bacterium_fields(self, row):
        return self._has_fields_for_class(row, Upload.CLASS_BACTERIUM)

    def _has_phage_fields(self, row):
        return self._has_fields_for_class(row, Upload.CLASS_PHAGE)

    def _has_fields_for_class(self, row, cls):
        for col_name, col_def in Upload.COLUMNS.items():
            if col_def.get('cls', '') == cls:
                allow_nulls = col_def.get('allow_null', False)
                if not allow_nulls:
                    value = row.get(col_name)
                    if value is None or (str(row.get(col_name)) or '').strip() == '':
                        return False
        
        return True

    def _specimen_errors(self, row):
        result = self._field_errors_for_class(row, Upload.CLASS_SPECIMEN)
        
        return result

    def _bacterium_errors(self, row):
        result = []
        result.extend(self._specimen_errors(row))
        result.extend(self._field_errors_for_class(row, Upload.CLASS_BACTERIUM))

        return result

    def _phage_errors(self, row):
        result = []
        result.extend(self._specimen_errors(row))
        result.extend(self._field_errors_for_class(row, Upload.CLASS_PHAGE))

        return result

    def _field_errors_for_class(self, row, cls):
        result = []
        for col_name, col_def in Upload.COLUMNS.items():
            if col_def.get('cls', '') == cls:
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
            case 'str':
                result.extend(self._is_invalid_string(value, col_def))
            case 'int':
                result.extend(self._is_invalid_interger(value, col_def))
            case 'date':
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

    @property
    def is_error(self):
        return self.status == Upload.STATUS__ERROR
