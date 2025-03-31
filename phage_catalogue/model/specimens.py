from datetime import date
from lbrc_flask.database import db
from lbrc_flask.security import AuditMixin
from lbrc_flask.model import CommonMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text
from phage_catalogue.model.lookups import Lookup


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

class BoxNumber(Lookup, db.Model):
    pass


class Specimen(AuditMixin, CommonMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20), index=True)

    __mapper_args__ = {
        "polymorphic_on": type,
    }

    freezer: Mapped[int] = mapped_column(index=True)
    drawer: Mapped[int] = mapped_column(index=True)
    position: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(Text, index=True)
    description: Mapped[str] = mapped_column(Text, index=True)
    notes: Mapped[str] = mapped_column(Text, index=True)
    sample_date: Mapped[date] = mapped_column(index=True)

    box_number_id: Mapped[int] = mapped_column(ForeignKey(BoxNumber.id), index=True, nullable=True)
    box_number: Mapped[BoxNumber] = relationship(foreign_keys=[box_number_id])
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

    # def data(self):
    #     return {
    #         "key": self.id,
    #         "freezer": self.freezer,
    #         "drawer": self.drawer,
    #         "position": self.position.upper(),
    #         "box_number": self.box_number.name,
    #         "name": self.name,
    #         "description": self.description,
    #         "notes": self.notes,
    #         "date": self.sample_date,
    #         "project": self.project.name,
    #         "storage method": self.storage_method.name,
    #         "staff member": self.staff_member.name,
    #     }


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
    
    # def data(self):
    #     result = super().data()

    #     result['bacterial species'] = self.species.name
    #     result['strain'] = self.strain.name
    #     result['media'] = self.medium.name
    #     result['plasmid name'] = self.plasmid.name
    #     result['resistance marker'] = self.resistance_marker.name

    #     return result


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

    # def data(self):
    #     result = super().data()

    #     result['phage id'] = self.phage_identifier.name
    #     result['host species'] = self.host.name

    #     return result
