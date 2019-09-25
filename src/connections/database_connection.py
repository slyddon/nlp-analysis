# Author: Sam Lyddon
# Date: 19/08/2019

import psycopg2


class DatabaseConnection:
    def __init__(
        self, user="postgres", password="password", host="XX.XX.XXX.XX", port=5432
    ):
        _conn = self._connect(user, password, host, port)
        self.conn = _conn

        # init tables
        self._create_loc_table()

    def _connect(self, user, password, host, port):
        """ Connect to postgres instance

        :param str user: DB user
        :param str password: DB password
        :param str host: DB host - if using docker this is the name of the service
        :param str port: DB port
        :return psycopg2.Connection: DB connection instance
        """
        conn = psycopg2.connect(host=host, port=port, user=user, password=password)
        return conn

    def _create_loc_table(self):
        """ Create location db table

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
        self.conn.commit()
        cur.close()

    def copy_from_csv(self, file, table):
        """ Insert data from pre-existing csv file

        :param str file: csv to copy from
        :param str table: table to copy to
        """
        copy_sql = """
           COPY locations 
           FROM stdin WITH CSV HEADER
           DELIMITER as ','
           """
        cur = self.conn.cursor()
        with open(file, "r") as f:
            cur.copy_expert(sql=copy_sql, file=f)
        self.conn.commit()
        cur.close()

    def get_table_names(self):
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

    def get_all_locations(self):
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

    def get_location(self, location):
        """ Get location information

        :param str location: location to retrieve
        :return tuple: (name, loc, lat)
        """
        cur = self.conn.cursor()
        cur.execute(
            f"""
            SELECT *
            FROM locations
            WHERE name = '{location}'
            """
        )
        return cur.fetchone()

    def add_location(self, location):
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
