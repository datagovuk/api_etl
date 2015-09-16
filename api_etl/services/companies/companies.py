import api_etl.lib as lib
from api_etl.util import slugify_name


class CompaniesBasicTransformer(lib.Transformer):

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
                row[self.header_map[k]] = v

        # TODO: Trim lat/lng down to more realistic resolution

        # Take a partial postcode so we can search for it ...
        if row['postcode']:
            row['partial_postcode'] = row['postcode'].split(' ')[0].strip()
        else:
            row['postcode'] = ''

        return row

    def new_header_rows(self, headers):
        """ When implemented in a subclass, returns the potentially modified header rows """
        for header in headers:
            self.header_map[header] = slugify_name(header)

        self.header_map['partial_postcode'] = 'partial_postcode'

        return self.header_map.values()

