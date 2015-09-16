# ETL Tools for DGU API Server

This repository contains a collection of tools which will, based on a YAML manifest files:

* Create a database for a theme 
* Download the RAW data via data.gov.uk
* Transforms the data in some small ways (e.g. split postcode to store outward code separately)
* Create the necessary database and database tables, and grant read-only permission to the default user 

APIs are split into themes, and services, where each theme can have multiple services.  So for instance the ```health``` theme will have a ```hospitals``` service (and probably others).


## Installation

Requirements:

* Python 2.7+
* Postgres > v9.0
* build-essential (for Ubuntu)
* Postgres-dev (for psycopg2)
* virtualenv (python-virtualenv on Ubuntu)

Installing ...

1. Create a virtualenv, and activate it 
2. ```git clone git@github.com:datagovuk/api_etl.git```
3. ```python setup.py develop```
4. Make a directory somewhere to store manifests
5. Make a directory somewhere to store downloads


## Configuration

### First task 

Before setting the configuration file, the following command should be run to obtain the command line required to set up the accounts.  You will be prompted for the password for each user, which will be used in the configuration file later.

```
etl database once 
```
Now copy and paste the commands into the command-line

### Configuration file 

Copy the sample.ini file and change the settings to reflect your setup.  Once the new .ini file is complete, the full path to the file should be set as an environment variable:

```
mkdir /etc/dgu_etl
cp dgu_etl/sample.ini /etc/dgu_etl/config.ini
export DGU_ETL_CONFIG='/etc/dgu_etl/config.ini'
```

Each command that requires config fill complain if this is not set as it will not be able to locate the configuration file.


### Database 

Databases for specific themes can (and should) be created with the ```etl database``` command which will create the database and set the permissions for the read-only user.

```
etl database init <theme> 
```


## Running ETL

To run all ETL within the health theme, the command looks like 

```
etl service run health 
```

To run the hospitals service within the health theme, the command is:

```
etl service run health.hospitals 
```

## Development

### Development mode

To stop downloads of content being performed every time you test something, you can set 

```
export DEV=1
```

which will only download files if the target file does not exist.

### Adding a theme

Create a new manifest file in the manifests directory (like the others):

    cp manifests/health.yml manifests/<theme>.yml
    vim manifests/<theme>.yml

Create a new directory in api_etl/services/ named after the theme:

    mkdir api_etl/services/<theme>

Create the __init__ where you'll later add the entrypoints for each service

    cp api_etl/services/template/__init__.py api_etl/services/<theme>/

Add the entrypoint to the module in setup.py:

    vim setup.py
    # add it in the list of services    
    python setup.py develop


### Adding a service (an ETL chain for a dataset)

Create any custom ETL python code needed, to be referenced in the entrypoint.

    cp api_etl/services/health/hospitals.py api_etl/services/<theme>/<service>.py
    vim api_etl/services/<theme>/<service>.py

Add the entrypoint:

    vim api_etl/services/<theme>/__init__.py

## Notes

Column names are lower-cased and all non-chars are removed during transformation. 
Duplicate column names are not supported.
Ideally we want the files imported to follow a schema.


## TODO: 

* ~~Simple Configuration:~~
	* ~~Location of manifest files~~
	* ~~DB user to use etc~~
* Workout how we might do lat-lng lookup ...
