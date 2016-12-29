#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

##############################################################################
##############################################################################

def demo_userinfo(emailsonly, term, prefix, num, instructors=None):
	codes = banner.sectioncodes(term)
	schedules = {name:code for code,name in codes["schedules"].items()}

	params = {"term":term, "subjects":[prefix], "num":num, "schedules":[schedules['Lecture']]}
	if instructors is not None:
		profs = {name:code for code,name in codes["instructors"].items()}
		params["instructors"] = [profs[p] for p in instructors]

	banner.termset(term)
	sections = banner.sectionsearch(**params)
	if sections is not None:
		emails = []
		print("Querying... ", end="")
		sys.stdout.flush()
		for s in sections:
			print("s{}={}".format(s["section"], s["crn"]), end=" ")
			sys.stdout.flush()
			crn = banner.crnset(s["crn"])
			if crn is not None:
				# Getting students
				students = banner.summaryclasslist()
				if students is not None:
					# Grabbing info
					for student in students:
						if emailsonly:
							emails.append(student["email"])
						else:
							emails.append((student["email"] + " | " + student["email"].split("@")[0] + " | " + student["name_firstfirst"]))
		print()
		print("\n".join(emails))

##############################################################################
##############################################################################

def main(argv):
	sid=argv[1] if len(argv) is 2 else None
	initialized = False
	while not initialized:
		initialized,sid = banner.init(sid=sid),None

	# demo_userinfo(False, "201720", "COMP", "1050")
	# demo_userinfo(True, "201720", "COMP", "1050")
	demo_userinfo(False, "201720", "COMP", "1050", ("Derbinsky, Nathaniel",))
	demo_userinfo(True, "201720", "COMP", "1050", ("Derbinsky, Nathaniel",))

	# print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
