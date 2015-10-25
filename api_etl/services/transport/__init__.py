
from api_etl.lib.extractor import CKANZipExtractor
from api_etl.lib import Transformer
import planned_road_works as r
import mot as m
import naptan_ferry_ports as nfp
import naptan_airports as nap
import api_etl.lib.extractor as e
import api_etl.lib.loader as l

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the transport services module """
    return [{
        'name': 'planned_road_works',
        'extractor': r.PlannedRoadWorksExtractor,
        'transformer': r.PlannedRoadWorksTransformer,
        'loader': r.PlannedRoadWordsLoader,
    },
    #{
    #    'name': 'anonymised_mot_test',
    #    'extractor': m.MOTExtractor,
    #    'transformer': m.MOTTransformer,
    #    'loader': m.MOTLoader,
    #},
    {
        'name': 'naptan_ferry_ports',
        'extractor': CKANZipExtractor,
        'transformer': Transformer,
        'loader': nfp.FerryLoader,
    },
    {
        'name': 'naptan_airports',
        'extractor': CKANZipExtractor,
        'transformer': Transformer,
        'loader': nap.AirportLoader,
    }]



