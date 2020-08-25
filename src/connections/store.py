import sqlalchemy
from . import utils
from .models import Base, Location, UnknownLocation
import logging

from typing import List

logger = logging.getLogger(__name__)


class LocationStore:
    def __init__(self, db_uri):

        self._db_uri = db_uri
        self._engine = sqlalchemy.create_engine(db_uri)
        self._check_connection()

        utils._initialize_tables(self._engine)

        Base.metadata.bind = self._engine
        SessionMaker = sqlalchemy.orm.sessionmaker(bind=self._engine)
        self.ManagedSessionMaker = utils._get_managed_session_maker(SessionMaker)

    def _check_connection(self) -> None:
        with self._engine.connect() as conn:
            statement = sqlalchemy.sql.text("SELECT version()")
            record = conn.execute(statement).fetchone()
            logger.info("Connected to %s" % record[0])
        return None

    def add_location(
        self, name: str, lon: float, lat: float, loc_type: str, loc_class: str
    ) -> None:
        """ Add location to db

        """
        with self.ManagedSessionMaker() as session:
            location = Location(
                name=name, lon=lon, lat=lat, loc_type=loc_type, loc_class=loc_class
            )
            session.add(location)

        if name in self.get_unknown_locations():
            self._remove_unknown_location(name)
        return None

    def get_location(self, name: str) -> "Location":
        """ Get location information

        :param str name: name of location to retrieve
        :return Location:
        """
        with self.ManagedSessionMaker() as session:
            location = session.query(Location).filter(Location.name == name).all()
            return location[0].to_entity()

    def get_locations(self) -> List[str]:
        """ Get names of all locations in db

        :return iterable(str): location names
        """
        with self.ManagedSessionMaker() as session:
            locations = session.query(Location.name).all()
            return [l[0] for l in locations]

    def delete_location(self, name: str) -> None:
        """ Remove location from db

        :param str location: name
        """
        with self.ManagedSessionMaker() as session:
            locations = session.query(Location).filter(Location.name == name)
            locations.delete()
        return None

    def add_unknown_location(self, name: str) -> None:
        """ Add location to db

        :param str location: name
        """
        with self.ManagedSessionMaker() as session:
            location = UnknownLocation(name=name)
            session.add(location)
        return None

    def get_unknown_locations(self) -> List[str]:
        """ Get names of all unknown locations in db

        :return iterable(str): location names
        """
        with self.ManagedSessionMaker() as session:
            locations = session.query(UnknownLocation.name).all()
            return [l[0] for l in locations]

    def _remove_unknown_location(self, name: str) -> None:
        """ Remove location from unknown list

        :param str name: name
        """
        with self.ManagedSessionMaker() as session:
            locations = session.query(UnknownLocation).filter(
                UnknownLocation.name == name
            )
            locations.delete()
        return None

    def get_filter_locations(self) -> List[str]:
        """

        """
        with self.ManagedSessionMaker() as session:
            locations = session.execute(
                """
                SELECT right_t.name
                FROM (
                    SELECT location_class, location_type
                    FROM (
                        SELECT location_class, location_type, Count(name) as count
                        FROM locations
                        GROUP BY location_class, location_type
                    ) AS grouped
                    WHERE (
                        count > 5 AND
                        location_type != 'continent' AND
                        location_class != 'highway'
                    ) OR (
                        location_class IN ('natural', 'waterway')
                    ) OR (
                        location_type IN ('sea', 'ocean', 'lighthouse')
                    )
                ) AS left_t
                LEFT OUTER JOIN (
                    SELECT * from locations
                ) AS right_t
                ON (
                    right_t.location_class = left_t.location_class AND
                    right_t.location_type = left_t.location_type
                )
                """
            )
            return [l[0] for l in locations]
