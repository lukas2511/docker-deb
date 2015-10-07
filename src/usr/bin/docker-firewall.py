#!/usr/bin/env python

import sys
import subprocess

sys.path.append("/etc/firewall")
from ports import ports

existing_rules = {}
existing_rules['iptables'] = subprocess.check_output(["iptables","-t","nat","-S","PREROUTING"]).splitlines()
existing_rules['ip6tables'] = subprocess.check_output(["ip6tables","-t","nat","-S","PREROUTING"]).splitlines()

mapped_ports = {'iptables': {'tcp': [], 'udp': []}, 'ip6tables': {'tcp': [], 'udp': []}}

for firewall in ['iptables', 'ip6tables']:
    for rule in existing_rules[firewall]:
        if not 'br0' in rule:
            continue

        rule = rule.split()
        interface = rule[rule.index("-i")+1]
        if not interface == "br0":
            continue

        proto = rule[rule.index("-p")+1]
        port = rule[rule.index("--dport")+1]
        dest = rule[rule.index("--to-destination")+1]

        if not port in ports[proto]:
            print("Removing " + proto + " port forwarding: " + port + " -> " + dest)
            rule[0] = "-D"
            subprocess.check_output([firewall, "-t", "nat"] + rule)
        elif dest != ports[proto][port][firewall]:
            print("Updating " + proto + " port forwarding: " + port + " -> " + ports[proto][port][firewall])
            rule[0] = "-D"
            subprocess.check_output([firewall, "-t", "nat"] + rule)
            rule[0] = "-A"
            rule[rule.index("--to-destination")+1] = ports[proto][port][firewall]
            subprocess.check_output([firewall, "-t", "nat"] + rule)
            mapped_ports[firewall][proto].append(port)
        else:
            mapped_ports[firewall][proto].append(port)

for firewall in ['iptables', 'ip6tables']:
    for proto in ["tcp", "udp"]:
        for port, forwarding in ports[proto].items():
            if not port in mapped_ports[firewall][proto]:
                print("Adding " + proto + " port forwarding: " + port + " -> " + forwarding[firewall])
                rule = ["-A", "PREROUTING", "-i", "br0", "-p", proto, "--dport", port, "-j", "DNAT", "--to-destination", forwarding[firewall]]
                subprocess.check_output([firewall, "-t", "nat"] + rule)

#print(ip6tables)
