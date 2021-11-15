#!/usr/bin/env python3

# example elastic rule

# pip3 install elasticsearch

from datetime import datetime
from elasticsearch import Elasticsearch
import os

es_host = os.environ.get('ES_HOST')

es = Elasticsearch([es_host])

top_ip_icmp_ping = es.search(index="fapro",
                             aggs={
                                 "ips": {
                                     "terms": {
                                         "field": "remote_ip",
                                         "order": {
                                             "_count": "desc"
                                         },
                                         "size": 10 # max aggs item
                                     }
                                 }
                             },
                             size=0,
                             query={
                                 "bool": {
                                     "filter": [
                                         {
                                             "bool": {
                                                 "should": [
                                                     {
                                                         "match_phrase": {
                                                             "message.keyword": "icmp_ping"
                                                         }
                                                     }
                                                 ],
                                                 "minimum_should_match": 1
                                             }
                                         }
                                     ]
                                 }
                             })

# print ping aggs result
import pprint
pprint.pprint(top_ip_icmp_ping['aggregations']['ips']['buckets'])

def query(day, q, **kwargs):
    "query info by day"
    r = es.search(index="fapro",
                  query={"bool":
                         {"must":
                          [{"range": {"@timestamp": {"gte": day,
                                                     "lt": f'{day}||+1d/d' }}},
                           {"query_string": {"query": q}}]}},
                  **kwargs)
    return r

## test query day range
# a = query("2021-10-20", "*", size=1, sort={"@timestamp": {"order": "desc"}})
# pprint.pprint(a)
# a = query("2021-10-20", "*", size=1, sort={"@timestamp": {"order": "asc"}})
# pprint.pprint(a)

### use paged aggs
def get_total_ip(day):
    "get total ip count of day"
    r = query(day,
              "*",
              aggs={"ip_count":
                    {"cardinality":
                     {"field": "remote_ip"}}},
              size=0)
    return r['aggregations']['ip_count']['value']

import math
def all_ip_count(day, q, ip_aggs=None, page_size=1000):
    "get all ip count info by day"
    res = []
    total = get_total_ip(day)
    page = math.ceil(total / page_size)
    for i in range(page):
        aggs = {"ips": {"terms": {"field": "remote_ip",
                                  "include": {"partition": i,
                                              "num_partitions": page},
                                  "size": page_size}}}
        if ip_aggs:
            aggs['ips']['aggs'] = ip_aggs
        r = query(day, q, aggs = aggs, size=0)
        res += r['aggregations']['ips']['buckets']
    return res

## get count of icmp_ping messages for each ip on 2021-10-20
ping_info = all_ip_count("2021-10-20", 'message.keyword:"icmp_ping"')

## get count of tcp_syn messages for each ip on 2021-10-20
syn_info = all_ip_count("2021-10-20", 'message.keyword:"tcp_syn"')

## get the local_port count of tcp_syn messages for each ip on 2021-10-20
local_port_agg = {"ports": {"terms": {"field": "local_port",
                                      "size": 1000}}}
ip_port_info = all_ip_count("2021-10-20", 'message.keyword:"tcp_syn"', ip_aggs = local_port_agg, page_size = 100)

## get tcp conn info for 94.232.47.190 on 2021-10-20
tcp_info = query("2021-10-20", 'remote_ip:"94.232.47.190" AND message.keyword:"close conn"',
                 aggs=local_port_agg,
                 size=0)


## get rdp cookie info for 94.232.47.190 on 2021-10-20
rdp_cookie_agg = {"cookies": {"terms": {"field": "cookie.keyword", "size": 100}}}
rdp_cookie_info = query("2021-10-20", 'remote_ip:"94.232.47.190" AND protocol:"rdp" AND cookie:"*"',
                        aggs=rdp_cookie_agg,
                        size=0)

## get http uri and user-agent info for 45.146.164.110 on 2021-10-20
http_info_agg = {"uri": {"terms": {"field": "uri.keyword", "size": 100}},
                 "user-agent": {"terms": {"field": "headers.User-Agent.keyword", "size": 100}} }
http_info = query("2021-10-20", 'remote_ip:"45.146.164.110" AND protocol:"http" AND uri:"*"',
                        aggs=http_info_agg,
                        size=0)

