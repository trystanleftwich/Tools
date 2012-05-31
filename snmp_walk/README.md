## Match Force10 Switch ports to Server Mac's
This script given a range, switch ip's and client ports will use snmp to match a switch port to a server interface.

###USAGE:
Example:
    python server_macadress.py -i 10.10.90 -s 10.10.9.2,10.10.90.3,10.10.90.4 -c 48,49,50,51
    
    Options:
      -i server_ips, --server_ips=server_ips
                            Server ips to connect to servers
      -s switch_ips, --switch_ips=switch_ips
                            Switch ips comma seperated
      -c client_ports, --client_ports=client_ports
                            client ports that connect each switch

###TODO:
* Make the MAC matching more robust
* Allow network ranges for server ips
* Change to allow > 2 stacked switchs
* Add other switch support

###ISSUES:
* Only works with a /24 network for servers and only tested on Force 10 S60 switches.
