from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator

from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, BoxNumber, Medium, Phage, PhageIdentifier, Plasmid, Project, ResistanceMarker, Specimen, StaffMember, StorageMethod, Strain
from phage_catalogue.model.uploads import Upload


class LookupFakeCreator(FakeCreator):
    def get(self, **kwargs):
        result = self.cls(
            name=kwargs.get('name', self.faker.pystr(min_chars=1, max_chars=100))
        )

        return result


class BacteriumFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Bacterium)

    def get(self, **kwargs):
        self.faker.add_provider(LookupProvider)

        result = self.cls(
            species = kwargs.get('species', self.faker.bacterial_species().choice_from_db()),
            strain = kwargs.get('strain', self.faker.strain().choice_from_db()),
            medium = kwargs.get('medium', self.faker.medium().choice_from_db()),
            plasmid = kwargs.get('plasmid', self.faker.plasmid().choice_from_db()),
            resistance_marker = kwargs.get('resistance_marker', self.faker.resistance_marker().choice_from_db()),
            sample_date = kwargs.get('sample_date', self.faker.date_object()),
            freezer = kwargs.get('freezer', self.faker.random_int()),
            drawer = kwargs.get('draw', self.faker.random_int()),
            position = kwargs.get('position', self.faker.random_letter()),
            description = kwargs.get('description', self.faker.sentence()),
            project = kwargs.get('project', self.faker.project().choice_from_db()),
            box_number = kwargs.get('box_number', self.faker.box_number().choice_from_db()),
            storage_method = kwargs.get('storage_method', self.faker.storage_method().choice_from_db()),
            staff_member = kwargs.get('staff_member', self.faker.staff_member().choice_from_db()),
            notes = kwargs.get('notes', self.faker.paragraph()),
            name = kwargs.get('name', f"Bacterium: {self.faker.pystr()}"),
        )

        return result


class PhageFakeCreator(FakeCreator):
    def __init__(self):
        super().__init__(Phage)

    def get(self, **kwargs):
        self.faker.add_provider(LookupProvider)

        result = self.cls(
            phage_identifier = kwargs.get('phage_identifier', self.faker.phage_identifier().choice_from_db()),
            host = kwargs.get('host', self.faker.bacterial_species().choice_from_db()),
            sample_date = kwargs.get('sample_date', self.faker.date_object()),
            freezer = kwargs.get('freezer', self.faker.random_int()),
            drawer = kwargs.get('draw', self.faker.random_int()),
            position = kwargs.get('position', self.faker.random_letter()),
            description = kwargs.get('description', self.faker.sentence()),
            project = kwargs.get('project', self.faker.project().choice_from_db()),
            box_number = kwargs.get('box_number', self.faker.box_number().choice_from_db()),
            storage_method = kwargs.get('storage_method', self.faker.storage_method().choice_from_db()),
            staff_member = kwargs.get('staff_member', self.faker.staff_member().choice_from_db()),
            notes = kwargs.get('notes', self.faker.paragraph()),
            name = kwargs.get('name', f"Phage: {self.faker.pystr()}"),
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
            filename = kwargs.get('filename', self.faker.file_name(extension='xslx')),
            status = kwargs.get('status', choice(Upload.STATUS_NAMES)),
            errors = kwargs.get('errors', '\n'.join([self.faker.sentence() for _ in range(5)])),
        )


class LookupProvider(BaseProvider):
    def create_standard_lookups(self):
        for _ in range(5):
            self.bacterial_species().get_in_db()
            self.strain().get_in_db()
            self.medium().get_in_db()
            self.plasmid().get_in_db()
            self.resistance_marker().get_in_db()
            self.phage_identifier().get_in_db()
            self.project().get_in_db()
            self.box_number().get_in_db()
            self.storage_method().get_in_db()
            self.staff_member().get_in_db()

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

    def bacteria_data(self, rows=10):
        result = []

        for _ in range(rows):
            b = self.generator.bacterium().get()
            result.append(b.data())
        
        return result

    def phage_data(self, rows=10):
        result = []

        for _ in range(rows):
            p = self.generator.phage().get()
            result.append(p.data())
        
        return result

    def specimen_data(self, rows=10):
        result = []

        for _ in range(rows):
            s = self.generator.specimen().get()
            result.append(s.data())
        
        return result
