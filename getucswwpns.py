#!/usr/bin/env python2.7

import os, sys, json, argparse, getpass, re

# Import ucsmsdk
try:
    from ucsmsdk import *
except ImportError, e:
    print "Import error: {}".format(str(e))
    print 'https://communities.cisco.com/docs/DOC-64378'
    sys.exit(1)


# Define and parse command line arguements
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ucs_domain", help="UCS Manager Host/IP")
    parser.add_argument("username", help="UCSM User Account")
    #  parser.add_argument("--password", help="UCSM Password")
    return parser.parse_args()


# Get password from environmental variable or prompt for input
def get_password():
    if os.environ.get('UCSM_PW'):
        return os.environ.get('UCSM_PW')
    else:
        return getpass.getpass('Password:')


def ucs_login(hostname, username, password):
    from ucsmsdk.ucshandle import UcsHandle

    handle = UcsHandle(hostname, username, password)
    handle.login()
    return handle


def ucs_logout(handle):
    handle.logout()


def format_as_device_alias_name(dn):
    re_pattern = 'ls-((?:\w|-|\s)+)\/fc-(.*)$'
    server = re.search(re_pattern, dn).group(1)
    hba = re.search(re_pattern, dn).group(2)
    device_alias = "{0}_{1}".format(server, hba)
    return device_alias


def get_vhba_list(handle):
    vHBADict = {}
    vHBADict['A'] = {}
    vHBADict['B'] = {}
    filter_str = '(addr, "derived",  type="ne")'
    object_array = handle.query_classid('VnicFc', filter_str=filter_str)
    for item in object_array:
        device_alias = format_as_device_alias_name(item.dn)
        vHBADict[item.switch_id][device_alias] = {'dn': item.dn,
                                             'name': item.name,
                                             'wwpn': item.addr}
    return vHBADict



def get_sp_list(handle, parent_dn="org-root"):
    sp_list = []
    filter_str = '(type, "instance")'
    mo = handle.query_dn(parent_dn)
    query_data = handle.query_children(in_mo=mo, class_id='LsServer', filter_str=filter_str)
    for item in query_data:
        sp_list.append(item.name)
    return sp_list


def get_sp_wwpn(handle, sp_name, parent_dn="org-root"):
    """
    This function will return the fibre channel wwpn addresses of a service profile
    Args:
        handle (UcsHandle)
        sp_name (string): Service Profile  name.
        parent_dn (string): Org.
    Returns:
        dict with 'A' and 'B' keys, each containing:
        adaptor name
        wwpn address
    Raises:
        ValueError: If LsServer is not present
    Example:
        sp_wwpn(handle, sp_name="sample_sp", parent_dn="org-root")
        sp_wwpn(handle, sp_name="sample_sp", parent_dn="org-root/sub-org")
    """

    dn = parent_dn + "/ls-" + sp_name
    mo = handle.query_dn(dn)
    if not mo:
        raise ValueError("sp '%s' does not exist" % dn)

    query_data = handle.query_children(in_mo=mo, class_id='VnicFc')

    vHBADict = {}
    FabADict = {}
    FabBDict = {}

    for item in query_data:
        if item.switch_id == 'A':
            FabADict[item.name] = item.addr
        if item.switch_id == 'B':
            FabBDict[item.name] = item.addr

    vHBADict['A'] = FabADict
    vHBADict['B'] = FabBDict

    return vHBADict


### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

# Main function (when running as an executable)
if __name__ == '__main__':
    # Retrive the command line arguements
    args = parse_args()

    # Connection Info
    ucsm_host = args.ucs_domain
    ucsm_user = args.username
    ucsm_pass = get_password()
    ucs_handle = ucs_login(ucsm_host, ucsm_user, ucsm_pass)

    vhba_dict = get_vhba_list(ucs_handle)
    print json.dumps(vhba_dict, sort_keys=True)
