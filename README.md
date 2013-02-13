obs_tool
========

A tool to assist in planning astronomical observing sessions.

Given a list of targets and an observing scenario, obstool calculates elevation, transit time, lunar separation, and a number of other useful factors. 

This is particularly helpful when making reservation to take ccd imagery on remote telescopes such as itelescope.net. 

Usage: 

1. Create an observing plan file. See "example.txt" for the format.
2. Edit control.conf to include your observing scenario.  This includes your location, the time and date, and the location of your observing plan file.
3. Run your scenario by typing "./obstool.py scenario_name"
