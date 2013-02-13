#!/usr/bin/python

#  obs_tool.py
#  	A tool to help plan ccd imaging sessions	
#  	by R. C. Altenburg
#
#	Requires PyEphem http://rhodesmill.org/pyephem/
#
#
import ephem, math, datetime, re, argparse, sys
import ConfigParser  # renamed configparser in Python 3

# command line
parser = argparse.ArgumentParser(
	description='''Analyzes an iTelescope.net observing plan file to
				help determine the best time to image a target.''')
parser.add_argument('scenario', nargs='?', default='DEFAULT')
args = parser.parse_args()

# get all the necessary data from the configuration file
config = ConfigParser.RawConfigParser()
config.read('control.conf')
observer_latitude = config.get(args.scenario, 'latitude')
observer_logitude = config.get(args.scenario, 'logitude')
observer_elevation = config.getfloat(args.scenario, 'elevation')
observer_timezone = config.getint(args.scenario, 'timezone')
observer_tz_text = config.get(args.scenario, 'tz_text')
observer_local_time =  config.get(args.scenario, 'local_time')
target_list = config.get(args.scenario, 'target_list')

if observer_local_time == 'now':
	observer_local_time = ''


# Default observing target file
#target_list = 'yso_targets.txt'  # could be sys.stdin


# pyEphem uses UT, so this is a helper routine to use local time
def ut_to_local_string (ut):
	return "%s %s" %(ephem.Date(ut + (observer_timezone * ephem.hour)), observer_tz_text)

# This tool reads iTelescope.net plan format "Target[tab]RA[tab]DEC" 
def plan_to_ephem (in_string):
	data = in_string.rstrip().split("\t")
	return ephem.readdb("%s,f|V,%s,%s,-999"%(data[0],data[1],data[2]))
	
# Read an iTelescope.net plan file and select only those lines begining with an alphanumeric character	
def load_targets (in_file):
	result = []
	f = open(in_file,'r')
	for line in f:
		if re.match("^\w",line):
			result.append(line.rstrip())
	f.close()
	return result

# Where the magic happens...
def process_plan (target_list, time_string=''):
	#declare observing sites
	observatory = ephem.Observer()
	observatory.lat = observer_latitude
	observatory.lon = observer_logitude
	observatory.elev = observer_elevation
	observatory.pressure = 0

	if time_string != '':
		observatory.date = ephem.Date(time_string)- (observer_timezone * ephem.hour)

	moon = ephem.Moon()
	moon.compute(observatory)

	###### Reporting Section

	print "Report for: %s " %(ut_to_local_string(observatory.date))
	print "---------------------------------" 

	observatory.horizon = '-18'
	moon_days = observatory.date - ephem.previous_new_moon(observatory.date)
	print "Astronomical twilight:\n\tNext ending: %s" %(ut_to_local_string(observatory.next_setting(ephem.Sun(),use_center=True)))
	print "\tNext beginning: %s" %(ut_to_local_string(observatory.next_rising(ephem.Sun(),use_center=True)))
	print "Moon age: %3.2f days -- Ilumination: %3.1f%%" % (moon_days, moon.phase)
	observatory.horizon = '0'
	print "---------------------------------\n"

	for target in target_list:
	
		varstar = plan_to_ephem(target)
		varstar.compute(observatory)

		print "Target: %s" %(varstar.name)
		try:
			print "Altitude: %3.2f" % (math.degrees(varstar.alt))
			print "Next rise: %s" % (ut_to_local_string(observatory.next_rising(varstar)))
			print "Next set: %s" % (ut_to_local_string(observatory.next_setting(varstar)))
		except ephem.AlwaysUpError:
			print "Object is circumpolar"
		except ephem.NeverUpError:
			print "*** Transit is below horizon ***"
		transit = observatory.next_transit(varstar)	
		print "Next transit: %s " % (ut_to_local_string(transit))
		temp_date = observatory.date
		observatory.date = transit
		varstar.compute(observatory)
		moon.compute(observatory)
		print "Transit altitude: %3.2f deg" % (math.degrees(varstar.alt))
		print "Lunar separation: %s" % (ephem.separation(varstar, moon))
		observatory.date = temp_date
		print "\n"
	
###### Main

t_list = load_targets(target_list)
if len(t_list) >= 1:
	if observer_local_time == '':
		process_plan(t_list)
	else:
		process_plan(t_list, observer_local_time)
	
	
	
