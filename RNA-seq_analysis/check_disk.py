#!/usr/bin/env python

import requests
import json
import sys
import time

comment = 'WARNING: Disk usage over 90% !!'
limit = 90

counter = 1
for line in open(sys.argv[1], 'r'):
    line = line.rstrip()
    data = line.split()
    if counter == 12:
        test = int(data[4].split("%")[0])
        if test > limit:
            requests.post('https://hooks.slack.com/services/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',
            data = json.dumps({
                'text': comment,
                'username': u'NGS Bot',
                'icon_emoji': u':space_invader:',
                'link_names': 1,
            }))
            time.sleep(600)
    counter += 1
