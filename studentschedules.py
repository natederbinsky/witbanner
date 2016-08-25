#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

from bs4 import BeautifulSoup

import sys

##############################################################################
##############################################################################

def _demo_schedlatex_parse(source):
	ret = []

	soup = BeautifulSoup(source, "html.parser")
	div = soup.findAll('div',attrs={'class':'pagebodydiv'})[0]
	tables = div.findAll('table', attrs={'class':'datadisplaytable'})

	first = True
	classId = None
	for table in tables:
		if first:
			caption = table.findAll('caption')[0]
			classId = caption.string.split(' - ')[1].strip().replace(' ', '')
			first = False
		else:
			row = table.findAll('tr')[1]
			cols = row.findAll('td')
			time = [{"hour":int(t[0][0]), "min":int(t[0][1]), "am":t[1]=="am"} for t in [[t[0].split(":"), t[1]] for t in [t.split() for t in cols[1].string.split(' - ')]]]
			days = cols[2].string

			for day in days:
				ret.append({"day":str(day), "time":{"from":time[0], "to":time[1]}, "class":str(classId)})
			first = True

	return ret

def _demo_schedlatex_schedule(events, t="class"):
	for event in events:
		day = event["day"].lower() if event["day"]!="R" else "h"
		title = event["class"]
		slotbottom = "todo"
		numslots = "todo"

		toH = event["time"]["to"]["hour"]
		toM = event["time"]["to"]["min"]
		toAM = event["time"]["to"]["am"]

		toNum = toH + (0 if toAM else (12 if toH is not 12 else 0)) + (0.0 if toM is 0 else (0.5 if toM <= 30 else 1.0))

		fromH = event["time"]["from"]["hour"]
		fromM = event["time"]["from"]["min"]
		fromAM = event["time"]["from"]["am"]

		fromNum = fromH + (0 if fromAM else (12 if fromH is not 12 else 0)) + (0.0 if fromM < 30 else 0.5)

		numslots = int((toNum-fromNum) / 0.5)

		toNumSlot = toNum - 0.5
		toRN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"][int(toNumSlot) - 1 - (0 if toNumSlot <= 12 else 12)]
		toAMPM = "am" if toNumSlot < 12 else "pm"
		toHalf = "H" if toNumSlot-int(toNumSlot) else ""
		slotbottom = "\\tc{}{}{}".format(toRN, toAMPM, toHalf)

		print("\\slot{}{{{}}}{{{}}}{{{}}}{{{}}}".format(t, day, slotbottom, "", numslots))

def demo_schedlatex(wids, term):
	banner.termset(term)
	for student in wids:
		xyz = banner.getxyz_wid(term, student)
		banner.idset(xyz)

		parse = _demo_schedlatex_parse(banner.studentschedule()["raw"])
		_demo_schedlatex_schedule(parse)

##############################################################################
##############################################################################

def main(argv):
	if len(argv) is 2:
		banner.init(argv[1])
	else:
		banner.init()

	demo_schedlatex(("W00325547","W00320677","W00259922"), "201710")

	print(banner.lastid())

if __name__ == "__main__":
	main(sys.argv)
