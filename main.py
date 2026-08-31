import asyncio
import logging
import signal
import sys
from pathlib import Path
from minty_transport.config.config_loader import ConfigLoader
from minty_transport.config.address_spec import AddressSpec
from minty_transport.logging.log_level_configurer import LogLevelConfigurer
from minty_transport.proxy.minty_proxy import MintyProxy

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs.txt', mode='a', encoding='utf-8')
        ]
    )

    logger = logging.getLogger("MintySwc")

    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.json")

    config = ConfigLoader.load(config_path)

    LogLevelConfigurer.apply(config.log_level)

    local_address = AddressSpec.parse(config.local_server_address).to_bind_address()
    target_address = AddressSpec.parse(config.target_server_address).to_remote_address()

    if config.target_server_address.startswith("0.0.0.0:") or config.target_server_address.startswith("::"):
        logger.info(f"Target address {config.target_server_address} is wildcard; using {target_address} for outbound UDP")

    proxy = MintyProxy(local_address, target_address)

    def signal_handler():
        logger.info("Shutdown signal received")
        asyncio.create_task(proxy.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: signal_handler())

    try:
        await proxy.start()
        logger.info(f"Config file: {config_path.absolute()}")
        logger.info("MintySwc is running. Press Ctrl+C to stop.")

        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Main loop cancelled")
    finally:
        await proxy.stop()
        logger.info("MintySwc stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
