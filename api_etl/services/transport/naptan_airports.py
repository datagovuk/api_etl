import unicodecsv as csv
import api_etl.lib as lib


class AirportLoader(lib.loader.PostgresLoader):

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
                    naptan_airports
                VALUES (
                    %(AtcoCode)s,
                    %(IataCode)s,
                    %(Name)s
                );
             """

        new_rows = []
        for row in reader:
            if self._row_exists(row, pk, service_manifest.name):
                continue

            new_rows.append(row)

        cur = self.conn.cursor()

        cur.executemany(q, new_rows)

        self.conn.commit()

        cur.close()

        print "  Inserted {} rows into database".format(len(new_rows))

    def _create_sql(self, service_manifest):
        # TODO: We should here check the schema for required fields so can can
        # NOT NULL the relevant columns - making sure to slugify them first ...
        create = """CREATE TABLE naptan_airports (
            AtcoCode varchar(8) primary key,
            IataCode varchar(3),
            Name varchar
        );"""

        u = self.config.database('reader_username')
        grant = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(u)

        return create + grant
