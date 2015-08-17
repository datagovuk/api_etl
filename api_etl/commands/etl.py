import cmd
import os
import sys

import api_etl.lib.services as svcs
from api_etl.lib.manifest import Manifest

class DbCommand(cmd.Cmd):

    def do_once(self, args):
        """ Creates the necessary roles, a super user and a reader account """
        accs = [
            "createuser -s ckan",
            "createuser -s -D -R -P -l reader",
        ]
        print ';\n'.join(accs) + ";"

    def do_init(self, args):
        """ Create the database for the '''args''' theme """
        cmds = [
            'createdb {db} -O {owner} -E utf-8'.format(db=args, owner="ckan"),
            'psql {db} -c "GRANT CONNECT ON DATABASE {db} TO {role}"',
            'psql {db} -c "GRANT USAGE ON SCHEMA public TO {role}"',
            'psql {db} -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}"',
            'psql {db} -c "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}"',
            'psql {db} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {role}"',
            'psql {db} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO {role}"',
            'psql {db} -c "REVOKE CREATE ON SCHEMA public FROM public"'
        ]
        print ';\n'.join(cmds).format(db=args,ro="ckan_reader", role='bob') + ";"


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

        entry = zip(services, service_entries)
        for e in entry:
            ep, sm = e
            self.run_etl(ep, sm)

    def print_separator(self, c='*'):
        print c * 60


    def run_etl(self, entry_points, service_manifest):
        """ Runs ETL by finding the manifest for each service based on the name"""
        self.print_separator('=')
        print "Running ETL with {} service".format(service_manifest.name)
        self.print_separator('=')

        extractor = entry_points['extractor']()
        print "\nExtracting data"
        self.print_separator()


        transformer = entry_points['transformer']()
        print "\nTransforming data"
        self.print_separator()


        loader = entry_points['loader']()
        print "\nLoading data"
        self.print_separator()


def main():
    commands = {
        'service': ServiceCommand,
        'database': DbCommand
    }

    args = sys.argv[1:]
    if not args:
        print >> sys.stderr, "Argument are required"
        sys.exit(1)

    command = args.pop(0)
    subcommand = args.pop(0) if args else ''

    if not command in commands:
        print >> sys.stderr, "Unknown command"
        sys.exit(1)

    c = commands.get(command)()
    c.onecmd("{} {}".format(subcommand, ' '.join(args)))