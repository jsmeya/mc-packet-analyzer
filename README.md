# mc-packet-analyzer

A packet capture and analysis program for TCP client-server communication on a Minecraft server (under certain conditions), built using Python and Scapy.

## Background

Over the years, I used to play a certain Minecraft server (the same one for which I built the [door code brute forcer](https://github.com/jsmeya/door-code-brute-forcer)).
My idea for this packet analyzer was initially part of that brute forcer project. I wanted to see if I could read the traffic between my client and the server to uncover how the door code system worked behind the scenes. This just led to curiosity about the entirety of what is actually being communicated between a Minecraft client and the server.

Just like with the brute forcer project, I will not be disclosing this minecraft server in specific.

## Encryption

By default (`online-mode=true`), Minecraft starts encrypting client-server communication partway through the Login state, once the key exchange completes. Everything afterward is encrypted with AES/CFB8. Building a packet sniffer for a server under this setting would require implementing a method toward decryption (such as a proxy or modded client). However, this server in specific is 'cracked,' operating in `online-mode=false`, meaning encryption is disabled. This allows for direct, raw packet inspection using Python and Scapy. Compression is still relevant, but that will be covered in a bit.

## Initial Capture

Initially, Scapy's `AsyncSniffer` was used to capture packets over TCP/IP port 25565, with a callback function to extract payloads; it printed a mix of payloads and empty byte strings. The empty byte strings are just TCP segments with no payload (mostly ACKs). Here's an example serverbound sequence:

```text
b'\x03\x00\x03\x01'
b''
b'\x03\x00\x03\x01'
b'\x06\x00\x0f\x00\x93;\x01'
b'\x03\x00\x03\x01'
b'\x03\x00\x03\x01'
b''
b''
b'\x03\x00\x03\x01'
```

## Encapsulation

Before going any further, it's necessary to clarify the classification of "packets" and "payloads" in this scenario. Take the following TCP payload for example (displayed as a bytes literal):

`b'\x03\x00\x03\x01'`

At the application layer (Minecraft), this is a packet. It contains header information and a payload (which will be clarified in the next section). \
At the transport layer (TCP), this is a payload, taken directly from `packet[TCP].payload`. \
This is encapsulation in action, where Minecraft packets are transported within TCP payloads. It's also worth noting that there is not always a one-to-one relationship. Some TCP payloads may contain multiple Minecraft packets, and conversely, large Minecraft packets can be split across multiple TCP segments.

Moving on...

## Payload Analysis

### NOTE: This server in specific was examined in version 1.8.9 and thus used protocol version 47 ([more info](https://minecraft.wiki/w/Protocol?oldid=2772100))

Of course, these TCP payloads mean nothing if we don't know how to read them. Breaking it down:

For starters, a typical Minecraft packet (with [compression](https://minecraft.wiki/w/Protocol?oldid=2772100#With_compression) enabled) is composed of the following:

1. **Packet Length (`VarInt`):** The size of the rest of the packet (including packet ID, data length and data) in bytes.
2. **Data Length (`VarInt`):** The length of the uncompressed packet (packet ID + data) or 0.
3. **Packet ID (`VarInt`):** A numerical identifier that specifies packet type (e.g., chat message, player position, block update, etc.) depending on the current connection state and direction (clientbound/serverbound).
4. **Packet Data:** A sequence of data fields specific to the packet ID (e.g., strings, integers, floats, booleans, or NBT Tags).

To apply this structure, take the following Minecraft packet (again):

`b'\x03\x00\x03\x01'`

1. The first byte here, `0x03`, represents the **packet length**. This is confirmed when examining the rest of the packet, which reveals three additional bytes.
2. The second byte, `0x00`, is the **data length**. Since it is 0, it signifies that the packet is not compressed. Nice!
3. The third byte, `0x03`, represents the **packet ID**. Referring to the `Play` connection state, bound to the server, under this server's protocol version, this is a `Player` packet with a single field: `On Ground`.
4. The final byte, `0x01`, represents the **packet data**. The above packet ID contains a `Boolean` field type: "*True if the client is on the ground, false otherwise*." With a value of one, this packet confirms the player is on the ground. 😎

Pretty cool! :)

## Next Steps

Looking forward, an automated packet analysis pipeline would *heavily* streamline the packet inspection process. Extending the existing architecture, this pipeline would decode packets captured over a given interval by mapping those bytes literals to an existing database. This can be accomplished through either direct API calls to the protocol website or by constructing a static reference database. At a closer look, here's what's next on the agenda:
* Distinguish between clientbound/serverbound packets (either input-directed or through separate sniffer threads)
* Replace `AsyncSniffer()` with `sniff()` for storing packets AND achieving better performance
* Identify the best approach for decoding packets

That's all for now.
