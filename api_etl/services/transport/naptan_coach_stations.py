import unicodecsv as csv
import api_etl.lib as lib

class CoachLoader(lib.loader.PostgresLoader):

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
                    naptan_coach_stations
                VALUES (
                    %(AtcoCode)s,
                    %(NationalCoachCode)s,
                    %(Name)s,
                    ST_GeomFromText(%(Point)s,  27700)
                );
             """

        new_rows = []
        for row in reader:
            if self._row_exists(row, pk, service_manifest.name):
                continue

            # https://stackoverflow.com/questions/6117646/insert-into-and-string-concatenation-with-python
            row['Point'] = "POINT(%(Easting)s %(Northing)s)" % row
            new_rows.append(row)

        cur = self.conn.cursor()

        cur.executemany(q, new_rows)

        q = u"""UPDATE
                    naptan_coach_stations
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

        create = """CREATE TABLE naptan_coach_stations (
            AtcoCode varchar(12),
            NationalCoachCode varchar(10) primary key,
            Name varchar,
            OSPoint geometry(POINT, 27700),
            LatLong geography(POINT, 4326)
        );"""

        u = self.config.database('reader_username')
        grant = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(u)

        return enable_postgis + create + grant
