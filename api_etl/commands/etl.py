import cmd
import glob
import json
import os
import sys
import psycopg2
import api_etl.lib.services as svcs
from api_etl.lib.manifest import Manifest


class DbCommand(cmd.Cmd):

    def do_once(self, args):
        """ Creates the necessary roles, a super user and a reader account """
        accs = [
            "createuser -s ckan",
            "createuser -S -D -R -P -l reader",
        ]
        print ';\n'.join(accs) + ";"
        self.create_db("apiserver")

    def create_db(self, name):
        """ Create the database for the '''args''' theme """
        from api_etl import Config

        c = Config()
        owner = c.database('owner')
        role = c.database('reader_username')

        cmds = [
            'createdb {db} -O {owner} -E utf-8',
            'psql {db} -c "GRANT CONNECT ON DATABASE {db} TO {role}"',
            'psql {db} -c "GRANT USAGE ON SCHEMA public TO {role}"',
            'psql {db} -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}"',
            'psql {db} -c "GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}"',
            'psql {db} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {role}"',
            'psql {db} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO {role}"',
            'psql {db} -c "REVOKE CREATE ON SCHEMA public FROM public"'
        ]
        print ';\n'.join(cmds).format(db=name, role=role, owner=owner) + ";"


class ServiceCommand(cmd.Cmd):

    def do_run(self, args):
        from api_etl import Config

        self.config = Config()

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
            self.run_etl(parts[0], ep, sm)

    def print_separator(self, c='*'):
        print c * 60

    def run_etl(self, theme, entry_points, service_manifest):
        """ Runs ETL by finding the manifest for each service based on the name"""
        self.print_separator('=')
        print "Running ETL with {} service".format(service_manifest.name)
        self.print_separator('=')

        # Extract
        extractor = entry_points['extractor']()
        print "\nExtracting data"
        self.print_separator()
        extracted_filepath = extractor.extract(self.config.manifest('working_folder'), service_manifest)
        print "  Extracted content at {}".format(extracted_filepath)

        # Transform
        transformer = entry_points.get('transformer')
        if not transformer:
            print "No transformer"
            transformed_filepath = extracted_filepath
        else:
            print "\nTransforming data"
            self.print_separator()
            transformed_filepath = os.path.join(self.config.manifest('working_folder'),
                                                service_manifest.name,
                                                'transformed.out')
            count = transformer().transform(service_manifest, extracted_filepath, transformed_filepath)
            print "  Wrote {} rows to {}".format(count, transformed_filepath)

        # Load
        loader = entry_points['loader']
        if not loader:
            print "No loader"
        else:
            loader = loader()
            print "\nLoading data"
            self.print_separator()

            loader.init_connection("apiserver")
            if not loader.table_exists(service_manifest):
                loader.create_table(service_manifest, transformed_filepath)
            else:
                print "  Table already exists in DB"

            encoding = 'utf-8'
            if hasattr(transformer, 'encoding'):
                encoding = transformer.encoding

            loader.load_data(service_manifest, transformed_filepath, encoding)
            loader.close_connection()

    def load_data(self, service_manifest, source_file):
        pass


class UtilCommand(cmd.Cmd):

    def do_manifest_convert(self, args):
        from api_etl import Config
        self.config = Config()
        owner = self.config.database('owner')
        self.conn = psycopg2.connect("dbname=apiserver user={}".format(owner))

        self.lookup = {
            "character varying": "string",
            "text": "string"
        }

        root = self.config.config.get('manifest', 'location')
        for f in glob.glob(os.path.join(root, '*.yml')):
            m = Manifest(f)
            theme = m.data['title'].lower()

            for service in m.get_services():
                out = {
                    "theme": theme,
                    "id": service.name,
                    "title": service.description,
                    "tablename": service.name,
                }

                q = """
                  SELECT column_name, data_type
                  FROM information_schema.columns
                  WHERE table_schema = 'public'
                    AND table_name   = '{table}';
                """.format(table=service.name)

                cur = self.conn.cursor()
                cur.execute(q)
                result = cur.fetchall()
                cur.close()

                out['fields'] = []
                for (n,t) in result:
                    d = {"name": n, "type": self.lookup.get(t, t)}
                    out['fields'].append(d)

                if isinstance(service.table_settings, list):
                    settings = service.table_settings[0]
                else:
                    settings = service.table_settings
                out['choice_fields'] = settings.get('choice_fields', [])

                if hasattr(service, "searchables"):
                    out['queries'] = service.searchables

                outfile = os.path.join(root, "manifests", service.name + ".json")
                print outfile
                with open(outfile, "w") as fout:
                    json.dump(out, fout, indent=2)

        self.conn.close()

def main():
    commands = {
        'service': ServiceCommand,
        'database': DbCommand,
        'util': UtilCommand
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
