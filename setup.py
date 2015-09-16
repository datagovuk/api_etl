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
        'nose',
        'pyyaml==3.11',
        'ckanapi==3.5',
        'requests==2.7',
        'unicodecsv==0.13.0',
        'chardet==2.3.0',
        'psycopg2==2.6.1',
        'lxml==3.4.4'
    ],
    'packages': ['api_etl'],
    'scripts': [],
    'name': 'api_etl',
    'entry_points': {
        'console_scripts': [
            'etl=api_etl.commands.etl:main',
        ],
        'services': [
            'health = api_etl.services.health:entrypoints',
            'transport = api_etl.services.transport:entrypoints',
            'companies = api_etl.services.companies:entrypoints',
        ]
    }
}

setup(**config)
