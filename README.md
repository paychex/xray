[![Build Status](https://travis-ci.org/paychex/xray.svg?branch=master)](https://travis-ci.org/paychex/xray)[![codecov](https://codecov.io/gh/paychex/xray/branch/master/graph/badge.svg)](https://codecov.io/gh/paychex/xray)

# Project Description
---
X-RAY captures and records software and mount points of a given host.


The module allows for two different types of data store with mongo being the preferred method:

### Mongo
Utilizing two mongo collections *host_collection*, a overridden collection outlining the software and mount points of a given host, and *software*, a collection that contains the meta data for all software. This is meant to get a scheduled guage of the vendors, platforms, and mounts within your environment.

### API
Utilizing an api structure of */virtualmachine* for the hosts, and */software*, the module allows you to get, put, and post. If your api endpoint structure is different modify the [api class](xray/api.py).


# Install
---
To install first the following procedure should be followed:
 1. ensure that the server has Python 3.6+<br>
  a. Execute `pip3 install git+https://github.com/paychex/xray.git`<br>
  b. On Windows Hosts only - `pip3 install pywin32`

<br><br>
# Mongo Database Collections
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

# API Structure
- /virtual machine
  - hostname is the foreign relation. */virtualmachine?name=hostame
- software
  - vm id is the foreign relation. */software?vm=id
  * Table includes: software name, vendor, version name, and version install/removal dates
  * When posting to the api, this module assumes that for all software, the api will reject the request if a record already exists for a concatination of package name, version, and vm.

<br><br>
# Execution
---
The main script was created as a wrapper for the xray module. It should be seen as a sample for how to interact with the module.
* On a host execute the `main.py` with the respective flags (use -h for help).
```
usage: main.py [-h] [-p PACKAGES] [-s SERVER] [-m MOUNTS] [-d] [-t]
                   [--prod] [--sleep]

A module to parse and record host pacakges to MongoDB or an API

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
  --sleep               Sleep a random time
```

# Environment Variables
---
- username (optional) - user for api auth (default: executing username)
- password (optional) - password for api auth (default: prompted)
- CONNECTION_STRING (optional) - if specified will use connection string and auth to mongo (default: utilze api)
- XRAY_ENDPOINT (required if no CONNECTION_STRING) - api endpoint to utilize for rest calls


<br><br>
# Mongo Database Query
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

# Contributing
When contributing, make sure you add your name to the setup.py file.


