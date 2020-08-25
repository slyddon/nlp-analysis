import logging
from typing import List, Tuple

import psycopg2

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(
        self, user="postgres", password="password", host="XX.XX.XXX.XX", port=5432
    ):
        self._conn = self._connect(user, password, host, port)
        self._check_connection()
        # init tables
        self._create_tables()

    @staticmethod
    def _connect(
        user: str, password: str, host: str, port: int
    ) -> psycopg2.extensions.connection:
        """ Connect to postgres instance

        :param str user: DB user
        :param str password: DB password
        :param str host: DB host - if using docker this is the name of the service
        :param int port: DB port
        :return psycopg2.extensions.connection: DB connection instance
        """
        conn = psycopg2.connect(host=host, port=port, user=user, password=password)
        return conn

    def _check_connection(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute("""SELECT version()""")
            record = cur.fetchone()
            logger.info("Connected to %s" % record)
        return None

    def _create_tables(self) -> None:
        """ Create location and unknown locations db tables

        """
        logger.debug("Creating tables")
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                name varchar,
                lon numeric,
                lat numeric,
                class varchar,
                type varchar
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS unknown_locations (
                name varchar
            )
            """
        )
        self._conn.commit()
        cur.close()

    def copy_from_csv(self, file: str, table: str) -> None:
        """ Insert data from pre-existing csv file

        :param str file: csv to copy from
        :param str table: table to copy to
        """
        copy_sql = f"""
           COPY {table}
           FROM stdin WITH CSV HEADER
           DELIMITER as ','
           """
        cur = self._conn.cursor()
        with open(file, "r") as f:
            cur.copy_expert(sql=copy_sql, file=f)
        self._conn.commit()
        cur.close()

    def get_table_names(self) -> List[str]:
        """ Get tables in db

        :return iterable(str): table names
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE'
            """
        )
        return cur.fetchall()

    def add_location(self, location: Tuple[str, float, float, str, str]) -> None:
        """ Add location to db

        :param iterable(str, numeric, numeric, str, str) location: (name, lon, lat, class, type)
        """
        sql = """
            INSERT INTO locations (name, lon, lat, class, type)
            VALUES(%s, %s, %s, %s, %s)
        """
        cur = self._conn.cursor()
        cur.execute(sql, location)
        self._conn.commit()
        cur.close()

        if location[0] in self.get_unknown_locations():
            self._remove_unknown_location(location[0])

    def get_locations(self) -> List[str]:
        """ Get names of all locations in db

        :return iterable(str): location names
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM locations
            """
        )
        return [l[0] for l in cur.fetchall()]

    def get_location(self, location: str) -> Tuple[str, float, float, str, str]:
        """ Get location information

        :param str location: location to retrieve
        :return tuple: (name, loc, lat, class, type)
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM locations
            WHERE name = %s
            """,
            (location,),
        )
        return cur.fetchone()

    def add_unknown_location(self, location: str) -> None:
        """ Add location to db

        :param str location: name
        """
        sql = """
            INSERT INTO unknown_locations (name)
            VALUES(%s)
        """
        cur = self._conn.cursor()
        cur.execute(sql, (location,))
        self._conn.commit()
        cur.close()

    def _remove_unknown_location(self, location: str) -> None:
        """ Remove location from unknown list

        :param str location: name
        """
        sql = """
            DELETE FROM unknown_locations WHERE
            name = %s
        """
        cur = self._conn.cursor()
        cur.execute(sql, (location,))
        self._conn.commit()
        cur.close()

    def get_unknown_locations(self) -> List[str]:
        """ Get names of all unknown locations in db

        :return iterable(str): location names
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM unknown_locations
            """
        )
        return [l[0] for l in cur.fetchall()]

    def get_filter_locations(self) -> List[str]:
        """ Get names of locations that appear sufficiently
            frequently and are not of an undesired type

        :return iterable(str): location names
        """
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT right_t.name
            FROM (
                SELECT class, type
                FROM (
                    SELECT class, type, Count(name) as count
                    FROM locations
                    GROUP BY class, type
                ) AS grouped
                WHERE (
                    count > 5 AND
                    type != 'continent' AND
                    class != 'highway'
                ) OR (
                    class IN ('natural', 'waterway')
                ) OR (
                    type IN ('sea', 'ocean', 'lighthouse')
                )
            ) AS left_t
            LEFT OUTER JOIN (
                SELECT * from locations
            ) AS right_t
            ON (right_t.class = left_t.class AND right_t.type = left_t.type)
            """
        )
        return [l[0] for l in cur.fetchall()]
