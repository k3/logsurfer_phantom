#!/usr/bin/python
#
# logsurfer_phantom.py
#
# A command-line utility written in Python to send events generated
# by logsurfer into Phantom
#
# Adapted from Phantom's API example code
#
# Usage:
#   logsurfer_phantom.py severity sensitivity
#   Where:
#      severity = low|medium|high
#      sensitivity = white|green|amber|red
#   stdin: contains log lines of the event
#
#
# This example uses the 3rd party "requests" module.  This can be installed
# with "pip install requests" from your client machine. If requests is not
# available, any library which supports https POSTS and basic authentication
# can be used.
import os, sys, csv
import json
import requests

AUTH_TOKEN = "NEL9fjJ5BAUKFLH/jdlq4YAtQWaoh7+VuJawCVTV9vI="
PHANTOM_SERVER = "phantom"
ARTIFACT_LABEL = "event"

headers = {
  "ph-auth-token": AUTH_TOKEN
}

container_common = {
    "description" : "Logsurfer Container",
}

# disable certificate warnings for self signed certificates
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#
# add_container
# create a new container object in phantom
#  name = Name of event
#  sid = Event indicator ID
#
def add_container(name, sid, severity, sensitivity):
  url = 'https://{}/rest/container'.format(PHANTOM_SERVER)

  post_data = container_common.copy()
  post_data['name'] = '{} ({})'.format(name, sid)
  post_data['source_data_identifier'] = sid
  post_data['severity'] = severity
  post_data['sensitivity'] = sensitivity
  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)
  if (r is None or r.status_code != 200):
    if r is None:
      print('Error adding container')
    else:
      print('Error {} {}'.format(r.status_code,json.loads(r.text)['message']))
    return False

  return r.json().get('id')

def add_artifact(container_id, sid, stream):
  url = 'https://{}/rest/artifact'.format(PHANTOM_SERVER)

  post_data = {}
  post_data['name'] = 'Artifact for {}'.format(sid)
  post_data['label'] = ARTIFACT_LABEL
  post_data['container_id'] = container_id
  post_data['source_data_identifier'] = "source data primary key for artifact or other identifier"

  # The cef key is intended for structured data that can be used when
  # dealing with product agnostic apps or playbooks. Place any standard
  # CEF fields here.
  #cef = {
  #  'sourceAddress': row[0],
  #  'sourcePort': row[1],
  #  'hash': row[2],
  #}

  # The "data" key can contain arbitrary json data. This is useful for
  # keeping data that does not comfortably fit into CEF fields or is highly
  # product specific
  #data = cef.copy()
  #data['score'] = row[3]
  #data['comment'] = row[4]

  #post_data['cef'] = cef
  #post_data['data'] = data
  post_data['data'] = stream
  
  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)

  if (r is None or r.status_code != 200):
    if (r is None):
      print('Error adding artifact')
    else:
      error = json.loads(r.text)
      print('Error {} {}'.format(r.status_code, error['message']))
    return False

  resp_data = r.json()
  return resp_data.get('id')

#def load_data(filename):
#  with open(filename, 'rb') as csvfile:
#    reader = csv.reader(csvfile)
#    first_row = True
#    for row in reader:
#      if first_row:
#        # skip the header
#        first_row = False
#        continue
#      if not row:
#       continue
#
#      container_id = add_container(row[4], row[5])
#      if not container_id:
#        continue
#      print 'Added container {}'.format(container_id)
#      artifact_id = add_artifact(row, container_id)

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print 'Usage: {} ip_addr description'.format(sys.argv[0])
    sys.exit(-1)

  # load_data(sys.argv[1])
  sid = 'LS-{}'.format(os.getpid())
  container_id = add_container("Logsurfer", sid, sys.argv[1], sys.argv[2])
  if container_id:
    print 'Added container {}'.format(container_id)
  log_data = sys.stdin
  artifact_id = add_artifact(container_id, sid, log_data)
  if artifact_id:
    print 'Added artifact {}'.format(artifact_id)
    
  sys.exit(0)

