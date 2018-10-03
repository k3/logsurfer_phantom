#!/usr/bin/python
#
# logsurfer_phantom.py
#
# A command-line utility written in Python to send events generated
# by logsurfer into Phantom
#
# Adapted from Phantom's API example code
#
# This example uses the 3rd party "requests" module.  This can be installed
# with "pip install requests" from your client machine. If requests is not
# available, any library which supports https POSTS and basic authentication
# can be used.
import os, sys, csv
import json
import requests

AUTH_TOKEN = "tuI6TaoiBv3fjtFcuQLKciCY+niZ87C2l4FLWcWQf7I="
PHANTOM_SERVER = "192.168.1.64"
ARTIFACT_LABEL = "event"

headers = {
  "ph-auth-token": AUTH_TOKEN
}

container_common = {
    "description" : "Test container added via REST API call",
}

# disable certificate warnings for self signed certificates
requests.packages.urllib3.disable_warnings()

def add_container(name, sid):
  url = 'https://{}/rest/container'.format(PHANTOM_SERVER)

  post_data = container_common.copy()
  post_data['name'] = '{} ({})'.format(name, sid)
  post_data['source_data_identifier'] = sid
  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)
  if (r is None or r.status_code != 200):
    if r is None:
      print('error adding container')
    else:
      print('error {} {}'.format(r.status_code,json.loads(r.text)['message']))
    return False

  return r.json().get('id')

def add_artifact(row, container_id):
  url = 'https://{}/rest/artifact'.format(PHANTOM_SERVER)

  post_data = {}
  post_data['name'] = 'artifact for {}'.format(row[4])
  post_data['label'] = ARTIFACT_LABEL
  post_data['container_id'] = container_id
  post_data['source_data_identifier'] = "source data primary key for artifact or other identifier"

  # The cef key is intended for structured data that can be used when
  # dealing with product agnostic apps or playbooks. Place any standard
  # CEF fields here.
  cef = {
    'sourceAddress': row[0],
    'sourcePort': row[1],
    'hash': row[2],
  }

  # The "data" key can contain arbitrary json data. This is useful for
  # keeping data that does not comfortably fit into CEF fields or is highly
  # product specific
  data = cef.copy()
  data['score'] = row[3]
  data['comment'] = row[4]

  post_data['cef'] = cef
  post_data['data'] = data

  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)

  if (r is None or r.status_code != 200):
    if (r is None):
      print('error adding artifact')
    else:
      error = json.loads(r.text)
      print('error {} {}'.format(r.status_code, error['message']))
    return False

  resp_data = r.json()
  return resp_data.get('id')

def load_data(filename):
  with open(filename, 'rb') as csvfile:
    reader = csv.reader(csvfile)
    first_row = True
    for row in reader:
      if first_row:
        # skip the header
        first_row = False
        continue
      if not row:
       continue

      container_id = add_container(row[4], row[5])
      if not container_id:
        continue
      print 'added container {}'.format(container_id)
      artifact_id = add_artifact(row, container_id)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Filename is required"
    sys.exit(-1)

  load_data(sys.argv[1])
  sys.exit(0)

