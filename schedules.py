#!/usr/bin/env python

from __future__ import print_function

from witbanner import banner

import sys

from flask import Flask, render_template, request
import html
import operator
import collections

##############################################################################
##############################################################################

_DAYS = collections.OrderedDict()
_DAYS["M"] = "Monday"
_DAYS["T"] = "Tuesday"
_DAYS["W"] = "Wednesday"
_DAYS["R"] = "Thursday"
_DAYS["F"] = "Friday"

def _demo_time_to_index(t, start):
	hrm,ampm = t.split(" ")
	hr,m = (int(x) for x in hrm.split(":"))
	isam = ampm=="am"

	index = hr
	if isam is False and hr < 12:
		index += 12

	index *= 10
	if m > 30:
		index += 5

	if not start:
		if m is 0:
			index -= 5

	return index

def _demo_facultyschedule(term, instructors, days):
	codes = banner.sectioncodes(term)
	profs = {name:code for code,name in codes["instructors"].items()}

	params = {"term":term,"subjects":codes["subjects"].keys()}
	params["instructors"] = [profs[p] for p in instructors]

	banner.termset(term)
	sections = banner.sectionsearch(**params)

	for section in sections:
		for classmtg in section["class"]:
			if classmtg[1].find("-") is not -1:
				tfrom,tto = classmtg[1].split("-")
				for day in (d for d in classmtg[0] if d in days):
					for tf in range(_demo_time_to_index(tfrom, True), _demo_time_to_index(tto, False)+1, 5):
						if tf>=80 and tf<200:
							days[day][tf].add(section["instructor"])
							
def _demo_studentschedule(term, students, days):
	banner.termset(term)
	
	for student in students:
		xyz = banner.getxyz_wid(term, student)
		banner.idset(xyz)
		
		schedule = banner.studentschedule()
		for entry in schedule:
			for meeting in entry["meetings"]:
				for day in meeting["days"]:
					for tf in range(_demo_time_to_index(meeting["times"][0], True), _demo_time_to_index(meeting["times"][1], False)+1, 5):
						if tf>=80 and tf<200:
							days[day][tf].add(xyz)

def demo_schedule(term, instructors, students):
	days = {d:{t:set() for t in range(80, 200, 5)} for d in _DAYS.keys()}
	
	_demo_facultyschedule(term, instructors, days)
	_demo_studentschedule(term, students, days)
	
	return days

##############################################################################
##############################################################################

def _demo_day(d):
	return "h" if d == "R" else d.lower()

def _demo_time(t):
	return ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"][t-1]
	
def demo_schedulelatex(term, instructors, students):
	days = demo_schedule(term, instructors, students)

	for day,schedule in days.items():
		for slot,prof in schedule.items():
			count = len(prof)
			if count > 0:
				color = "class"
				if count >= (len(instructors)+len(students))/2.:
					color = "office" # red
				elif count > 1:
					color = "away" # yellow
				print("\\slot{}{{{}}}{{\\tc{}{}{}}}{{{}}}{{1}}".format(color, _demo_day(day), _demo_time(slot/10 if slot <= 120 else (slot - 120)/10), "am" if slot < 120 else "pm", "H" if (slot / 5) % 2 is 1 else "",count))

##############################################################################
##############################################################################

app = Flask(__name__)

@app.route("/", methods=["GET"])
def _demo_term():
	finfo = banner.termform()
	
	retval = []	
	retval.append('<form action="profs" method="GET">')
	
	retval.append('<select name="term">')
	for code,name in sorted(finfo["params"]["term"].items(), key=operator.itemgetter(1)):
		retval.append('<option value="{}">{}</option>'.format(html.escape(code), html.escape(name)))
	retval.append('</select>')
	
	retval.append('<input type="submit" value="submit" />')
	
	retval.append('</form>')
	
	return "\n".join(retval)

@app.route("/profs", methods=["GET"])
def _demo_profs():
	codes = banner.sectioncodes(request.args["term"])
	
	retval = []	
	retval.append('<form action="search" method="GET">')
	retval.append('<input type="hidden" name="term" value="{}" />'.format(request.args["term"]))
	
	retval.append('<h3>Faculty</h3>')
	retval.append('<select name="profs" multiple="multiple" size="20">')
	for code,name in sorted(codes["instructors"].items(), key=operator.itemgetter(1)):
		retval.append('<option value="{}">{}</option>'.format(html.escape(name), html.escape(name)))
	retval.append('</select>')
	retval.append('<br />')
	
	retval.append('<h3>W-Numbers (separated by whitespace)</h3>')
	retval.append('<textarea name="students" rows="20" cols="50">')
	retval.append('</textarea>')
	
	retval.append('<br /><br />')
	retval.append('<input type="submit" value="submit" />')
	
	retval.append('</form>')
	
	return "\n".join(retval)
	
def _demo_search_time(slot):
	ampm = "am" if slot < 120 else "pm"
	slot -= 0 if slot < 130 else 120
	m = "30" if (slot / 5) % 2 is 1 else "00"
	h = slot / 10
	return "{}:{} {}".format(h, m, ampm)

def _demo_search_color(count, numprofs):
	if count is 0:
		return "white"
	elif count is 1:
		return "DarkGrey"
	elif count >= numprofs/2.:
		return "Red"
	else:
		return "Yellow"

@app.route("/search", methods=["GET"])
def _demo_search():
	retval = []
	
	profslist = request.args.getlist("profs")
	studentslist = request.args["students"].split()
	
	days = demo_schedule(request.args["term"], profslist, studentslist)
	num = len(profslist) + len(studentslist)
	
	day_names = list(days.keys())
	slot_names = sorted(days[day_names[0]].keys())
	
	retval.append('<h1>Heatmap</h1>')
	if profslist:
		retval.append('<h2>Faculty ({}): '.format(len(profslist)) + html.escape('; '.join(profslist)) + '</h2>')
		
	if studentslist:
		retval.append('<h2>Students ({}): '.format(len(studentslist)) + html.escape('; '.join(studentslist)) + '</h2>')
	
	retval.append('<table border="1">')
	
	retval.append('<tr>')
	retval.append('<th style="width: 80px"></th>')
	for d,name in _DAYS.items():
		retval.append('<th style="width: 80px">{}</th>'.format(html.escape(name)))
	retval.append('</tr>')
	
	for slot in slot_names:
		retval.append('<tr>')
		retval.append('<th>{}</th>'.format(html.escape(_demo_search_time(slot))))
		for d in _DAYS.keys():
			count = len(days[d][slot])
			retval.append('<td style="text-align: center; background-color: {}">{}</td>'.format(_demo_search_color(count, num), html.escape(str(count) if count > 0 else "")))
		retval.append('</tr>')
	
	retval.append('</table>')
	
	return "\n".join(retval)
	
def demo_scheduleweb():
	print("running at http://localhost:8080")
	app.run(host="0.0.0.0", port=8080, debug=False)
	
##############################################################################
##############################################################################

def main(argv):
	if len(argv) is 2:
		banner.init(argv[1])
	else:
		banner.init()
		
	demo_scheduleweb()
	
	# demo_schedulelatex("201710", ("Derbinsky, Nathaniel",), ("W00325547", "W00323663",))

if __name__ == "__main__":
	main(sys.argv)
