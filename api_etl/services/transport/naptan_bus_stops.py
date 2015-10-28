import unicodecsv as csv
import api_etl.lib as lib

class BusLoader(lib.loader.PostgresLoader):

    def create_table(self, service_manifest, input_dir):
        print "  Creating table {} in DB {}".format(service_manifest.name,
                                                    self.database_name)

        q = self._create_sql(service_manifest)

        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def load_data(self, service_manifest, source_file, encoding):

        pk = service_manifest.table_settings["pk_name"]

        print "  Loading data into table {}".format(service_manifest.name)
        reader = csv.DictReader(open(source_file), encoding=encoding)

        q = u"""INSERT INTO
                    naptan_bus_stops
                VALUES (
                    %(AtcoCode)s,
                    %(NaptanCode)s,
                    %(CommonName)s,
                    ST_GeomFromText(%(Point)s,  27700)
                );
             """
        cur = self.conn.cursor()

        new_rows = []
        for row in reader:
            if self._row_exists(row, pk, service_manifest.name):
                continue

            # https://stackoverflow.com/questions/6117646/insert-into-and-string-concatenation-with-python
            row['Point'] = "POINT(%(Easting)s %(Northing)s)" % row
            new_rows.append(row)

            if len(new_rows) == 1000:
                cur.executemany(q, new_rows)
                new_rows = []

        cur.executemany(q, new_rows)

        q = u"""UPDATE
                    naptan_bus_stops
                SET
                    LatLong = ST_Transform(OSPoint, 4326);"""
        cur.execute(q)

        self.conn.commit()

        cur.close()

        print "  Inserted {} rows into database".format(len(new_rows))

    def _create_sql(self, service_manifest):
        # TODO: We should here check the schema for required fields so can can
        # NOT NULL the relevant columns - making sure to slugify them first ...
        enable_postgis = "CREATE EXTENSION IF NOT EXISTS postgis;"

        create = """CREATE TABLE naptan_bus_stops (
            AtcoCode varchar(12) primary key,
            NaptanCode varchar(10),
            CommonName varchar,
            OSPoint geometry(POINT, 27700),
            LatLong geography(POINT, 4326)
        );"""

        u = self.config.database('reader_username')
        grant = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(u)

        return enable_postgis + create + grant
