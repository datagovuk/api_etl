from pkg_resources import iter_entry_points

#TODO: Is it themes & services or is it services & subservices?

def service_names():
    """
    Returns the name of all of the known services
    """
    return [ep.name for ep in iter_entry_points(group='services', name=None)]

def service(name):
    """
    Returns the list of ETL object dicts for the specified service
    """
    entry_point = list(iter_entry_points(group='services', name=name))
    if not entry_point:
        raise ImportError("Can't load the {} endpoints".format(name))
    endpoint_func = entry_point[0].load()
    return endpoint_func()

def named_subservice(service_name, subservice):
    """ Returns subservice entrypoints from a top level service, such as
    'health' and 'hospital' """
    eps = service(service_name)
    for ep in eps:
        if ep['name'] == subservice:
            return ep
    raise ImportError("Could not find service '{}' in theme '{}'".format(subservice, service_name))
