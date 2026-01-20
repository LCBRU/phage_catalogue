from functools import cache
from random import choice
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator, FakeCreatorArgs, LookupFakeCreator
from lbrc_flask.database import db
from sqlalchemy import select
from phage_catalogue.model.specimens import BacterialSpecies, Bacterium, BoxNumber, Medium, Phage, PhageIdentifier, Plasmid, Project, ResistanceMarker, Specimen, StaffMember, StorageMethod, Strain
from phage_catalogue.model.uploads import Upload
from tests import convert_specimens_to_spreadsheet_data


class BacteriumFakeCreator(FakeCreator):
    cls = Bacterium

    def _create_item(self, save: bool, args: FakeCreatorArgs):
        if args.get('lookups_in_db', True):
            lookup_getter = args.get_or_choice_from_db
        else:
            lookup_getter = args.get_or_create

        result = self.cls(
            species = lookup_getter('species', self.faker.bacterial_species()),
            strain = lookup_getter('strain', self.faker.strain()),
            medium = lookup_getter('medium', self.faker.medium()),
            plasmid = lookup_getter('plasmid', self.faker.plasmid()),
            resistance_marker = lookup_getter('resistance_marker', self.faker.resistance_marker()),
            sample_date = args.get('sample_date', self.faker.date_object()),
            freezer = args.get('freezer', self.faker.random_int()),
            drawer = args.get('drawer', self.faker.random_int()),
            position = args.get('position', self.faker.random_letter()),
            description = args.get('description', self.faker.sentence()),
            project = lookup_getter('project', self.faker.project()),
            box_number = lookup_getter('box_number', self.faker.box_number()),
            storage_method = lookup_getter('storage_method', self.faker.storage_method()),
            staff_member = lookup_getter('staff_member', self.faker.staff_member()),
            notes = args.get('notes', self.faker.paragraph()),
            name = args.get('name', f"Bacterium: {self.faker.pystr()}"),
        )

        return result


class PhageFakeCreator(FakeCreator):
    cls = Phage

    def _create_item(self, save: bool, args: FakeCreatorArgs):
        if args.get('lookups_in_db', True):
            lookup_getter = args.get_or_choice_from_db
        else:
            lookup_getter = args.get_or_create

        result = self.cls(
            phage_identifier = lookup_getter('phage_identifier', self.faker.phage_identifier()),
            host = lookup_getter('host', self.faker.bacterial_species()),
            sample_date = args.get('sample_date', self.faker.date_object()),
            freezer = args.get('freezer', self.faker.random_int()),
            drawer = args.get('draw', self.faker.random_int()),
            position = args.get('position', self.faker.random_letter()),
            description = args.get('description', self.faker.sentence()),
            project = lookup_getter('project', self.faker.project()),
            box_number = lookup_getter('box_number', self.faker.box_number()),
            storage_method = lookup_getter('storage_method', self.faker.storage_method()),
            staff_member = lookup_getter('staff_member', self.faker.staff_member()),
            notes = args.get('notes', self.faker.paragraph()),
            name = args.get('name', f"Bacterium: {self.faker.pystr()}"),
        )

        return result


class SpecimenFakeCreator(FakeCreator):
    cls = Specimen

    def _create_item(self, save: bool, args: FakeCreatorArgs):
        if choice([True, False]):
            return self.faker.bacterium()._create_item(save, args)
        else:
            return self.faker.phage()._create_item(save, args)


class UploadFakeCreator(FakeCreator):
    cls = Upload

    def _create_item(self, save: bool, args: FakeCreatorArgs):
        return self.cls(
            filename = args.get('filename', self.faker.unique.file_name(extension='xslx')),
            status = args.get('status', choice(Upload.STATUS_NAMES)),
            errors = args.get('errors', '\n'.join([self.faker.sentence() for _ in range(5)])),
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

        return {
            'bacterial_species': list(db.session.execute(select(BacterialSpecies).order_by(BacterialSpecies.id)).scalars()),
            'strain': list(db.session.execute(select(Strain).order_by(Strain.id)).scalars()),
            'medium': list(db.session.execute(select(Medium).order_by(Medium.id)).scalars()),
            'plasmid': list(db.session.execute(select(Plasmid).order_by(Plasmid.id)).scalars()),
            'resistance_marker': list(db.session.execute(select(ResistanceMarker).order_by(ResistanceMarker.id)).scalars()),
            'phage_identifier': list(db.session.execute(select(PhageIdentifier).order_by(PhageIdentifier.id)).scalars()),
            'project': list(db.session.execute(select(Project).order_by(Project.id)).scalars()),
            'box_number': list(db.session.execute(select(BoxNumber).order_by(BoxNumber.id)).scalars()),
            'storage_method': list(db.session.execute(select(StorageMethod).order_by(StorageMethod.id)).scalars()),
            'staff_member': list(db.session.execute(select(StaffMember).order_by(StaffMember.id)).scalars()),
        }

    @cache
    def bacterial_species(self):
        return LookupFakeCreator(self, BacterialSpecies)

    @cache
    def strain(self):
        return LookupFakeCreator(self, Strain)

    @cache
    def medium(self):
        return LookupFakeCreator(self, Medium)

    @cache
    def plasmid(self):
        return LookupFakeCreator(self, Plasmid)

    @cache
    def resistance_marker(self):
        return LookupFakeCreator(self, ResistanceMarker)

    @cache
    def phage_identifier(self):
        return LookupFakeCreator(self, PhageIdentifier)

    @cache
    def project(self):
        return LookupFakeCreator(self, Project)

    @cache
    def box_number(self):
        return LookupFakeCreator(self, BoxNumber)

    @cache
    def storage_method(self):
        return LookupFakeCreator(self, StorageMethod)

    @cache
    def staff_member(self):
        return LookupFakeCreator(self, StaffMember)


class SpecimenProvider(BaseProvider):
    @cache
    def bacterium(self):
        return BacteriumFakeCreator(self)

    @cache
    def phage(self):
        return PhageFakeCreator(self)

    @cache
    def specimen(self):
        return SpecimenFakeCreator(self)


class UploadProvider(BaseProvider):
    @cache
    def upload(self):
        return UploadFakeCreator(self)

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
