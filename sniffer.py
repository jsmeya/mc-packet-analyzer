import sys
import time
from scapy.all import AsyncSniffer, TCP, IP

def process_packet(packet):
    if packet.haslayer(TCP) and packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        payload = bytes(packet[TCP].payload)
        print(payload)

sniffer = AsyncSniffer(filter="tcp port 25565", prn=process_packet, store=False)
sniffer.start()

try:
    print("Running packet sniffer on TCP port 25565...")
    print("'CTRL + C' to stop at any time.")

    while sniffer.thread.is_alive():
        time.sleep(0.5)
except KeyboardInterrupt:
    sniffer.stop()
    print("\nExiting...")
    sys.exit(0)