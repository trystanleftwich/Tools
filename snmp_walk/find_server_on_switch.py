#!/usr/bin/env python
""" This script given a range, switch ip's and client ports will use snmp to match a switch port to a server interface.

    USAGE:
        python server_macadress.py -i 10.10.90 -s 10.10.9.2,10.10.90.3,10.10.90.4 -c 48,49,50,51
        
        Options:
          -i server_ips, --server_ips=server_ips
                                Server ips to connect to servers
          -s switch_ips, --switch_ips=switch_ips
                                Switch ips comma seperated
          -c client_ports, --client_ports=client_ports
                                client ports that connect each switch
    
    TODO:
        Make everything more robust in MAC matching, network ranges, number of stacked switch and type of switch.

    ISSUES:
        Only works with a /24 network for servers and only test on Force 10 S60 switches.
"""
from optparse import OptionParser
import os
import re
import socket


def find_server_macs(server_range):
    """ Given a range it will log into each server and get the MAC of each interface
    """
    server_addr = {}
    
    hwaddr_regex = re.compile("eth\d+ .* HWaddr (\S+)")
    inet_regex = re.compile(".*inet addr:(\S+)\s+Bcast:.* Mask:.*")
    # TODO: make the user be able to pass in ranges. Defaults to /24 
    for server_octect in xrange(0,256):
        server = "%s.%d"%(server_range,server_octect)
        cmd = """ssh -t %s 'for i in {1..10}; do /sbin/ifconfig eth$i | /bin/grep -E -e "HWaddr|inet addr";done'"""%(server)
        lines = os.popen(cmd).readlines()
    
        hwaddr, inet = "",""
    
        for line in lines:
            if hwaddr_regex.match(line):
                hwaddr = hwaddr_regex.match(line).group(1)
            elif inet_regex.match(line):
                inet = inet_regex.match(line).group(1)
            if hwaddr and inet:
                try:
                    server_name = socket.gethostbyaddr(server)[0] 
                except:
                    server_name = server
                server_addr[hwaddr] = [ inet, server_name]
                hwaddr, inet = "",""

    return server_addr

def snmpwalk(server_macs,switchs,client_ports):
    """ Walks the switch ips via SNMP finding all MACS that match
        previously found via the
    """
    switches = switchs.split(',')
    client_ports = client_ports.split(',')
    
    for switch in switches:
        print switch
        # TODO: Make this useable on other switchs not just Force 10
        snmp_cmd = "snmpwalk -v 2c -c tfly-snmp-community %s .1.3.6.1.2.1.17.7.1.2.2.1.2"%switch
        lines = os.popen(snmp_cmd).readlines()
    
    
        for line in lines:
            combined = line.split(' ')[0].split('.')[-7:]
            port_num = line.split(' ')[-1].rstrip()
    
            vlan = combined[0]
            # TODO: Make this more robust
            mac_address = ':'.join([hex(int(i))[2:] for i in combined[1:]])
            mac_address_up = ':'.join([str.upper(hex(int(i))[2:]) for i in combined[1:]])
    
    
            if port_num not in client_ports and str(int(port_num)-56) not in client_ports:
                # TODO: Make this more robust, ability for up to 5 stacked switchs
                if int(port_num) < 56:
                    port_num="0/%s"%int(port_num)
                else:
                    port_num="1/%s"%(int(port_num)-56)
    
                if mac_address in server_macs:
                    print vlan,mac_address, port_num, server_macs[mac_address][0], server_macs[mac_address][1]
                elif mac_address_up in server_macs:
                    print vlan,mac_address, port_num, server_macs[mac_address_up][0], server_macs[mac_address_up][1]
                else:
                    print vlan,mac_address, port_num


def main():
    parser = OptionParser()
    parser.add_option("-i", "--server_ips", dest="server_ips",
                      help="Server ips to connect to servers", metavar="server_ips")
    parser.add_option("-s", "--switch_ips", dest="switch_ips",
                      help="Switch ips comma seperated", metavar="switch_ips")
    parser.add_option("-c", "--client_ports", dest="client_ports",
                      help="client ports that connect each switch", metavar="client_ports")
    (options, args) = parser.parse_args()

    print options

    server_macs = find_server_macs(options.server_ips)
    snmpwalk(server_macs,options.switch_ips,options.client_ports)



if __name__ in '__main__':
    main()
