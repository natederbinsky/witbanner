#!/usr/bin/env python

from __future__ import print_function

import sys

import requests
import urlparse
import urllib

from bs4 import BeautifulSoup

##############################################################################
##############################################################################

_BASE_URL = "https://prodweb2.wit.edu"
_SID = None

def _banner_call(endpoint, method, params):
	global _SID
	if _SID is None:
		return False, None

	r = getattr(requests,method)(urlparse.urljoin(_BASE_URL, endpoint), cookies={"SESSID":_SID}, data=params)
	if "SESSID" in r.cookies:
		_SID = r.cookies["SESSID"]
		return True, r
	else:
		_SID = None
		return False, r

def banner_get(endpoint, params={}):
	return _banner_call(endpoint, "get", params)

def banner_post(endpoint, params={}):
	return _banner_call(endpoint, "post", params)

def banner_init(sid):
	global _SID
	_SID = sid

def banner_lastid():
	global _SID
	return _SID

##############################################################################
##############################################################################

# necessary hack because banner doesn't properly close tags
def _getstring(tag):
	firstline = str(tag).splitlines()[0]
	return firstline[firstline.find(">")+1:].strip()

def parse_select(select):
	return {str(option["value"]):_getstring(option) for option in select.find_all("option")}

##############################################################################
##############################################################################

def parse_menu(html):
	retval = { "links":{} }
	soup = BeautifulSoup(html, "html.parser")

	retval["title"] = str(soup.title.string)

	maintable = soup.find("table", {"class":"menuplaintable"})
	for link in maintable.find_all("a", {"class":"submenulinktext2"}):
		retval["links"][str(link.string)] = str(link["href"])

	return retval

def parse_form(html):
	retval = { "params":{} }
	soup = BeautifulSoup(html, "html.parser")

	retval["title"] = str(soup.title.string)

	form = soup.find("div", {"class":"pagebodydiv"}).find("form")

	retval["action"] = str(form["action"])

	for select in form.find_all("select"):
		retval["params"][str(select["name"])] = parse_select(select)

	for hidden in form.find_all("input", {"type":"hidden"}):
		retval["params"][str(hidden["name"])] = str(hidden["value"])

	return retval

def parse_summaryclasslist(html):
	retval = []
	soup = BeautifulSoup(html, "html.parser")

	# 0=course information, 1=enrollment counts
	infotable = soup.find_all("table", {"class":"datadisplaytable"})[2]
	for student in infotable.find_all("tr")[1:]:
		info = {}
		fields = student.find_all("td")

		info["wid"] = str(fields[2].span.string)
		info["name_lastfirst"] = str(fields[1].span.a.string)
		info["name_firstfirst"] = str(fields[9].span.a["target"])
		info["email"] = str(fields[9].span.a["href"].split(":")[1])
		info["img"] = str(fields[10].img["src"])

		retval.append(info)

	return retval

def parse_detailclasslist(html):
	retval = []
	soup = BeautifulSoup(html, "html.parser")

	# 0=course information, 1=enrollment counts
	infotable = soup.find_all("table", {"class":"datadisplaytable"})[2]
	rowstate = 1
	info = {}
	for row in infotable.find_all("tr")[1:]:
		if rowstate is 1:
			fields = row.find_all("td")
			info["wid"] = str(fields[2].string)
			info["name_lastfirst"] = str(fields[1].a.string)
			info["email"] = str(fields[5].span.a["href"].split(":")[1])
			rowstate+=1
			continue
		elif rowstate in [2, 3, 4]:
			rowstate+=1
			continue
		elif rowstate in [5, 6]:
			if row.find("th") is None:
				rowstate+=1
			else:
				info[str(row.th.string.split(":")[0])] = str(row.td.string).strip()
		elif rowstate is 7:
			rowstate = 1
			retval.append(info)
			info = {}
			continue

	# don't forget the last student!
	retval.append(info)

	return retval

def parse_courselist(html):
	retval = []
	soup = BeautifulSoup(html, "html.parser")

	for course in soup.find_all("form", {"action":"/SSBPROD/bwskfcls.P_GetCrse"}):
		info = {
			"subj":str(course.find("input", {"name":"sel_subj", "value":lambda x: x!="dummy"})["value"]),
			"num":str(course.find("input", {"name":"SEL_CRSE"})["value"]),
			"title":str(course.parent.find_previous_sibling("td").string),
		}
		retval.append(info)

	return retval



def parse_searchform(html):
	soup = BeautifulSoup(html, "html.parser")
	selects = {
		"sel_subj":"subjects",
		"sel_schd":"schedules",
		"sel_levl":"levels",
		"sel_ptrm":"parts",
		"sel_instr":"instructors",
	}

	return {key:parse_select(soup.find("select", {"name":name})) for name,key in selects.items()}

def parse_sectionlist(html):
	retval = []
	soup = BeautifulSoup(html, "html.parser")

	maintable = soup.find("table", {"class":"datadisplaytable"})

	if maintable is not None:
		state = 1
		for row in maintable.find_all("tr"):
			if state is 1:
				state+=1
				continue
			elif state is 2:
				state+=1
				continue
			elif state is 3:
				cols = row.find_all("td")
				if len(cols) is 0:
					state = 2
				else:
					if cols[1].find("a") is not None:
						course = {}
						course["crn"] = str(cols[1].a.string)
						course["status"] = str(cols[0].string)
						course["subj"] = str(cols[2].string)
						course["num"] = str(cols[3].string)
						course["section"] = str(cols[4].string)
						course["credits"] = str(cols[6].string)
						course["title"] = str(cols[7].string)
						course["cap"] = str(cols[10].string)
						course["active"] = str(cols[11].string)
						course["attr"] = str(cols[16].string.strip())
						course["instructor"] = ' '.join(str(''.join([s for s in cols[13].stripped_strings])).split())
						course["class"] = [(str(cols[8].string),str(cols[9].string),str(cols[15].string))]

						retval.append(course)
					else:
						retval[len(retval)-1]["class"].append((str(cols[8].string),str(cols[9].string),str(cols[15].string)))

				continue

	return retval

##############################################################################
##############################################################################

def banner_mainmenu():
	good,r = banner_get("/SSBPROD/twbkwbis.P_GenMenu?name=bmenu.P_MainMnu")
	if good:
		return parse_menu(r.text)
	else:
		return None

def banner_facultymenu():
	good,r = banner_get("/SSBPROD/twbkwbis.P_GenMenu?name=bmenu.P_FacMainMnu")
	if good:
		return parse_menu(r.text)
	else:
		return None

def banner_termform():
	good,r = banner_get("/SSBPROD/bwlkostm.P_FacSelTerm")
	if good:
		return parse_form(r.text)
	else:
		return None

def banner_termset(term):
	good,r = banner_post("/SSBPROD/bwlkostm.P_FacStoreTerm", {"term":term, "name1":"bmenu.P_FacMainMnu"})
	if good:
		return term
	else:
		return None

def banner_crnform():
	good,r = banner_get("/SSBPROD/bwlkocrn.P_FacCrnSel")
	if good:
		return parse_form(r.text)
	else:
		return None

def banner_crnset(crn):
	# unsure if calling_proc should be P_FACENTERCRN or P_FACCRNSEL, but I'm guessing the former is more flexible
	good,r = banner_post("/SSBPROD/bwlkocrn.P_FacStoreCRN", {"crn":crn, "name1":"bmenu.P_FacMainMnu", "calling_proc_name":"P_FACENTERCRN"})
	if good:
		return crn
	else:
		return None

def banner_summaryclasslist():
	good,r = banner_get("/SSBPROD/bwlkfcwl.P_FacClaListSum")
	if good:
		return parse_summaryclasslist(r.text)
	else:
		return None

def banner_detailclasslist():
	good,r = banner_get("/SSBPROD/bwlkfcwl.P_FacClaList")
	if good:
		return parse_detailclasslist(r.text)
	else:
		return None

def banner_sectiontermform():
	good,r = banner_get("/SSBPROD/bwskfcls.p_sel_crse_search")
	if good:
		return parse_form(r.text)
	else:
		return None

# not sure if this is ever going to be useful... (just sets the term_in in searches)
def banner_sectiontermset(term):
	good,r = banner_post("/SSBPROD/bwckgens.p_proc_term_date", {"p_term":term, "p_calling_proc":"P_CrseSearch"})
	if good:
		return term
	else:
		return None

def banner_coursesearch(term, subjects):
	params = [
		("sel_subj","dummy"),
		("path","1"),
		("rsts","dummy"),
		("crn","dummy"),
		("sel_day","dummy"),
		("sel_schd","dummy"),
		("sel_insm","dummy"),
		("sel_camp","dummy"),
		("sel_levl","dummy"),
		("sel_sess","dummy"),
		("sel_instr","dummy"),
		("sel_ptrm","dummy"),
		("sel_attr","dummy"),
		("begin_ap","x"),
		("end_ap","y"),
		("SUB_BTN","Course Search"),
		("sel_crse",""),
		("sel_title",""),
		("sel_from_cred",""),
		("sel_to_cred",""),
		("sel_ptrm","%"),
		("begin_hh","0"),
		("begin_mi","0"),
		("end_hh","0"),
		("end_mi","0")
	]

	params.append(("term_in",term))
	for subj in subjects:
		params.append(("sel_subj", subj))

	good,r = banner_post("/SSBPROD/bwskfcls.P_GetCrse", params)
	if good:
		return parse_courselist(r.text)
	else:
		return None

def banner_sectioncodes(term):
	params = [
		("sel_subj","dummy"),
		("path","1"),
		("rsts","dummy"),
		("crn","dummy"),
		("sel_day","dummy"),
		("sel_schd","dummy"),
		("sel_insm","dummy"),
		("sel_camp","dummy"),
		("sel_levl","dummy"),
		("sel_sess","dummy"),
		("sel_instr","dummy"),
		("sel_ptrm","dummy"),
		("sel_attr","dummy"),
		("begin_ap","x"),
		("end_ap","y"),
		("SUB_BTN","Advanced Search"),
		("sel_crse",""),
		("sel_title",""),
		("sel_from_cred",""),
		("sel_to_cred",""),
		("sel_ptrm","%"),
		("begin_hh","0"),
		("begin_mi","0"),
		("end_hh","0"),
		("end_mi","0")
	]

	params.append(("term_in",term))

	good,r = banner_post("/SSBPROD/bwskfcls.P_GetCrse", params)
	if good:
		return parse_searchform(r.text)
	else:
		return None

def banner_sectionsearch(term, subjects, num="", title="", schedules=["%"], cred_from="", cred_to="", levels=["%"], partsofterm=["%"], instructors=["%"], attrs=["%"], beginh="0", beginm="0", beginap="a", endh="0", endm="0", endap="a", days=[]):
	params = [
		("rsts","dummy"),
		("crn","dummy"),
		("sel_subj","dummy"),
		("sel_day","dummy"),
		("sel_schd","dummy"),
		("sel_insm","dummy"),
		("sel_camp","dummy"),
		("sel_levl","dummy"),
		("sel_sess","dummy"),
		("sel_instr","dummy"),
		("sel_ptrm","dummy"),
		("sel_attr","dummy"),
		("sel_crse",num),
		("sel_title",title),
		("sel_from_cred",cred_from),
		("sel_to_cred",cred_to),
		("begin_hh", beginh),
		("begin_mi", beginm),
		("begin_ap", beginap),
		("end_hh", endh),
		("end_mi", endm),
		("end_ap", endap),
		("SUB_BTN","Advanced Search"),
		("path","1"),
	]

	params.append(("term_in",term))

	to_add = {
		"sel_subj":subjects,
		"sel_schd":schedules,
		"sel_levl":levels,
		"sel_ptrm":partsofterm,
		"sel_instr":instructors,
		"sel_attr":attrs,
		"sel_day":days,
	}

	for key,source in to_add.items():
		for s in source:
			params.append((key, s))

	good,r = banner_post("/SSBPROD/bwskfcls.P_GetCrse_Advanced", params)
	if good:
		return parse_sectionlist(r.text)
	else:
		return None

##############################################################################
##############################################################################

def comp1000emails(instructors=None):
	codes = banner_sectioncodes("201710")
	schedules = {name:code for code,name in codes["schedules"].items()}

	params = {"term":"201710", "subjects":["COMP"], "num":"1000", "schedules":[schedules['Lecture']]}
	if instructors is not None:
		profs = {name:code for code,name in codes["instructors"].items()}
		params["instructors"] = [profs[p] for p in instructors]

	term = banner_termset("201710")
	sections = banner_sectionsearch(**params)
	if sections is not None:
		emails = []
		comp1000 = [s["crn"] for s in sections]
		for s in comp1000:
			print("Querying {}...".format(s))
			crn = banner_crnset(s)
			if crn is not None:
				print(" Getting students")
				students = banner_summaryclasslist()
				if students is not None:
					print(" Grabbing e-mails")
					for student in students:
						emails.append(student["email"])
	print(emails)
	print(len(emails))

def main(argv):
	if len(argv) is not 2:
		print("{} <initial session id>".format(argv[0]))

	banner_init(argv[1])

	# print(banner_mainmenu())
	# print(banner_facultymenu())
	# print(banner_termform())
	# print(banner_termset("201710"))
	# print(banner_crnform())
	# print(banner_crnset("11588"))
	# print(banner_summaryclasslist())
	# print(banner_detailclasslist())

	# print(banner_sectiontermform())
	# print(banner_sectiontermset("201710"))
	# print(banner_coursesearch("201710", ["COMP", "MATH"]))

	# comp1000emails()
	# comp1000emails(["Derbinsky, Nathaniel"])

	print(banner_lastid())

	# good,r,sid = banner_get("/SSBPROD/bwskfcls.P_GetCrse", sid)
	# if good:
	# 	print(r.text)
	# 	print(sid)
	# else:
	# 	print("sadness :(")

if __name__ == "__main__":
	main(sys.argv)
