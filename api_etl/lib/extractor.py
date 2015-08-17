import os

import ckanapi
import requests

class Extractor(object):
    """ Provides base class for methods to be called when we
    want to extract data based on a manifest file """

    def extract(self, working_folder, service_manifest):
        """ Should return the full path to the newly downloaded content """
        pass


class CKANExtractor(Extractor):
    """ A generic CKAN extractor for retrieving data from
    CKAN """

    def extract(self, working_folder, service_manifest):
        wf = os.path.join(working_folder, service_manifest.name)
        if not os.path.exists(wf):
            os.mkdir(wf)

        print "  Extracting content to {}".format(wf)

        print "  Fetching resource ({}) metadata".format(service_manifest.resource)
        ckan = ckanapi.RemoteCKAN('http://data.gov.uk',
            user_agent='dgu_api_etl/0.1 (+http://data.gov.uk)')
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

        return target_file