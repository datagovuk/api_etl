
import hospitals as h
import api_etl.lib.extractor as e
import api_etl.lib.loader as l

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the health services module """
    return [{
        'name': 'hospitals',
        'extractor': h.HSCICExtractor,
        'transformer': h.HospitalTransformer,
        'loader': l.PostgresLoader,
    },
    {
        'name': 'clinics',
        'extractor': h.HSCICExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'gp_surgeries',
        'extractor': h.HSCICExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'social_care_locations',
        'extractor': h.HSCICExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'pharmacies',
        'extractor': h.HSCICExtractor,
        'transformer': h.HospitalTransformer, # Use same transformer as hospitals
        'loader': l.PostgresLoader,
    },
    {
        'name': 'dental_practices',
        'extractor': e.CKANExtractor,
        'transformer': h.DentistTransformer,
        'loader': l.PostgresLoader,
    }]


