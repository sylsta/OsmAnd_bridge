#!/usr/bin/env python
#
# PyMTP demo scripts
# (c) 2008 Nick Devito
# Released under the GPL v3 or later.
#

import sys
sys.path.insert(0, "../")

import pymtp
import pyid3lib

def usage():
	print "Usage: %s <source> <target>" % (sys.argv[0])

def main():
	if len(sys.argv) <= 3:
		usage()
		sys.exit(2)
		
	mtp = pymtp.MTP()
	mtp.connect()

	source = sys.argv[1]
	target = sys.argv[2]

	file_id = mtp.send_file_from_file(source, target)
	print "Created new track with ID: %s" % (file_id)
	mtp.disconnect()
		
if __name__ == "__main__":
	main()
