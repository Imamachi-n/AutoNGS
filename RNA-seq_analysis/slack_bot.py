import requests
import json
import sys

comment = ""
if len(sys.argv) >= 2:
    comment = sys.argv[1]
else:
    comment = 'Task was successfully finished !!'

requests.post('https://hooks.slack.com/services/<hogehoge>',
data = json.dumps({
    'text': comment,
    'username': u'NGS Bot',
    'icon_emoji': u':space_invader:',
    'link_names': 1,
}))
