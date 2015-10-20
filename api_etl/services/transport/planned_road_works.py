import unicodecsv as csv
import os

import ckanapi
import requests
from lxml import etree

import api_etl.lib as lib
from api_etl.util import slugify_name

FIELD_NAMES = [
"reference_number", "road", "local_authority", "location",
"start_date", "end_date", "expected_delay", "description", "traffic_management",
"closure_type", "centre_easting", "centre_northing", "status", "published_date",
]

class PlannedRoadWorksExtractor(lib.Extractor):

    def extract(self, working_folder, service_manifest):
        """
        Extracts the XML from the dataset ID and then converts them all
        to a single CSV file for import.
        """
        wf = os.path.join(working_folder, service_manifest.name, "planned_road_works")
        if not os.path.exists(wf):
            os.makedirs(wf)

        csv_out_path = os.path.join(wf, "output.csv")
        csv_file = open(csv_out_path, "wb")
        writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
        writer.writeheader()

        print "  Fetching resources from {}".format(service_manifest.dataset)
        ckan = ckanapi.RemoteCKAN('http://data.gov.uk',
            user_agent='dgu_api_etl/0.1 (+http://data.gov.uk)',
            get_only=True)
        count = 0
        package = ckan.action.package_show(id=service_manifest.dataset)
        for resource in package['resources']:
            target = os.path.join(wf, resource['url'].split('/')[-1])

            # TODO: Remove this ...
            if os.environ.get('DEV') and os.path.exists(target):
                print "  Skipping file during dev"
            else:
                try:
                    r = requests.get(resource['url'].strip(), stream=True)
                    with open(target, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=4096):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                except:
                    print "    FAILED to process: {}".format(resource['url'])
                    continue

            #print "    Processing XML for {}".format(target)
            try:
                gen = self._file_dict_generator(target)
                for d in gen:
                    count += 1
                    writer.writerow(d)
            except:
                print "DODGY XML FILE: {}".format(target)
                continue

        print "TOTAL: {}".format(count)
        csv_file.close()
        return csv_out_path


    def _node_to_dict(self, node):
        d = {}
        for n in node:
            d[n.tag] = n.text
        return d

    def _file_dict_generator(self, target):
        global TOTES
        root = etree.parse(target).getroot()
        for node in root:
            d = self._node_to_dict(node)
            yield d

class PlannedRoadWorksTransformer(lib.Transformer):

    def transform_row(self, row_in):
        return row_in

    def new_header_rows(self, headers):
        return headers


class PlannedRoadWordsLoader(lib.loader.PostgresLoader):

    def create_table(self, service_manifest, input_file):
        print "  Creating table {} in DB {}".format(service_manifest.name, self.database_name)
        reader = csv.reader(open(input_file))
        q = self._create_sql(service_manifest, reader.next())

        cur = self.conn.cursor()
        cur.execute(q)
        self.conn.commit()
        cur.close()

    def _create_sql(self, service_manifest, headers):
        # TODO: We should here check the schema for required fields so can can NOT NULL
        # the relevant columns - making sure to slugify them first ...
        columns = []

        pkname = self._get_pk_name(service_manifest)

        table_settings = service_manifest.table_settings
        indices = [i.strip() for i in table_settings['index'].split(',')]
        print "  Indices are {}".format(indices)

        for h in headers:
            if pkname and pkname == h:
                columns.append("{} TEXT primary key".format(h))
            else:
                if h in [u'end_date', u'published_date', u'start_date']:
                    columns.append("{} TIMESTAMP".format(h))
                else:
                    columns.append("{} TEXT".format(h))

        q = """
            CREATE TABLE {}({});\n
        """.strip().format(service_manifest.name, ",\n".join(columns))
        idx = []
        for i in indices:
            s = "CREATE INDEX ON {} ((lower({})));".format(service_manifest.name, i)
            idx.append(s)

        idx = ";\n".join(idx)

        grant_q = "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {};".format(self.config.database('reader_username'))

        return q + idx + grant_q






