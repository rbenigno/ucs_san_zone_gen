# Overview

Python scripts for generating Cisco MDS/NX-OS SAN zone config snippets based on existing UCS Service Profiles.
The script will connect to a UCS domain to gather the necessary host side data (name and vHBA info).

Fabric parameters are set through a static configuration file (YAML).  This includes VSAN ID and targets.

The zone template uses single-initiator, single-target zoning.

# Usage

* Activate a clean [virtual environment](https://virtualenv.pypa.io/en/stable/).
* Load the required packages with pip.

        pip install -r requirements.txt

* Create a fabric configuration file.

        # Example fabric.yaml
        ---
        A:
          vsan_id: 1001
          target_aliases:
            - xio-c1_x1-sc1-fc1
            - xio-c1_x1-sc2-fc1
            - xio-c1_x2-sc1-fc1
            - xio-c1_x2-sc2-fc1

        B:
          vsan_id: 1002
          target_aliases:
            - xio-c1_x1-sc1-fc2
            - xio-c1_x1-sc2-fc2
            - xio-c1_x2-sc1-fc2
            - xio-c1_x2-sc2-fc2

* Generate the zones by running the ucszonebuild.py script.

        usage: ucszonebuild.py [-h] fabric_cfg ucs_domain username

        positional arguments:
          fabric_cfg  Path to fabric config YAML file
          ucs_domain  UCS Manager Host/IP
          username    UCSM User Account (for AD use 'ucs-<DOMAIN>\<USER>')

        optional arguments:
          -h, --help  show this help message and exit

