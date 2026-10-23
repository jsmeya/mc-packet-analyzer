import sys
import time
from scapy.all import AsyncSniffer, TCP, IP

packet_count = 0
start_time = time.perf_counter()

def process_packet(packet):
    global packet_count
    if packet.haslayer(TCP) and packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        packet_count += 1

        raw_bytes = bytes(packet[TCP].payload)
        print(raw_bytes)

def output_packet_summary():
    print(f"\nTotal packet count: {packet_count}")
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time interval: {elapsed_time}")

    packet_rate = packet_count / elapsed_time
    print(f"Packets per second: {packet_rate}")

    return None

sniffer = AsyncSniffer(filter="tcp port 25565", prn=process_packet, store=False)
sniffer.start()

try:
    print("Running packet sniffer on TCP port 25565...")
    print("'CTRL + C' to stop at any time.")

    while sniffer.thread.is_alive():
        time.sleep(0.5)
except KeyboardInterrupt:
    sniffer.stop()

    output_packet_summary()

    print("\nExiting...")
    sys.exit(0)