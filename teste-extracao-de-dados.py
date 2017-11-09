#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 08:28:05 2017

@author: vitor
"""
#!/usr/env python
# -*- coding: utf-8 -*-
import twitter
import pprint

api = twitter.Api(consumer_key='ZKRIOBv9D0dfIiKm8ipSnrXi9',
                      consumer_secret='B7w6zr1gBBelWGNrmpEdB8lfnUZBSmeCLNeU7xdQjcY3LR4VQe',
                      access_token_key='291980403-6TwbXCN2IS2Iuvudt10tW88LN5p2UjgDvix3A9ik',
                      access_token_secret='LzFyaSrE1sIRKZ1OI4Yhb8ry9adXGeFFKM5sTyyhooQzJ')

api.VerifyCredentials()
    # <twitter.user.User object at 0x02EE5EF0> 
	
status_list = api.GetSearch(
	geocode=None, term=u"ladrão", since_id=None,
	lang='pt', count=10, result_type='recent'
)

print(status_list)
# [<twitter.status.Status object at 0x03078AF0>, <twitter.status.Status object at 0x03078B90>, <twitter.status.Status object at 0x03078C50>, <twitter.status.Status object at 0x03078D30>, <twitter.status.Status object at 0x03078D90>, <twitter.status.Status object at 0x03078DF0>, <twitter.status.Status object at 0x03078E50>, <twitter.status.Status object at 0x03078F10>, <twitter.status.Status object at 0x03078F70>, <twitter.status.Status object at 0x03088030>] 

help(twitter.Status)

status_list[0].GetText()
# u’RT @PandaRcds: @edmilsonpapo10 @OThereza MAIS UMA DAS MENTIRAS DO LULA LADR\xc3O DO BRASIL!’ 

hashtags = dict()

for status in status_list:
	status_hashtags = status.hashtags
	for hash in status_hashtags:
		if hashtags.get(hash.text) is None:
			hashtags[hash] = 1
		else:
			hashtags[hash] += 1 

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(hashtags)

