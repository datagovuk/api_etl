import os
import ckanapi
import requests

import api_etl.lib as lib
from api_etl.util import slugify_name

class HSCICExtractor(lib.Transformer):

    def extract(self, working_folder, service_manifest):
        wf = os.path.join(working_folder, service_manifest.name)
        if not os.path.exists(wf):
            os.mkdir(wf)

        print "  Extracting content to {}".format(wf)

        print "  Fetching resource ({}) metadata".format(service_manifest.resource)
        ckan = ckanapi.RemoteCKAN('https://data.gov.uk',
            user_agent='dgu_api_etl/0.1 (+https://data.gov.uk)')
        resource = ckan.action.resource_show(id=service_manifest.resource)

        target_file = os.path.join(wf, service_manifest.name + "." + resource['format'].lower())

        # TODO: Remove this ...
        if os.environ.get('DEV') and os.path.exists(target_file):
            print "  Skipping file during dev"
        else:
            r = requests.get(resource['url'], stream=True)
            with open(target_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush()

        print "  Desquiggling file"
        from api_etl.tools.dedelimiter import convert_squiggle_to_tabs
        content = convert_squiggle_to_tabs(target_file)

        open(target_file, 'wb').write(content)

        return target_file



class HospitalTransformer(lib.Transformer):

    def __init__(self):
        self.first = True
        self.header_map = {}

    def transform_row(self, row_in):
        """ When provided with a row, it should return a new row """
        row = {}

        # Copy the existing data ...
        for k, v in row_in.iteritems():
            if k is None:
                print "*" * 30
                print "BAD DATA in source: {}".format(row_in)
                print "*" * 30
                return None

            row[self.header_map[k]] = v

        # TODO: Trim lat/lng down to more realistic resolution

        def find_postcode_key(r):
            for k in r:
                if k.lower() == 'postcode':
                    return k
            return ""

        # Take a partial postcode so we can search for it ...
        row['partial_postcode'] = ""
        postcode_key = find_postcode_key(row_in.keys())
        if postcode_key:
            if row_in[postcode_key]:
                row['partial_postcode'] = row_in[postcode_key].split(' ')[0].strip()

        return row

    def new_header_rows(self, headers):
        """ When implemented in a subclass, returns the potentially modified header rows """
        for header in headers:
            self.header_map[header] = slugify_name(header).lower()

        self.header_map['partial_postcode'] = 'partial_postcode'

        return self.header_map.values()

class DentistTransformer(lib.Transformer):

    def __init__(self):
        self.first = True
        self.header_map = {}

    def transform_row(self, row_in):
        """ When provided with a row, it should return a new row """
        row = {}

        # Copy the existing data ...
        for k, v in row_in.iteritems():
            if k is None:
                print "*" * 30
                print "BAD DATA in source: {}".format(row_in)
                print "*" * 30
                return None
            else:
                key = self.header_map.get(k, '')
                if key:
                    row[key] = v

        # TODO: Trim lat/lng down to more realistic resolution

        # Take a partial postcode so we can search for it ...
        if row['postcode']:
            row['partial_postcode'] = row['postcode'].split(' ')[0].strip()
        else:
            row['postcode'] = ''
            row['partial_postcode'] = ''

        return row

    def new_header_rows(self, headers):
        """ When implemented in a subclass, returns the potentially modified header rows """
        for header in headers:
            self.header_map[header] = header.lower().replace(' ', '_').replace('-', '_')
            if header.lower().startswith('col'):
                del self.header_map[header]
        self.header_map['partial_postcode'] = 'partial_postcode'

        return self.header_map.values()

