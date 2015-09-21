import unicodecsv as csv
import os
from chardet.universaldetector import UniversalDetector
import gzip
import re


import ckanapi
import requests

import api_etl.lib as lib
from api_etl.util import slugify_name

FIELD_NAMES = [
   "TESTID", "VEHICLEID", "TESTDATE",
    "TESTCLASSID", "TESTTYPE", "TESTRESULT",
    "TESTMILEAGE", "POSTCODEREGION", "MAKE",
    "MODEL",  "COLOUR",  "FUELTYPE",
    "CYLCPCTY",  "FIRSTUSEDATE"
]

class MOTExtractor(lib.Extractor):

    def extract(self, working_folder, service_manifest):
        wf = os.path.join(working_folder, service_manifest.name, "mot")
        if not os.path.exists(wf):
            os.makedirs(wf)

        #ckan = ckanapi.RemoteCKAN('https://data.gov.uk',
        #    user_agent='dgu_api_etl/0.1 (+http://data.gov.uk)')
        #package = ckan.action.package_show(id=service_manifest.dataset)

        package = requests.get("https://data.gov.uk/api/3/action/package_show?id=" + service_manifest.dataset).json()
        required_resources = []
        for resource in package['result']['resources']:
            if "testing data results" in resource["description"]:
                required_resources.append(resource)

        for resource in required_resources:
            target_file = os.path.join(wf, resource['url'].split('/')[-1])
            self.download_file(resource['url'], target_file)
            break

        return wf

    def download_file(self, url, target):
        # TODO: Remove this ...
        print "Writing to target {}".format(target)
        print target[:-3]
        if os.environ.get('DEV') and (os.path.exists(target) or os.path.exists(target[:-3])) :
            print "  Skipping file during dev"
        else:
            r = requests.get(url, stream=True)
            with open(target, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush()

class MOTTransformer(lib.Transformer):

    def __init__(self):
        pass

    def transform(self, service_manifest, input_dir, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        row_count = 0
        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                opener = open
            elif filename.endswith('.txt.gz'):
                opener = gzip.open
            else:
                continue

            output_filename = os.path.join(output_dir, filename)
            filename = os.path.join(input_dir, filename)

            if os.environ.get('DEV') and os.path.exists(output_filename):
                print " ... skipping in DEV mode"
                return output_dir

            detector = UniversalDetector()
            with opener(filename) as input_file:
                for line in input_file.readlines():
                    detector.feed(line)
                    if detector.done:
                        break
                    detector.close()
            self.encoding = detector.result.get('encoding', 'windows-1252')
            print "  .... {}".format(self.encoding)

            headers = FIELD_NAMES

            with opener(filename) as input_file:
                reader = csv.reader(input_file,encoding=self.encoding, delimiter="|")

                print "  Transforming data ..."
                with open(output_filename, 'wb') as output_file:
                    writer = csv.writer(output_file)
                    writer.writerow(headers)

                    for row in reader:
                        new_row = self.transform_row(row)
                        if new_row:
                            writer.writerow(new_row)
                            row_count += 1

        return row_count


    def transform_row(self, row_in):
        if row_in[-1] == 'NULL':
            row_in = '';
        return row_in

    def new_header_rows(self, headers):
        return FIELD_NAMES

class MOTLoader(lib.loader.PostgresLoader):

    def create_table(self, service_manifest, input_dir):
        print "  Creating table {} in DB {}".format(service_manifest.name, self.database_name)

        q = self._create_sql(service_manifest)

        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def load_data(self, service_manifest, source_dir, encoding):

        inserted = 0
        for f in os.listdir(source_dir):
            source_file = os.path.join(source_dir, f)

            pk = service_manifest.table_settings["pk_name"].upper()

            print "  Loading data into table {}".format(service_manifest.name)
            reader = csv.DictReader(open(source_file), encoding=encoding)
            for row in reader:
                if not self._row_exists(row, pk, service_manifest.name):
                    self._insert_row(service_manifest.name, row)
                    inserted += 1

                if inserted % 100 == 0:
                    self.conn.commit()

            if inserted:
                self.conn.commit()

        print "  Inserted {} rows into database".format(inserted)


    def _create_sql(self, service_manifest):
        # TODO: We should here check the schema for required fields so can can NOT NULL
        # the relevant columns - making sure to slugify them first ...

        create = """CREATE TABLE anonymised_mot_test (
            testid integer primary key,
            vehicleid integer,
            testdate timestamp,
            testclassid text,
            testtype text,
            testresult text,
            testmileage integer,
            postcoderegion text,
            make text,
            model text,
            colour text,
            fueltype text,
            cylcpcty integer,
            firstusedate timestamp
        );"""


        grant_q = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(self.config.database('reader_username'))

        return create + grant_q




