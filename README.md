[![Build Status](https://travis-ci.org/paychex/xray.svg?branch=master)](https://travis-ci.org/paychex/xray)

# Project Description
---
X-RAY captures and records software and mount points of a given host. Utilizing two mongo collections *host_collection*, a overridden collection outlining the software and mount points of a given host, and *software*, a collection that contains the meta data for all software. This is meant to get a scheduled guage of the vendors, platforms, and mounts within your environment.


# Install
---
To install first the following procedure should be followed:
 1. ensure that the server has Python 3.6+<br>
  a. Execute `pip3 install -r requirements.txt`<br>
  b. On Windows Hosts only - `pip3 install pywin32`
 2. Create a mongo database, and python file with the variable "CONNECTION_STRING" with the connection string of the database.
   File Structure:
```
lib\
  mongo_info_prod.py
  mongo_info_nonprod.py
```


<br><br>
# Database Collections
---
### software
Minimum Data
* Package Name
* Software Vendor
* Version Objects

*Additional meta data from external source may be provided, but is not required via script. To add data add directly to the database using the CLI or Mongo GUI. Any data provided will not be provided*

### host_collection
Minimum Data
* Last Updated
* Name (server hostname)
* Last Update Duration (time of execution)
* Mount Objects
* Software Objects

*Any data overridden here will be removed during next execution*

<br><br>
# Execution
---
To execute the module either
* On a host execute the `__init__.py` with the respective flags (use -h for help).
```
usage: __init__.py [-h] [-p PACKAGES] [-s SERVER] [-m MOUNTS] [-d] [-t]
                   [--prod] [--sleep]

A module to parse and record host pacakges to MongoDB

optional arguments:
  -h, --help            show this help message and exit
  -p PACKAGES, --packages PACKAGES
                        host packages file (json output - see "software.py" get_local_mounts() for formatting )
  -s SERVER, --server SERVER
                        server hostname
  -m MOUNTS, --mounts MOUNTS
                        mount points file (json output - see "mounts.py" get_local_mounts() for formatting )
  -d, --debug           Debug output
  -t, --test            Test host capture without pointing to db
  --prod                Write to prod db
  --sleep               Sleep a random time
```

<br><br>
# Database Query
---
Below are some sample queries in which you can capture data
### Host Query
To get the host object for hostname.domain.com
`db.host_collection.find({ "name" : "hostname.domain.com" })`
### Software Query
To get all objects that have the package software-name
`db.host_collection.find( { "software.package_name" : "software-name" })`
### Version Query
To get just the hostnames for servers that have version 0.2.0 of software-name
`db.host_collection.find( { "software.package_name" : "software-name", "software.versions.name": "0.2.0"  }, { name:1, _id:0 } )`

<br><br>

