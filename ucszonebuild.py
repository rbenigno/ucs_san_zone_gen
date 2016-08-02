#!/usr/bin/env python2.7

from zonebuild import *
from getucswwpns import *

# Define and parse command line arguments
def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("fabric_cfg", help="Path to fabric config YAML file")
    parser.add_argument("ucs_domain", help="UCS Manager Host/IP")
    parser.add_argument("username", help="UCSM User Account (for AD use 'ucs-<DOMAIN>\<USER>')")
    return parser.parse_args()


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

    # Connect to UCS Manager
    ucsm_host = args.ucs_domain
    ucsm_user = args.username
    ucsm_pass = get_password()
    ucs_handle = ucs_login(ucsm_host, ucsm_user, ucsm_pass)

    # Generate the vHBA list from UCS
    device_aliases = get_vhba_list(ucs_handle)

    # Print the device-alias config snippets
    print generate_device_alias_config(device_aliases)

    # Print the zone config snippets
    print generate_zone_config(fabric_cfg, device_aliases)