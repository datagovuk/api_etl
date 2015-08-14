import cmd
import os
import sys

import api_etl.lib.services as svcs


class NullCommand(cmd.Cmd):
    def default(self, *args):
        print >> sys.stderr, "Unknown command"

class ServiceCommand(cmd.Cmd):

    def do_run(self, args):
        parts = args.split('.')
        services = None
        if len(parts) == 1:
            services = svcs.service(parts[0])
        else:
            services = [svcs.named_subservice(*parts)]

        self.run_etl(services)


    def run_etl(self, services):
        print "Running ETL with {} services".format(len(services))


def main():
    commands = {
        'service': ServiceCommand
    }

    args = sys.argv[1:]
    command = args.pop(0)
    subcommand = args.pop(0) if args else ''

    c = commands.get(command, NullCommand)()
    c.onecmd("{} {}".format(subcommand, ' '.join(args)))