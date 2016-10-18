import os
import zipfile

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
        ckan = ckanapi.RemoteCKAN('https://data.gov.uk',
            user_agent='dgu_api_etl/0.1 (+https://data.gov.uk)')
        resource = ckan.action.resource_show(id=service_manifest.resource, requests_kwargs={'verify': False})

        target_file = os.path.join(wf, service_manifest.name + "." + resource['format'].lower())

        # TODO: Remove this ...
        if os.environ.get('DEV') and os.path.exists(target_file):
            print "  Skipping file during dev"
        else:
            r = requests.get(resource['url'], stream=True, verify=False)
            with open(target_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush()

        return target_file


class CKANZipExtractor(CKANExtractor):
    """ Retrieves data from CKAN and unzips it """

    def extract(self, working_folder, service_manifest):
        zipped_file = CKANExtractor.extract(self, working_folder, service_manifest)

        target_path = zipped_file.replace('.zip', '')
        if target_path == zipped_file:
            target_path = zipped_file + '.unzipped'

        # TODO: Remove this ...
        if os.environ.get('DEV') and os.path.exists(target_path) \
                and os.listdir(target_path):
            print "  Skipping unzip during dev"
        else:
            print "  Unzipping..."
            self.unzip(zipped_file, target_path)
            print "  ...unzipped"

        files = os.listdir(target_path)
        if len(files) == 1:
            return os.path.join(target_path, files[0])
        elif len(files) == 0:
            raise Exception('No files in the zip')
        else:
            try:
                if service_manifest.filename_in_zip not in files:
                    raise Exception('Cannot find filename %r in zipped files %r' %
                                    (service_manifest.filename_in_zip, files))
            except AttributeError:
                raise Exception(
                    'Multiple files in zip - specify which one '
                    'using filename_in_zip option in manifest. '
                    'Dir: %s Files: %s' %
                    (target_path, files))

            return os.path.join(target_path, service_manifest.filename_in_zip)

    def unzip(self, source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            for member in zf.infolist():
                # Path traversal defense copied from
                # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
                words = member.filename.split('/')
                path = dest_dir
                for word in words[:-1]:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if word in (os.curdir, os.pardir, ''): continue
                    path = os.path.join(path, word)
                zf.extract(member, path)
