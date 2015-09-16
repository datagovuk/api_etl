
import oatmeal_millers as r
import api_etl.lib.extractor as e
import api_etl.lib.loader as l

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the transport services module """
    return [{
        'name': 'oatmeal_millers',
        'extractor': r.OatmealMillersExtractor,
        'transformer': r.OatmealMillersTransformer,
        'loader': l.PostgresLoader,
    }]


