
import hospitals as h
import api_etl.lib.extractor as e

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the health services module """
    return [{
        'name': 'hospitals',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer,
        'loader': h.HospitalLoader,
    }]