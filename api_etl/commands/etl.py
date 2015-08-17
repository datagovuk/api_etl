import cmd
import os
import sys

import api_etl.lib.services as svcs
from api_etl.lib.manifest import Manifest

class NullCommand(cmd.Cmd):
    def default(self, *args):
        print >> sys.stderr, "Unknown command"

class ServiceCommand(cmd.Cmd):

    def do_run(self, args):
        parts = args.split('.')
        services = []
        service_entries = []

        manifest_filename = "{}.yml".format(parts[0])
        manifest = Manifest(manifest_filename)

        if len(parts) == 1:
            services = svcs.service(parts[0])
            service_entries = manifest.get_services()
        else:
            services = [svcs.named_subservice(*parts)]
            service_entries = [manifest.get_service(parts[1])]

        for s in service_entries:
            self.run_etl(s)

    def run_etl(self, service):
        """ Runs ETL by finding the manifest for each service based on the name"""
        print "Running ETL with {} service".format(service.name)




def main():
    commands = {
        'service': ServiceCommand
    }

    args = sys.argv[1:]
    command = args.pop(0)
    subcommand = args.pop(0) if args else ''

    c = commands.get(command, NullCommand)()
    c.onecmd("{} {}".format(subcommand, ' '.join(args)))