# mc-packet-analyzer

A packet capture and analysis program for TCP client-server communication on a Minecraft server (under certain conditions), built using Python and Scapy.

## Background

Over the years, I used to play a certain Minecraft server (the same one for which I built the [door code brute forcer](https://github.com/jsmeya/door-code-brute-forcer)).
My idea for this packet analyzer was initially part of that brute forcer project. I wanted to see if I could read the traffic between my client and the server to uncover how the door code system worked behind the scenes.

## Encryption

By default (`online-mode=true`), Minecraft encrypts all client-server communication using AES-CFB8 right after the initial login sequence. Building a packet sniffer for a server under this setting would require implementing an additional decryption layer. However, this server in specific is 'cracked,' operating in `online-mode=false`, meaning encryption is disabled. This allows for direct, raw packet inspection using Python and Scapy.

## Initial Capture

Initially, Scapy's `AsyncSniffer` was used to capture packets over TCP/IP port 25565, with a callback function to extract payloads; it printed a mix of raw hex payloads and empty byte strings. Here's an example sequence:

```text
b'\x03\x00\x03\x01'
b'\x03\x00\x03\x01'
b''
b'\x03\x00\x03\x01'
b''
b'\x03\x00\x03\x01'
b''
b''
```

## Encapsulation

Before going any further, it's necessary to clarify the classification of "packets" and "payloads" in this scenario. Take the following TCP payload for example:

`b'\x03\x00\x03\x01'`

At the application layer (Minecraft), this is a packet. It contains header information and a payload (which will be clarified in the next section). \
At the transport layer (TCP), this is a payload. This is from implementing scapy to strip away the header information of the packet. \
This is encapsulation in action, where Minecraft packets are transported within TCP payloads. It's also worth noting that there is not always a one-to-one relationship. Some TCP payloads may contain multiple Minecraft packets. \

Moving on...
