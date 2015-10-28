import os
import sys
import requests
from zipfile import ZipFile
import glob

import unicodecsv as csv
import api_etl.lib as lib


class CodepointExtractor(lib.Extractor):

    def extract(self, working_folder, service_manifest):
        data_folder = os.path.join(working_folder, "codepoint")
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        source = service_manifest.source_url
        target_file = os.path.join(data_folder, "codepoint.zip")

        if not os.environ.get('NOFETCH', False):
            print "Downloading source file"
            r = requests.get(source, stream=True)
            with open(target_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush()

            with ZipFile(target_file, 'r') as zf:
                print "Unzipping"
                zf.extractall(data_folder)

        return os.path.join(data_folder, "Data", "CSV")


class CodepointTransformer(lib.Transformer):

    def transform(self, service_manifest, input_folder, output_filename):
        files = glob.glob(os.path.join(input_folder, "*.csv"))
        count = 0

        if os.environ.get('NOFETCH', False) and os.path.exists(output_filename):
            return 0

        with open(output_filename, 'wb') as output_file:
            writer = csv.writer(output_file)

            headers = ["Postcode", "Quality", "Easting", "Northing", "Country",
                              "NHSRegion", "NHSHealthAuthority", "County", "District", "Ward"]
            writer.writerow(headers)

            for filename in files:
                with open(filename, 'r') as input_file:
                    reader = csv.reader(input_file)
                    for row in reader:
                        count += 1
                        writer.writerow(row)

        return count

class CodepointLoader(lib.loader.PostgresLoader):

    def create_table(self, service_manifest, input_dir):
        print "  Creating table {} in DB {}".format(service_manifest.name,
                                                                        self.database_name)

        q = self._create_sql(service_manifest)
        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()

        pass

    def load_data(self, service_manifest, source_file, encoding):

        with open(source_file, 'r') as f:
            reader = csv.DictReader(f, encoding=encoding)
            insertq = self._insert_statement()

            row_count = 0
            new_rows = []
            for row in reader:
                sys.stdout.write(
                    "\r Prepping data row {0}".format(row_count + 1)
                )
                sys.stdout.flush()

                row_count += 1
                if self._row_exists(row, "Postcode", service_manifest.name):
                    continue

                # https://stackoverflow.com/questions/6117646/insert-into-and-string-concatenation-with-python
                row['Point'] = "POINT(%(Easting)s %(Northing)s)" % row
                new_rows.append(row)

                if len(new_rows) % 100 == 0:
                    print "Committing 100 rows"
                    cur = self.conn.cursor()
                    cur.executemany( insertq, new_rows)

                    q = u"""UPDATE
                                codepoint
                            SET
                                LatLong = ST_Transform(OSPoint, 4326) WHERE LatLong is NULL"""
                    cur.execute(q)
                    self.conn.commit()
                    cur.close()

                    new_rows = []

            if new_rows:
                cur = self.conn.cursor()
                cur.executemany( insertq, new_rows)

                q = u"""UPDATE
                            codepoint
                        SET
                            LatLong = ST_Transform(OSPoint, 4326) WHERE LatLong is NULL"""
                cur.execute(q)
                self.conn.commit()
                cur.close()


    def _insert_statement(self):
        return """
            INSERT INTO
                    codepoint (Postcode, OSPoint, District, Ward)

                VALUES (
                    %(Postcode)s,
                    ST_GeomFromText(%(Point)s,  27700),
                    %(District)s,
                    %(Ward)s
                );
        """


    def _create_sql(self, service_manifest):
        enable_postgis = "CREATE EXTENSION IF NOT EXISTS postgis;"

        f = """create function normalise_postcode(pc varchar) returns varchar as $$
                        SELECT upper(replace(pc, ' ', ''));
                 $$ LANGUAGE SQL;"""

        create = """CREATE TABLE codepoint (
            Postcode varchar(12) primary key,
            OSPoint geometry(POINT, 27700),
            LatLong geography(POINT, 4326),
            District varchar(64),
            Ward varchar(64)
        );"""

        u = self.config.database('reader_username')
        idx = "CREATE INDEX ON codepoint  ((lower(Postcode)));"
        grant = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(u)
        return enable_postgis + create + idx + grant;
