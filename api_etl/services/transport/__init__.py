
import planned_road_works as r
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
    }]


