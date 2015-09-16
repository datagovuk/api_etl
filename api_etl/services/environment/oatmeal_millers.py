import re

import ckanapi

import api_etl.lib as lib

FIELD_NAMES = [
    'year',
    'quarter',
    'oats_milled',
    'oat_flakes_and_rolled_oats',
    'oat_flour_and_other_cuts',
    'closing_stocks',
]

class OatmealMillersExtractor(lib.extractor.CKANExtractor):

    def extract(self, working_folder, service_manifest):
        """
        Extracts the XML from the dataset ID and then converts them all
        to a single CSV file for import.
        """
        input_file_path = super(OatmealMillersExtractor, self).extract(working_folder, service_manifest)
        output_file_path = re.sub(".csv$", ".final.csv", input_file_path)
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "wb") as output_file:
                lines = ["\t".join(FIELD_NAMES) + "\n"] + input_file.readlines()[2:]
                output_file.writelines(lines)

        return output_file_path

class OatmealMillersTransformer(lib.Transformer):

    def transform_row(self, row_in):
        return row_in

    def new_header_rows(self, headers):
        return FIELD_NAMES
