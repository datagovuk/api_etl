# ETL Tools for DGU API Server

This repository contains a collection of tools which will, based on a YAML manifest files:

* Create a database for a theme 
* Download the RAW data via data.gov.uk
* Transforms the data in some small ways (e.g. split postcode to store outward code separately)
* Create the necessary database and database tables, and grant read-only permission to the default user 

APIs are split into themes, and services, where each theme can have multiple services.  So for instance the ```health``` theme will have a ```hospitals``` service (and probably others).


## Installation




## Configuration

### First task 

Before setting the configuration file, the following command should be run to obtain the command line required to set up the accounts.  You will be prompted for the password for each user, which will be used in the configuration file later.

```
etl database once 
```

### Configuration file 

Copy the sample.ini file and change the settings to reflect your setup.  Once the new .ini file is complete, the full path to the file should be set as an environment variable:

```
export DGU_ETL_CONFIG='/var/etl/config.ini'
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




## TODO: 

* Simple Configuration:
	* Location of manifest files 
	* DB user to use etc
