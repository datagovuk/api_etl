
import codepoint as cp

def entrypoints():
    """ Returns a list of ETL objects for various entries underneath
    the health services module """
    return [{
        'name': 'codepoint',
        'extractor': cp.CodepointExtractor,
        'transformer': cp.CodepointTransformer,
        'loader': cp.CodepointLoader,
    }]


