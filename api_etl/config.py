import os
import sys
import ConfigParser

class Config(object):

    def __init__(self):
        location = os.environ.get("DGU_ETL_CONFIG", None)
        if not location:
            print "DGU_ETL_CONFIG is not set. Unable to load configuration"
            sys.exit(0)

        self.config = ConfigParser.ConfigParser()
        try:
            self.config.readfp(open(location))
        except:
            print "Unable to load config defined in DGU_ETL_CONFIG"
            sys.exit(0)

    def database(self, option):
        return self.config.get('database', option)

    def manifest(self, option):
        return self.config.get('manifest', option)