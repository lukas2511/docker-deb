#!/usr/bin/env python

import sys
import subprocess

if len(sys.argv) < 3:
    print("Usage: " + sys.argv[0] + " public_interface docker_interface")
    sys.exit(1)

PUBLIC_INTERFACE = sys.argv[1]
DOCKER_INTERFACE = sys.argv[2]

sys.dont_write_bytecode = True
sys.path.append("/etc/firewall")
from ports import ports

found_docker_rules = False
for line in subprocess.check_output(["iptables","-S"]).splitlines():
    if '-N DOCKER' in line:
        found_docker_rules = True

if not found_docker_rules:
    subprocess.check_output(["iptables", "-N", "DOCKER"])
    subprocess.check_output(["iptables", "-A", "FORWARD", "-o", DOCKER_INTERFACE, "-j", "DOCKER"])
    subprocess.check_output(["iptables", "-A", "FORWARD", "-o", DOCKER_INTERFACE, "-m", "conntrack", "--ctstate", "RELATED,ESTABLISHED", "-j", "ACCEPT"])
    subprocess.check_output(["iptables", "-A", "FORWARD", "-i", DOCKER_INTERFACE, "!", "-o", DOCKER_INTERFACE, "-j", "ACCEPT"])
    subprocess.check_output(["iptables", "-A", "FORWARD", "-i", DOCKER_INTERFACE, "-o", DOCKER_INTERFACE, "-j", "ACCEPT"])
    subprocess.check_output(["iptables", "-t", "nat", "-A", "POSTROUTING", "-s", "172.17.0.0/16", "!", "-o", DOCKER_INTERFACE, "-j", "MASQUERADE"])

existing_rules = {}
existing_rules['iptables'] = subprocess.check_output(["iptables","-t","nat","-S","PREROUTING"]).splitlines()
existing_rules['ip6tables'] = subprocess.check_output(["ip6tables","-t","nat","-S","PREROUTING"]).splitlines()

mapped_ports = {'iptables': {'tcp': [], 'udp': []}, 'ip6tables': {'tcp': [], 'udp': []}}

for firewall in ['iptables', 'ip6tables']:
    for rule in existing_rules[firewall]:
        if not PUBLIC_INTERFACE in rule:
            continue

        rule = rule.split()
        interface = rule[rule.index("-i")+1]
        if not interface == PUBLIC_INTERFACE:
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
                rule = ["-A", "PREROUTING", "-i", PUBLIC_INTERFACE, "-p", proto, "--dport", port, "-j", "DNAT", "--to-destination", forwarding[firewall]]
                subprocess.check_output([firewall, "-t", "nat"] + rule)

#print(ip6tables)
