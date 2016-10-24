# coding=utf-8
import unicodecsv as csv
import chardet
import sys

SEPARATORS = {
    'tab'  : '\t',
    'comma': ',',
    'pipe' : '|',
    ''     : ',',
}

CHARDET_SAMPLE_SIZE = 1000*1024  # do chardet on the first few KB of the file


class Transformer(object):

    def transform(self, service_manifest, input_filename, output_filename):

        # Encoding
        if hasattr(service_manifest, 'encoding'):
            self.encoding = service_manifest.encoding
        else:
            print "  Determining encoding ..."
            encoding_check = chardet.detect(open(input_filename).read(CHARDET_SAMPLE_SIZE))
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

                row_pos = 0

                try:
                    for row in reader:
                        # Progress bar
                        sys.stdout.write(
                            "\rTransforming data row {0}".format(row_count + 1)
                        )
                        sys.stdout.flush()

                        new_row = self.transform_row(row)

                        if new_row:
                            writer.writerow(new_row)
                            row_count += 1
                        # this_row records the current row, so if there is an
                        # exception during the "for" step, we know it wasn't
                        # the row before that caused it (the value of row)
                        row_pos += 1
                except Exception, e:
                    print 'Exception occurred processing data row %s in %s' % \
                        (row_pos + 1, input_filename)

        return row_count

    def new_header_rows(self, headers):
        """ When implemented in a subclass, returns the potentially modified header rows """
        return headers

    def transform_row(self, row_in):
        """ To be implemented by subclass. It is expected that given
            a row (dict), it will return a new row (dict)"""
        return row_in

