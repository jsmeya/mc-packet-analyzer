import time
from scapy.all import sniff, AsyncSniffer, TCP, IP

packet_count = 0

def process_packet(packet):
    global packet_count
    if packet.haslayer(TCP) and packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        if src_ip == "192.168.1.214":
            packet_count += 1

            raw_bytes = bytes(packet[TCP].payload)
            print(raw_bytes)

def run_async_sniffer():
    sniffer = AsyncSniffer(filter="tcp port 25565", prn=process_packet, store=False)
    sniffer.start()
    start_time = time.perf_counter()

    try:
        print("Running packet sniffer on TCP port 25565...")
        print("'CTRL + C' to stop at any time.")

        while sniffer.thread.is_alive():
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        pass

    finally:
        if sniffer.running:
            sniffer.stop()

        output_packet_summary(start_time)

        print("\nExiting...")

# Only when using AsyncSniffer()
def output_packet_summary(start_time):
    print(f"\nTotal packet count: {packet_count}")
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time interval: {elapsed_time}")

    packet_rate = packet_count / elapsed_time
    print(f"Packets per second: {packet_rate}")

    return None

def get_packet_count():
    while True:
        try:
            sniff_count = int(input("Enter the amount of packets to capture: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")
    return sniff_count

def main():
    async_option = input("Would you like to sniff asynchronously? (y/n): ").lower()

    if async_option == "y":
        run_async_sniffer()

    elif async_option == "n":

        sniff_count = get_packet_count()
        packets = sniff(count = sniff_count, filter="tcp port 25565", prn=process_packet, store=False)

if __name__ == "__main__":
    main()