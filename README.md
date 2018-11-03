# Logsurfer Phantom

A command-line utility for Logsurfer to send events into a Splunk-Phantom server.

NOTE: This code is currently broken - the Phantom API requres the data
to be submitted in JSON format, at the moment this code sends just
plain log lines which result in an error.

