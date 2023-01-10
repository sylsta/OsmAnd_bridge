#!/usr/bin/env python
#
# PyMTP Demo program
# (c) 2013 Hans-Christoph Steiner
# Released under the GPL-3
#

import sys
sys.path.insert(0, "../") # so the examples work out of the box
import pymtp

mtp = pymtp.MTP()
devices = mtp.detect_devices()
for d in devices:
    entry = d.device_entry
    print('found: ' + entry.vendor + " " + entry.product)
