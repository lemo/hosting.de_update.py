#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
    modify dns settings for hosting.de with rest api
    https://github.com/lemo/hosting.de_update.py

"""
__author__ = "Alexander Goltz"
__copyright__ = "Copyright 2019"
__credits__ = ["Alexander Goltz"]
__license__ = "MIT"
__status__ = 'Prototype'

import sys
import string
import argparse
import json
import requests

parser = argparse.ArgumentParser()
action_group = parser.add_mutually_exclusive_group()
action_group.add_argument(
    "--update",
    action='store_const',
    dest='mode',
    const='update',
    default='update',
    help='update an entry, default mode')
action_group.add_argument("--add",
                          action='store_const', dest='mode', const='add',
                          help='add a new entry')
action_group.add_argument("--remove",
                          action='store_const', dest='mode', const='remove',
                          help='remove an existing array')
parser.add_argument("-a", "--authtoken",
                    required=True,
                    help='your authentication token from hosting.de')
parser.add_argument("-n", "--name",
                    required=True,
                    help='name to update')
parser.add_argument(
    "-z",
    "--zone",
    help='dns soa zone aka. root zone, default(last two parts of --name)')
parser.add_argument("-t", "--type",
                    required=True,
                    help='dns type e.g. A,AAAA,MX,...')
parser.add_argument("-c", "--content",
                    help='content to set, normally your ip or text')
parser.add_argument("--ttl",
                    type=int,
                    default=86400,
                    help='TTL time to live of entry, default(86400)')
parser.add_argument("-v", "--verbose",
                    action='count',
                    help='print more info')
args = parser.parse_args()
if args.verbose > 1:
    print args

if args.zone is None:
    args.zone = string.join(args.name.split(".")[-2:], '.')

if args.verbose:
    print args

payload = {
    "authToken": args.authtoken
}
headers = {'content-type': 'application/json'}

url = "https://secure.hosting.de/api/dns/v1/json/zonesFind"
if args.verbose:
    print '> ' + url
    print json.dumps(payload, indent=4)
answer = requests.post(url, data=json.dumps(payload), headers=headers)
if args.verbose:
    print '<'
    print answer.text

if answer.status_code != requests.codes.ok:
    answer.raise_for_status()
    exit_on_error()

oldRecords = []
if args.mode == 'update' or args.mode == 'remove':
    for record in json.loads(answer.text)['response']['data']:
        for e in record['records']:
            if e['name'] == args.name and e['type'] == args.type:
                if args.mode == 'remove' and args.content is not None and args.content != e[
                        'content']:
                    continue
                oldRecords.append(e)

newRecords = []
if args.mode == 'update' or args.mode == 'add':
    newRecords.append(
        {
            "name": args.name,
            "type": args.type,
            "content": args.content,
            "ttl": args.ttl
        }
    )
payload = {
    "authToken": args.authtoken,
    "zoneConfig": {
        "name": args.zone
    },
    "recordsToAdd": newRecords,
    "recordsToDelete": oldRecords
}
url = "https://secure.hosting.de/api/dns/v1/json/zoneUpdate"
if args.verbose:
    print '> ' + url
    print json.dumps(payload, indent=4)
answer = requests.post(url, data=json.dumps(payload), headers=headers)
if args.verbose:
    print '<'
    print answer.text
if answer.status_code != requests.codes.ok:
    answer.raise_for_status()
    exit_on_error()
sys.exit()


def exit_on_error():
    print 'something went wrong'
    if args.verbose == 0:
        print 'maybe increase verbosity with -v'
    sys.exit('exiting')
