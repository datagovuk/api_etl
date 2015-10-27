
import planned_road_works as r
import mot as m
import naptan_ferry_ports as nfp
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
        'extractor': nfp.FerryExtractor,
        'transformer': nfp.FerryTransformer,
        'loader': nfp.FerryLoader,
    }]



