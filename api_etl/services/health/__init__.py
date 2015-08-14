
import hospitals as h

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the health services module """
    return [{
        'name': 'hospitals',
        'extractor': h.HospitalExtractor,
        'transformer': h.HospitalTransformer,
        'loader': h.HospitalLoader,
    }]