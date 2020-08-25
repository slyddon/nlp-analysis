from sqlalchemy import Column, Integer, String, Float, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, Sequence("location_id_seq"), primary_key=True)
    name = Column(String)
    lon = Column(Float)
    lat = Column(Float)
    location_class = Column(String)
    location_type = Column(String)

    def __repr__(self):
        return "<Location(name='%s')>" % self.name

    def to_entity(self):
        return Location(
            id=self.id,
            name=self.name,
            lon=self.lon,
            lat=self.lat,
            location_class=self.location_class,
            location_type=self.location_type,
        )


class UnknownLocation(Base):
    __tablename__ = "unknown_locations"

    id = Column(Integer, Sequence("unknown_location_id_seq"), primary_key=True)
    name = Column(String)

    def __repr__(self):
        return "<UnknownLocation(name='%s')>" % self.name

    def to_entity(self):
        return UnknownLocation(id=self.id, name=self.name)
