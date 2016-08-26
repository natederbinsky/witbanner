#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

##############################################################################
##############################################################################

def demo_comp1000emails(term, instructors=None):
	codes = banner.sectioncodes(term)
	schedules = {name:code for code,name in codes["schedules"].items()}

	params = {"term":term, "subjects":["COMP"], "num":"1000", "schedules":[schedules['Lecture']]}
	if instructors is not None:
		profs = {name:code for code,name in codes["instructors"].items()}
		params["instructors"] = [profs[p] for p in instructors]

	banner.termset(term)
	sections = banner.sectionsearch(**params)
	if sections is not None:
		emails = []
		comp1000 = [s["crn"] for s in sections]
		for s in comp1000:
			print("Querying {}...".format(s))
			crn = banner.crnset(s)
			if crn is not None:
				print(" Getting students")
				students = banner.summaryclasslist()
				if students is not None:
					print(" Grabbing e-mails")
					for student in students:
						emails.append(student["email"])
	print(",".join(emails))
	print(len(emails))

##############################################################################
##############################################################################

def main(argv):
	if len(argv) is 2:
		banner.init(argv[1])
	else:
		banner.init()

	demo_comp1000emails("201710")
	demo_comp1000emails("201710",["Derbinsky, Nathaniel"])

	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
