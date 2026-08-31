MintySwc
Python port of MintyTransport.
A simple proxy that translates packets between MCPE versions, so 0.15.10 clients can play on 0.14.3 servers.
How it works
0.15.10 client <--> MintySwc (Python) <--> 0.14.3 server
The proxy accepts 0.15.10 connections, opens a RakNet bridge to the 0.14.3 server, and translates game packets back and forth (v84 <-> v70).
Quick start
Requires Python 3.10+.
Bash
git clone https://github.com/swatoichell-create/MintySwc.git
cd MintySwc
python main.py
Config:
config.json will be generated on first run.
Config
JSON

{
  "localServerAddress": "0.0.0.0:19132",
  "targetServerAddress": "127.0.0.1:19133",
  "logLevel": "INFO"
}
    localServerAddress — proxy port for 0.15.10 players.
    targetServerAddress — target 0.14.3 server.
    logLevel — log verbosity (INFO, DEBUG, TRACE).
License
GPL-3.0. Original Java project by Shiiyuko.
