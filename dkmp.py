#!/usr/bin/env python3

# PhilleConnect Systemclient v2 - dont kill my process
# © 2019 Johannes Kreutz.

# Include dependencies
import sys
import time

# Include modules
import modules.watchdog as wd

# Startup modes
if len(sys.argv) == 2:
    watchdog = wd.watchdog(3, sys.argv[1])
    watchdog.start()
    # Watchdog only process, so keep main thread blocked
    while True:
        time.sleep(1)
else:
    print("Wrong parameters. Aborting.")
    sys.exit()
