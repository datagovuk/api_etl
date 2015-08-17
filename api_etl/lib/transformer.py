# coding=utf-8
from api_etl.util import slugify_name

import unicodecsv as csv
import chardet

SEPARATORS = {
    'tab'  : '\t',
    'comma': ',',
    ''     : ',',
}

class Transformer(object):

    def transform(self, service_manifest, input_filename, output_filename):

        print "  Determining encoding ..."
        encoding_check = chardet.detect(open(input_filename).read())
        self.encoding = encoding_check.get('encoding', 'windows-1252')
        print "  .... {}".format(self.encoding)

        row_count = 0
        with open(input_filename) as input_file:
            reader = csv.DictReader(input_file, encoding=self.encoding, delimiter=SEPARATORS[service_manifest.separator])

            headers = [n for n in reader.fieldnames]
            # Ask the subclass to add any new headers it will add
            headers = self.new_header_rows(headers)

            print "  Transforming data ..."
            with open(output_filename, 'wb') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=headers)
                writer.writeheader()

                for row in reader:
                    new_row = self.transform_row(row)
                    if new_row:
                        writer.writerow(new_row)
                        row_count += 1
        return row_count

    def new_header_rows(self, headers):
        """ When implemented in a subclass, returns the potentially modified header rows """
        return headers

    def transform_row(self, row_in):
        """ To be implemented by subclass. It is expected that given
            a row (dict), it will return a new row (dict)"""
        pass

