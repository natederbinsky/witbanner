#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

##############################################################################
##############################################################################

def demo_adviseeemails(term):
	banner.termset(term)
	print(";".join([x["email"] for x in banner.adviseelisting()]))

##############################################################################
##############################################################################

def main(argv):
	sid=argv[1] if len(argv) is 2 else None
	initialized = False
	while not initialized:
		initialized,sid = banner.init(sid=sid),None

	demo_adviseeemails("201710")
	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
