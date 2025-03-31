from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator

from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, BoxNumber, Medium, Phage, PhageIdentifier, Plasmid, Project, ResistanceMarker, Specimen, StaffMember, StorageMethod, Strain
from phage_catalogue.model.uploads import Upload
from tests import convert_specimens_to_spreadsheet_data


class LookupFakeCreator(FakeCreator):
    def get(self, **kwargs):
        result = self.cls(
            name=kwargs.get('name', self.faker.pystr(min_chars=1, max_chars=100))
        )

        return result
    
    def get_value_or_get(self, source, key, from_db):
        if key in source:
            return source[key]
        elif from_db:
            return self.choice_from_db()
        else:
            return self.get()


class BacteriumFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Bacterium)

    def get(self, lookups_in_db=True, **kwargs):
        self.faker.add_provider(LookupProvider)

        result = self.cls(
            species =  self.faker.bacterial_species().get_value_or_get(kwargs, 'species', lookups_in_db),
            strain = self.faker.strain().get_value_or_get(kwargs, 'strain', lookups_in_db),
            medium = self.faker.medium().get_value_or_get(kwargs, 'medium', lookups_in_db),
            plasmid = self.faker.plasmid().get_value_or_get(kwargs, 'plasmid', lookups_in_db),
            resistance_marker = self.faker.resistance_marker().get_value_or_get(kwargs, 'resistance_marker', lookups_in_db),
            sample_date = kwargs.get('sample_date') or self.faker.date_object(),
            freezer = kwargs.get('freezer') or self.faker.random_int(),
            drawer = kwargs.get('draw') or self.faker.random_int(),
            position = kwargs.get('position') or self.faker.random_letter(),
            description = kwargs.get('description') or self.faker.sentence(),
            project = self.faker.project().get_value_or_get(kwargs, 'project', lookups_in_db),
            box_number = self.faker.box_number().get_value_or_get(kwargs, 'box_number', lookups_in_db),
            storage_method = self.faker.storage_method().get_value_or_get(kwargs, 'storage_method', lookups_in_db),
            staff_member = self.faker.staff_member().get_value_or_get(kwargs, 'staff_member', lookups_in_db),
            notes = kwargs.get('notes') or self.faker.paragraph(),
            name = kwargs.get('name') or f"Bacterium: {self.faker.pystr()}",
        )

        return result


class PhageFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Phage)

    def get(self, lookups_in_db=True, **kwargs):
        self.faker.add_provider(LookupProvider)

        result = self.cls(
            phage_identifier = self.faker.phage_identifier().get_value_or_get(kwargs, 'phage_identifier', lookups_in_db),
            host = self.faker.bacterial_species().get_value_or_get(kwargs, 'host', lookups_in_db),
            sample_date = kwargs.get('sample_date') or self.faker.date_object(),
            freezer = kwargs.get('freezer') or self.faker.random_int(),
            drawer = kwargs.get('draw') or self.faker.random_int(),
            position = kwargs.get('position') or self.faker.random_letter(),
            description = kwargs.get('description') or self.faker.sentence(),
            project = self.faker.project().get_value_or_get(kwargs, 'project', lookups_in_db),
            box_number = self.faker.box_number().get_value_or_get(kwargs, 'box_number', lookups_in_db),
            storage_method = self.faker.storage_method().get_value_or_get(kwargs, 'storage_method', lookups_in_db),
            staff_member = self.faker.staff_member().get_value_or_get(kwargs, 'staff_member', lookups_in_db),
            notes = kwargs.get('notes') or self.faker.paragraph(),
            name = kwargs.get('name') or f"Phage: {self.faker.pystr()}",
        )

        return result


class SpecimenFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Specimen)

    def get(self, **kwargs):
        creator_cls = choice([BacteriumFakeCreator, PhageFakeCreator])
        creator = creator_cls()
        return creator.get(**kwargs)


class UploadFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Upload)

    def get(self, **kwargs):
        return self.cls(
            filename = kwargs.get('filename') or self.faker.file_name(extension='xslx'),
            status = kwargs.get('status') or choice(Upload.STATUS_NAMES),
            errors = kwargs.get('errors') or '\n'.join([self.faker.sentence() for _ in range(5)]),
        )


class LookupProvider(BaseProvider):

    def bacterial_species_name(self, i):
        return f"Bacterium {i}"

    def strain_name(self, i):
        return f"Strain {i}"

    def medium_name(self, i):
        return f"Medium {i}"

    def plasmid_name(self, i):
        return f"Plasmid {i}"

    def resistance_marker_name(self, i):
        return f"Resistance Marker {i}"

    def phage_identifier_name(self, i):
        return f"Phage Identifier {i}"

    def project_name(self, i):
        return f"Project {i}"

    def box_number_name(self, i):
        return f"Box Number {i}"

    def storage_method_name(self, i):
        return f"Storage Method {i}"

    def staff_member_name(self, i):
        return f"Staff Member {i}"

    def create_standard_lookups(self):
        for i in range(5):
            self.bacterial_species().get_in_db(name=self.bacterial_species_name(i))
            self.strain().get_in_db(name=self.strain_name(i))
            self.medium().get_in_db(name=self.medium_name(i))
            self.plasmid().get_in_db(name=self.plasmid_name(i))
            self.resistance_marker().get_in_db(name=self.resistance_marker_name(i))
            self.phage_identifier().get_in_db(name=self.phage_identifier_name(i))
            self.project().get_in_db(name=self.project_name(i))
            self.box_number().get_in_db(name=self.box_number_name(i))
            self.storage_method().get_in_db(name=self.storage_method_name(i))
            self.staff_member().get_in_db(name=self.staff_member_name(i))

    def bacterial_species(self):
        return LookupFakeCreator(BacterialSpecies)

    def strain(self):
        return LookupFakeCreator(Strain)

    def medium(self):
        return LookupFakeCreator(Medium)

    def plasmid(self):
        return LookupFakeCreator(Plasmid)

    def resistance_marker(self):
        return LookupFakeCreator(ResistanceMarker)

    def phage_identifier(self):
        return LookupFakeCreator(PhageIdentifier)

    def project(self):
        return LookupFakeCreator(Project)

    def box_number(self):
        return LookupFakeCreator(BoxNumber)

    def storage_method(self):
        return LookupFakeCreator(StorageMethod)

    def staff_member(self):
        return LookupFakeCreator(StaffMember)


class SpecimenProvider(BaseProvider):
    def bacterium(self):
        return BacteriumFakeCreator()

    def phage(self):
        return PhageFakeCreator()

    def specimen(self):
        return SpecimenFakeCreator()


class UploadProvider(BaseProvider):
    def upload(self):
        return UploadFakeCreator()

    def bacteria_spreadsheet_data(self, rows=10):
        result = []

        for _ in range(rows):
            b = self.generator.bacterium().get()
            result.append(b)
        
        return convert_specimens_to_spreadsheet_data(result)

    def phage_spreadsheet_data(self, rows=10):
        result = []

        for _ in range(rows):
            p = self.generator.phage().get()
            result.append(p)
        
        return convert_specimens_to_spreadsheet_data(result)

    def specimen_spreadsheet_data(self, rows=10):
        result = []

        for _ in range(rows):
            s = self.generator.specimen().get()
            result.append(s)
        
        return convert_specimens_to_spreadsheet_data(result)
