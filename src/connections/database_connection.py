import psycopg2
from typing import List, Tuple


class DatabaseConnection:
    def __init__(
        self, user="postgres", password="password", host="XX.XX.XXX.XX", port=5432
    ):
        _conn = self._connect(user, password, host, port)
        self.conn = _conn

        # init tables
        self._create_loc_table()

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

    def _create_loc_table(self) -> None:
        """ Create location and unknown locations db tables

        """
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS locations (
                name varchar,
                lon numeric,
                lat numeric
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
        self.conn.commit()
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
        cur = self.conn.cursor()
        with open(file, "r") as f:
            cur.copy_expert(sql=copy_sql, file=f)
        self.conn.commit()
        cur.close()

    def get_table_names(self) -> List[str]:
        """ Get tables in db

        :return iterable(str): table names
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_type='BASE TABLE'
            """
        )
        return cur.fetchall()

    def add_location(self, location: Tuple[str, float, float]) -> None:
        """ Add location to db

        :param iterable(str, numeric, numeric) location: (name, loc, lat)
        """
        sql = """
            INSERT INTO locations (name, lon, lat)
            VALUES(%s, %s, %s)
        """
        cur = self.conn.cursor()
        cur.execute(sql, location)
        self.conn.commit()
        cur.close()

    def get_locations(self) -> List[str]:
        """ Get names of all locations in db

        :return iterable(str): location names
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM locations
            """
        )
        return [l[0] for l in cur.fetchall()]

    def get_location(self, location: str) -> Tuple[str, float, float]:
        """ Get location information

        :param str location: location to retrieve
        :return tuple: (name, loc, lat)
        """
        cur = self.conn.cursor()
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
        cur = self.conn.cursor()
        cur.execute(sql, (location,))
        self.conn.commit()
        cur.close()

    def get_unknown_locations(self) -> List[str]:
        """ Get names of all unknown locations in db

        :return iterable(str): location names
        """
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT name
            FROM unknown_locations
            """
        )
        return [l[0] for l in cur.fetchall()]
