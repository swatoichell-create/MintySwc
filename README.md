# MintySwc

A protocol-translating proxy for Minecraft: Pocket Edition that lets 0.15.10 clients connect to 0.14.3 servers by rewriting packets on the fly.

## What is this?

MintySwc is a complete Python rewrite of the original Kotlin MintyTransport project. It acts as a middleman between newer MCPE clients and older servers, translating everything from login packets to entity movements so they can talk to each other.

```
0.15.10 client  <-->  MintySwc  <-->  0.14.3 server
                     (translates 84+ packet types)
```

## What's New in This Version

This isn't just a simple port - I've rebuilt it from the ground up with some serious improvements:

### Complete RakNet Implementation
- Full protocol support including unconnected pings (so servers show up in your local list)
- Proper handshake sequences
- Connection health monitoring with ping/pong
- Automatic retransmission of lost packets
- MTU negotiation for optimal performance
- All the reliability levels you'd expect

### Better Packet Translation
- 84+ packet types mapped between versions
- JWT login decoding for 0.15.10 authentication
- Handles batch packets with compression
- Entity translation (movement, rotation, removal)
- Block updates and motion handling
- Text messages and player lists

### More Robust
- Better error handling throughout
- Detailed logging when things go wrong
- Tracks dropped packets for debugging
- Graceful shutdown handling
- Connection state monitoring

### Performance
- Priority-based packet queuing
- Efficient frame encoding
- Automatic cleanup of old packets
- ACK/NACK compression to save bandwidth

## Requirements

- Python 3.8 or newer
- No external dependencies - just the standard library

## Getting Started

1. Clone or download this repository
2. Navigate to the `MintySwc` directory
3. Create a `config.json` file:

```json
{
  "localServerAddress": "0.0.0.0:19132",
  "targetServerAddress": "127.0.0.1:19133",
  "logLevel": "INFO"
}
```

4. Run it:

```bash
python main.py
```

The config file is optional - if it doesn't exist, one will be created automatically.

## Configuration

| Field                 | What it does                                                      | Default            |
| --------------------- | ----------------------------------------------------------------- | ------------------ |
| `localServerAddress`  | Where MintySwc listens for clients                                 | `0.0.0.0:19132`    |
| `targetServerAddress` | Where to forward connections to (your 0.14.3 server)               | `0.0.0.0:19133`    |
| `logLevel`            | How much to log: `OFF`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE` | `INFO`             |

Logs go to both the console and `logs.txt`.

## How It Works

1. **Client connects** to MintySwc like it's a normal 0.15.10 server
2. **MintySwc establishes** its own connection to the target 0.14.3 server
3. **Packets flow both ways** through the proxy
4. **Each packet gets translated** - IDs get remapped, data structures get reformatted
5. **Special handling** for complex packets like login (JWT decoding), entities (rotation scaling), text messages, etc.
6. **Batches get processed** - compressed packets are decompressed, inner packets translated, then re-compressed

## RakNet Details

This implementation includes the full RakNet protocol:

### Supported Operations
- Unconnected Ping/Pong (server discovery)
- Open Connection Request 1/2 (handshake)
- Connection Request/Accepted
- Frame Set encoding/decoding
- ACK/NACK for reliable delivery
- Connected Ping/Pong for health checks
- Disconnect Notification
- All data packet types (0x80-0x8F)

### Reliability Levels
- **UNRELIABLE**: Fire and forget
- **UNRELIABLE_SEQUENCED**: Ordered but not guaranteed
- **RELIABLE**: Guaranteed delivery, no ordering
- **RELIABLE_ORDERED**: Guaranteed delivery + ordering
- **RELIABLE_SEQUENCED**: Guaranteed delivery + sequencing
- **UNRELIABLE_WITH_ACK_RECEIPT**: Unreliable with acknowledgment
- **RELIABLE_WITH_ACK_RECEIPT**: Reliable with acknowledgment

### Performance Features
- MTU negotiation (548-1464 bytes)
- Priority queuing (Immediate, High, Medium, Low)
- ACK/NACK compression
- Split packet handling for large data
- 30-second connection timeout
- Adaptive retransmission based on RTT

## Packet Translation

### Bidirectional Mapping
- 84+ packet IDs mapped between 0.15.10 and 0.14.3
- Fallback to ID rewrite for unmapped packets
- Per-packet special handling where needed

### Special Translators
- **Login**: JWT chain → old login format
- **Batch**: Decompress, translate inner packets, recompress
- **Text**: Message type conversion
- **Add Entity**: Rotation scaling between versions
- **Move Entity**: Byte angle ↔ float angle conversion
- **Remove Player**: Split into player list removal + entity removal
- **Update Block**: Count-prefixed → flat format
- **Set Entity Motion**: Batch translation

### Data Models
- Login data with JWT chain parsing
- Skin data translation
- Slot summaries for equipment
- Text view with parameters

## Project Structure

```
MintySwc/
├── main.py                    # Entry point
├── config.json               # Configuration
├── logs.txt                  # Log file
└── minty_transport/
    ├── util/                 # Binary utilities
    │   ├── binary.py
    │   ├── byte_reader.py
    │   ├── byte_writer.py
    │   └── zlib.py
    ├── config/               # Configuration handling
    │   ├── address_spec.py
    │   ├── config_loader.py
    │   └── proxy_config.py
    ├── logging/              # Logging setup
    │   └── log_level_configurer.py
    ├── raknet/               # Full RakNet implementation
    │   ├── raknet_protocol.py
    │   ├── raknet_connection.py
    │   ├── local_raknet_server.py
    │   ├── local_raknet_session.py
    │   ├── remote_raknet_client.py
    │   ├── raknet_handler.py
    │   └── raknet_tuning.py
    ├── mcpe/                 # MCPE packet translation
    │   ├── mcpe_protocol.py
    │   ├── mcpe_packet_ids.py
    │   ├── mcpe_packet_map.py
    │   ├── mcpe_translator.py
    │   ├── login_codec.py
    │   ├── batch_codec.py
    │   ├── text_type.py
    │   ├── model/            # Data models
    │   └── translator/       # Specific packet translators
    └── proxy/                # Proxy logic
        ├── minty_proxy.py
        └── proxy_bridge.py
```

## Development

### Testing

1. Set up a 0.14.3 MCPE server
2. Configure `config.json` with your server details
3. Run `python main.py`
4. Connect a 0.15.10 client to the proxy
5. The server should appear in your local server list

### Debugging

Set `logLevel` to `DEBUG` in `config.json` to see:
- Detailed packet translation logs
- RakNet protocol details
- Packet drop statistics
- Connection state changes

### Adding New Translators

1. Create a new class in `minty_transport/mcpe/translator/`
2. Inherit from `PacketTranslator`
3. Implement the `translate` method
4. Register it in `ClientToServerRegistry` or `ServerToClientRegistry`

Example:
```python
from ..packet_translator import PacketTranslator
from ..packet_direction import PacketDirection
from ..mcpe_packet_ids import McpePacketIds

class MyTranslator(PacketTranslator):
    def __init__(self):
        super().__init__(PacketDirection.CLIENT_TO_SERVER, 
                        McpePacketIds.NEW_MY_PACKET, 
                        McpePacketIds.OLD_MY_PACKET)

    def translate(self, packet: bytes, context):
        # Your translation logic here
        return [translated_packet]
```

## Monitoring

The proxy logs:
- Client connections and disconnections
- Packet translation statistics
- Dropped packets (with IDs and counts)
- Connection health monitoring
- Errors with full stack traces

## Troubleshooting

**Server not showing in local list?**
- Check that `localServerAddress` is set correctly
- Make sure you're using the right port (default 19132)
- Try setting `logLevel` to `DEBUG` to see if pings are being received

**Connection dropping?**
- Check if the target server is actually running
- Verify `targetServerAddress` is correct
- Look at the logs for error messages
- Try increasing timeout values in raknet_tuning.py

**Packets getting dropped?**
- Set `logLevel` to `DEBUG` to see which packets are unsupported
- Some packet types might not have translators yet
- Check if the packet IDs match between versions

## License

Copyright (C) 2026 Shiiyuko

MintySwc is free software licensed under the GNU General Public License v3.0 or later. It comes with ABSOLUTELY NO WARRANTY. You're welcome to redistribute it under certain conditions.

## Credits

Based on the original MintyTransport project by Shiiyuko, rewritten in Python with enhancements.
