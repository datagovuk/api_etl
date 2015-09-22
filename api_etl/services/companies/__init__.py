import api_etl.lib.extractor as e
import api_etl.lib.loader as l
import companies


def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    this theme """
    return [{
        'name': 'companies-basic',
        'extractor': e.CKANZipExtractor,
        'transformer': companies.CompaniesBasicTransformer,
        'loader': l.PostgresLoader,
    },
    ]
