from nose.tools import *

import api_etl.lib as lib
import api_etl.lib.services as svcs

def test_service_list():
    assert svcs.service_names() == ['health'], svcs.service_names()

def test_get_service():
    ep = svcs.service('health')[0]
    _check_hospital_entrypoints(ep)

def test_get_subservice():
    ep = svcs.named_subservice('health', 'hospitals')
    _check_hospital_entrypoints(ep)

@raises(ImportError)
def test_get_subservice_fail_toplevel():
    ep = svcs.named_subservice('wombles', 'tobermory')

@raises(ImportError)
def test_get_subservice_fail_named():
    ep = svcs.named_subservice('health', 'tobermory')

def _check_hospital_entrypoints(ep):
    from api_etl.services.health import hospitals as h

    assert ep['name'] == 'hospitals', ep['name']
    assert isinstance(ep['transformer'](), h.HospitalTransformer)
    assert isinstance(ep['transformer'](), lib.Transformer)
    assert isinstance(ep['loader'](), h.HospitalLoader)
    assert isinstance(ep['loader'](), lib.Loader)
    assert isinstance(ep['extractor'](), h.HospitalExtractor)
    assert isinstance(ep['extractor'](), lib.Extractor)