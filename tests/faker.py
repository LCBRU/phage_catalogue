from random import choice
from faker.providers import BaseProvider
from sqlalchemy import select
from lbrc_flask.database import db

from phage_catalogue.model import BacterialSpecies, Bacterium, Medium, Phage, PhageIdentifier, Plasmid, Project, ResistanceMarker, StaffMember, StorageMethod, Strain, Upload


class LookupProvider(BaseProvider):
    def create_standard_lookups(self):
        for _ in range(5):
            self.get_bacterial_species_db()
            self.get_strain_db()
            self.get_medium_db()
            self.get_plasmid_db()
            self.get_resistance_marker_db()
            self.get_phage_identifier_db()
            self.get_project_db()
            self.get_storage_method_db()
            self.get_staff_member_db()
        
    def get_lookup(self, cls, **kwargs):

        result = cls(
            name=kwargs.get('name', self.generator.pystr(min_chars=1, max_chars=100))
        )

        return result

    def get_lookup_db(self, cls, **kwargs):
        x = self.get_lookup(cls, **kwargs)

        db.session.add(x)
        db.session.commit()

        return x

    def get_lookup_random(self, cls, **kwargs):
        return choice(list(db.session.execute(select(cls)).scalars()))

    def get_bacterial_species(self, **kwargs):
        return self.get_lookup(BacterialSpecies, **kwargs)

    def get_bacterial_species_db(self, **kwargs):
        return self.get_lookup_db(BacterialSpecies, **kwargs)

    def get_bacterial_species_random(self):
        return self.get_lookup_random(BacterialSpecies)

    def get_strain(self, **kwargs):
        return self.get_lookup(Strain, **kwargs)

    def get_strain_db(self, **kwargs):
        return self.get_lookup_db(Strain, **kwargs)

    def get_strain_random(self):
        return self.get_lookup_random(Strain)

    def get_medium(self, **kwargs):
        return self.get_lookup(Medium, **kwargs)

    def get_medium_db(self, **kwargs):
        return self.get_lookup_db(Medium, **kwargs)

    def get_medium_random(self):
        return self.get_lookup_random(Medium)

    def get_plasmid(self, **kwargs):
        return self.get_lookup(Plasmid, **kwargs)

    def get_plasmid_db(self, **kwargs):
        return self.get_lookup_db(Plasmid, **kwargs)

    def get_plasmid_random(self):
        return self.get_lookup_random(Plasmid)

    def get_resistance_marker(self, **kwargs):
        return self.get_lookup(ResistanceMarker, **kwargs)

    def get_resistance_marker_db(self, **kwargs):
        return self.get_lookup_db(ResistanceMarker, **kwargs)

    def get_resistance_marker_random(self):
        return self.get_lookup_random(ResistanceMarker)

    def get_phage_identifier(self, **kwargs):
        return self.get_lookup(PhageIdentifier, **kwargs)

    def get_phage_identifier_db(self, **kwargs):
        return self.get_lookup_db(PhageIdentifier, **kwargs)

    def get_phage_identifier_random(self):
        return self.get_lookup_random(PhageIdentifier)

    def get_project(self, **kwargs):
        return self.get_lookup(Project, **kwargs)

    def get_project_db(self, **kwargs):
        return self.get_lookup_db(Project, **kwargs)

    def get_project_random(self):
        return self.get_lookup_random(Project)

    def get_storage_method(self, **kwargs):
        return self.get_lookup(StorageMethod, **kwargs)

    def get_storage_method_db(self, **kwargs):
        return self.get_lookup_db(StorageMethod, **kwargs)

    def get_storage_method_random(self):
        return self.get_lookup_random(StorageMethod)

    def get_staff_member(self, **kwargs):
        return self.get_lookup(StaffMember, **kwargs)

    def get_staff_member_db(self, **kwargs):
        return self.get_lookup_db(StaffMember, **kwargs)
    
    def get_staff_member_random(self):
        return self.get_lookup_random(StaffMember)



class SpecimenProvider(BaseProvider):
    def get_bacterium(self, **kwargs):
        return Bacterium(
            species = kwargs.get('species', self.generator.get_bacterial_species_random()),
            strain = kwargs.get('strain', self.generator.get_strain_random()),
            medium = kwargs.get('medium', self.generator.get_medium_random()),
            plasmid = kwargs.get('plasmid', self.generator.get_plasmid_random()),
            resistance_marker = kwargs.get('resistance_marker', self.generator.get_resistance_marker_random()),
            sample_date = kwargs.get('sample_date', self.generator.date()),
            freezer = kwargs.get('freezer', self.generator.random_int()),
            draw = kwargs.get('draw', self.generator.random_int()),
            position = kwargs.get('position', self.generator.random_letter()),
            description = kwargs.get('description', self.generator.sentence()),
            project = kwargs.get('project', self.generator.get_project_random()),
            storage_method = kwargs.get('storage_method', self.generator.get_storage_method_random()),
            staff_member = kwargs.get('staff_member', self.generator.get_staff_member_random()),
            notes = kwargs.get('notes', self.generator.paragraph()),
        )

    def get_bacterium_db(self, **kwargs):
        x = self.get_bacterium(**kwargs)

        db.session.add(x)
        db.session.commit()

        return x

    def get_phage(self, **kwargs):
        return Phage(
            phage_identifier = kwargs.get('phage_identifier', self.generator.get_phage_identifier_random()),
            host = kwargs.get('host', self.generator.get_bacterial_species_random()),
            sample_date = kwargs.get('sample_date', self.generator.date()),
            freezer = kwargs.get('freezer', self.generator.random_int()),
            draw = kwargs.get('draw', self.generator.random_int()),
            position = kwargs.get('position', self.generator.random_letter()),
            description = kwargs.get('description', self.generator.sentence()),
            project = kwargs.get('project', self.generator.get_project_random()),
            storage_method = kwargs.get('storage_method', self.generator.get_storage_method_random()),
            staff_member = kwargs.get('staff_member', self.generator.get_staff_member_random()),
            notes = kwargs.get('notes', self.generator.paragraph()),
        )

    def get_phage_db(self, **kwargs):
        x = self.get_phage(**kwargs)

        db.session.add(x)
        db.session.commit()

        return x


    def get_specimen(self, **kwargs):
        if choice([True, False]):
            return self.get_phage()
        else:
            return self.get_bacterium()


    def get_specimen_db(self, **kwargs):
        if choice([True, False]):
            return self.get_phage_db()
        else:
            return self.get_bacterium_db()


class UploadProvider(BaseProvider):
    def get_upload(self, **kwargs):
        return Upload(
            filename = kwargs.get('filename', self.generator.file_name(extension='xslx')),
            status = kwargs.get('status', choice(Upload.STATUS_NAMES)),
            errors = kwargs.get('errors', [self.generator.sentence() for _ in range(5)]),
        )

    def get_upload_db(self, **kwargs):
        x = self.get_bacterium(**kwargs)

        db.session.add(x)
        db.session.commit()

        return x
