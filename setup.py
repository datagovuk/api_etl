try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ETL scripts for api.data.gov.uk',
    'author': 'Ross Jones',
    'url': 'https://github.com/datagovuk/api_etl',
    'download_url': 'https://github.com/datagovuk/api_etl',
    'author_email': 'ross@servercode.co.uk',
    'version': '0.1',
    'install_requires': [
        'nose'
    ],
    'packages': ['api_etl'],
    'scripts': [],
    'name': 'api_etl',
    'entry_points': {
        'services': [
            'health = api_etl.services.health:entrypoints',
        ]
    }
}

setup(**config)