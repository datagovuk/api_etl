import os

import yaml

# Make this configurable
MANIFEST_ROOT = "./manifests/"

class ManifestService(object):

    def __init__(self, data):
        self.data = data
        for k, v in self.data.iteritems():
            setattr(self, k, v)


class Manifest(object):

    def __init__(self, path):
        self.path = path
        self.load()

    def load(self):
        filepath = os.path.join(MANIFEST_ROOT, self.path)
        self.data = yaml.load(open(filepath).read())

    def get_service(self, name):
        services_by_name = dict((d['name'], d) for d in self.data['services'])
        try:
            service_data = services_by_name[name]
        except KeyError:
            raise Exception("Cannot find service {} in {}".format(name, services_by_name.keys()))
        return ManifestService(service_data)

    def get_services(self):
        return [ManifestService(s) for s in self.data['services']]


