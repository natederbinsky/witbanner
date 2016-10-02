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
	wid = "W00365715"
	xyz = banner.getxyz_wid(term, wid)

	banner.termset(term)
	banner.idset(xyz)
	
	transcript = banner.studenttranscript()
	gpa = transcript["totals"]["overall"]["gpa"] if "overall" in transcript["totals"] else "unknown"
	print("{}: {}".format(transcript["info"]["Name"][0], gpa))
	
	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
