import api_etl.lib.extractor as e
import api_etl.lib.loader as l
#import companies


def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    this theme """
    return [
        # add entrypoints for each service here
        #{'name': 'companies-basic',
        # 'extractor': e.CKANExtractor,
        # 'transformer': companies.CompaniesBasicTransformer,
        # 'loader': l.PostgresLoader,},
    ]
