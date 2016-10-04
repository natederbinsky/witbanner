#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

##############################################################################
##############################################################################

def findgrade(transcript, subject, num):
	ret = { "inst":[], "transfer":[] }
	
	for transfer in transcript["transfer"]:
		for credit in transfer["credits"]:
			if credit["subject"]==subject and credit["course"]==num:
				ret["transfer"].append((transfer["term"],transfer["source"],))
	
	for term in transcript["terms"]:
		for course in term["courses"]:
			if course["subject"]==subject and course["course"]==num:
				ret["inst"].append((term["term"], course["grade"], course["quality"]))
	
	return ret

def main(argv):
	sid=argv[1] if len(argv) is 2 else None
	initialized = False
	while not initialized:
		initialized,sid = banner.init(sid=sid),None

	term = "201710"
	# wid = "W00237397"
	wid = "W00316837"
	xyz = banner.getxyz_wid(term, wid)

	banner.termset(term)
	banner.idset(xyz)
	
	transcript = banner.studenttranscript()
	print("{}: {}".format(transcript["info"]["Name"][0], findgrade(transcript, "ENGL", "100")))
	
	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
