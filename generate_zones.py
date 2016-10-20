#!/usr/bin/env python2.7

"""
Functions to generate MDS zone templates based on a fixed set of fabric settings
and initiator parameters (server name, HBA name, WWPN).
"""

# Define and parse command line arguments
def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("fabric_cfg", help="Path to fabric config YAML file")
    parser.add_argument("initiator_json", help="Path to initiator JSON file")
    return parser.parse_args()


# Load a YAML file
def load_yaml_file(file_path):
    from yaml import load, CLoader as Loader
    with open(file_path) as file:
        data = load(file, Loader=Loader)
    return data


# Load a JSON file
def load_json_file(file_path):
    import json
    with open(file_path) as json_data:
        data = json.load(json_data)
    return data


def generate_device_alias_list(devices):
    aliases = {}
    aliases['A'] = {}
    aliases['B'] = {}

    for fabric in aliases:
        for host in devices:
            for hba in devices[host][fabric]:
                device_alias = "{0}_{1}".format(host, hba)
                wwpn = devices[host][fabric][hba]
                aliases[fabric][device_alias] = wwpn
    return aliases


def generate_device_alias_config(aliases):
    j2template = """
!### FABRIC A
device-alias database
{% for name, vhba in fabric_A.iteritems() %}
  device-alias name {{name}} pwwn {{vhba.wwpn}}
{% endfor %}
device-alias commit

!### FABRIC B
device-alias database
{% for name, vhba in fabric_B.iteritems() %}
  device-alias name {{name}} pwwn {{vhba.wwpn}}
{% endfor %}
device-alias commit
    """
    from jinja2 import Template
    template = Template(j2template, trim_blocks=True, lstrip_blocks=True)
    return template.render(fabric_A=aliases['A'], fabric_B=aliases['B'])


# Generate the MDS zone config snippets
def generate_zone_config(fabric_confg, initiator_aliases):

    vsans = {'A': fabric_confg['A']['vsan_id'],
             'B': fabric_confg['B']['vsan_id']}

    targets = {'A': fabric_confg['A']['target_aliases'],
               'B': fabric_confg['B']['target_aliases']}

    j2template = """
{% for fabric, vsan in vsans.iteritems() %}

!### FABRIC {{fabric}}

{% for initator in initiators[fabric] %}
{% for target in targets[fabric] %}
zone name {{initator}}__{{target}} vsan {{vsan}}
  member device-alias {{initator}}
  member device-alias {{target}}
{% endfor %}
{% endfor %}

zoneset name Fabric_{{fabric}}_XXX vsan {{vsan}}
{% for initator in initiators[fabric] %}
{% for target in targets[fabric] %}
  member {{initator}}__{{target}}
{% endfor %}
{% endfor %}

{% endfor %}
    """

    from jinja2 import Template
    template = Template(j2template, trim_blocks=True, lstrip_blocks=True)
    return template.render(initiators=initiator_aliases, targets=targets, vsans=vsans)


### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':
    # Retrive the command line arguements
    args = parse_args()

    # Fabric and target info
    fabric_config_file = args.fabric_cfg
    fabric_cfg = load_yaml_file(fabric_config_file)

    # Initiators
    initiator_file = args.initiator_json
    initiators = load_json_file(initiator_file)

    # Create a list of device aliases
    device_aliases = generate_device_alias_list(initiators)

    # Print the device-alias config snippets
    print generate_device_alias_config(device_aliases)

    # Create the zone config snippets
    print generate_zone_config(fabric_cfg, device_aliases)