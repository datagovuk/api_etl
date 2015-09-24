
import hospitals as h
import api_etl.lib.extractor as e
import api_etl.lib.loader as l

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the health services module """
    return [{
        'name': 'hospitals',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer,
        'loader': l.PostgresLoader,
    },
    {
        'name': 'clinics',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'gp_surgeries',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'social_care_locations',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'pharmacies',
        'extractor': e.CKANExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'dental_practices',
        'extractor': e.CKANExtractor,
        'transformer': h.DentistTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    }]


