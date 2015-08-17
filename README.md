# ETL Tools for DGU API Server

This repository contains a collection of tools which will, based on a YAML manifest file:

* Download the RAW data via data.gov.uk
* Transforms the data in some small ways (e.g. split postcode to store outward code separately)
* Create the necessary database and database tables, and grant read-only permission to the default user 

APIs are split into themes, and services, where each theme can have multiple services.  So for instance the ```health``` theme will have a ```hospitals``` service (and probably others).


## Installation




## Configuration




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
