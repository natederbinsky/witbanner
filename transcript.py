#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

##############################################################################
##############################################################################

def main(argv):
	sid=argv[1] if len(argv) is 2 else None
	initialized = False
	while not initialized:
		initialized,sid = banner.init(sid=sid),None

	term = "201710"
	wid = "W00237397"
	xyz = banner.getxyz_wid(term, wid)

	banner.termset(term)
	banner.idset(xyz)
	print(banner.studenttranscript())
	
	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
