<h1 align="center">
How to build a network scanning analysis platform - Part I
</h1>
<h5 align="right">Build a distributed scan log collection system</h5>
<br/>

### [中文版](howto_CN_2.md)

## Description
In the [previous article](howto_1.md), we introduced how to build a distributed scan log collection system. Now that a lot of logs have been collected, how to obtain the desired knowledge from the logs? We need data analysis.

Recall our original goal: to find out which IPs doing scanning? Which organization these IPs belong to? What is the purpose of these organization scans?
This tutorial will introduce how to perform a simple analysis on the collected logs and
create ip analysis rules.

[Demo website](https://faweb.fofa.so/)

## Rules introduction
Because the logs collected by FaPro are scattered, every ip access request will generate a lot of logs. The log message types include tcp_syn, icmp_ping, udp_packet, and protocol interaction logs.

To analyze the behavior of a single IP, We need a way to aggregate these logs based on ip, we call it aggregation rule. These rules are implemented through elasticsearch aggregation queries, we need to write elasticsearch queries to extract the corresponding data.

How to define rules? Which dimensions of data do we want to aggregate? You need to define it yourself. Here are a few simple rules.

Summarize the ip log message by day, aggregation the number of tcp_syn visits, which ports have been visited; the number of icmp_ping visits, the ports accessed by udp_packet, and the number of visits corresponding to each port, etc.


In the next section, we will describe how to write elasticsearch queries for these rules.

## Write rules

If you are not familiar with elastic query, you can use kibana to display the corresponding chart first, and then use inpect to view the corresponding query statement to obtain the elastic query statement.

For example, aggregate query the icmp_ping times of each ip, with the help of kibana's chart:
![icmp ping count](icmp_ping_count.gif)

After obtaining the elastic query statement, convert it to python code:
```python 
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

pprint.pprint(top_ip_icmp_ping['aggregations']['ips']['buckets'])
```

However, this query is for all data, we need to query by day, and perform paginating aggregations results:
```python 
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

local_port_agg = {"ports": {"terms": {"field": "local_port",
                                      "size": 1000}}}
## get the local_port count of tcp_syn messages for each ip on 2021-10-20
ip_port_info = all_ip_count("2021-10-20", 'message.keyword:"tcp_syn"', ip_aggs = local_port_agg, page_size = 100)

pprint.pprint(ip_port_info[0])
### output result
{'doc_count': 1939, # tcp_syn message count
 'key': '94.232.47.190',
 'ports': {'buckets': [{'doc_count': 1937, 'key': 3389}, # 3389 visits 1937 times
                       {'doc_count': 2, 'key': 3390}], # 3390 visits 2 times
           'doc_count_error_upper_bound': 0,
           'sum_other_doc_count': 0}}
```

Take 94.232.47.190 as an example, it has visited ports 3389 and 3390, and now it obtains the information about whether to establish a tcp connection:
```python 
tcp_info = query("2021-10-20", 'remote_ip:"94.232.47.190" AND message.keyword:"close conn"',
                 aggs=local_port_agg,
                 size=0)

pprint.pprint(tcp_info)
{'aggregations': {'ports': {'buckets': [{'doc_count': 1937, 'key': 3389},
                                        {'doc_count': 2, 'key': 3390}],
                            'doc_count_error_upper_bound': 0,
                            'sum_other_doc_count': 0}}}
```
As you can see, ports 3389 and 3390 have carried out a tcp handshake and a connection is established.

Next, query the cookie information used by rdp to obtain further ip behavior:
```python 
rdp_cookie_agg = {"cookies": {"terms": {"field": "cookie.keyword", "size": 100}}}
rdp_cookie_info = query("2021-10-20", 'remote_ip:"94.232.47.190" AND protocol:"rdp" AND cookie:"*"',
                        aggs=rdp_cookie_agg,
                        size=0)

pprint.pprint(rdp_cookie_info)
{'aggregations': {'cookies': {'buckets': [{'doc_count': 976,
                                           'key': 'Cookie: mstshash=Administr'},
                                          {'doc_count': 4,
                                           'key': 'Cookie: mstshash=Test'}],
                              'doc_count_error_upper_bound': 0,
                              'sum_other_doc_count': 0}}}
```

示例获取ip地址为45.146.164.110的http访问信息:
```python 
http_info_agg = {"uri": {"terms": {"field": "uri.keyword", "size": 100}},
                 "user-agent": {"terms": {"field": "headers.User-Agent.keyword", "size": 100}} }
http_info = query("2021-10-20", 'remote_ip:"45.146.164.110" AND protocol:"http" AND uri:"*"',
                        aggs=http_info_agg,
                        size=0)

pprint.pprint(http_info)
{'aggregations': {'uri': {'buckets': [{'doc_count': 63, 'key': '/'},
                                      {'doc_count': 54,
                                       'key': '/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php'},
                                      {'doc_count': 30,
                                       'key': '/api/jsonws/invoke'},
                                      {'doc_count': 28,
                                       'key': '/Autodiscover/Autodiscover.xml'},
                                      {'doc_count': 28,
                                       'key': '/_ignition/execute-solution'},
                                      {'doc_count': 27,
                                       'key': '/?XDEBUG_SESSION_START=phpstorm'},
                                      {'doc_count': 27,
                                       'key': '/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'},
                                      {'doc_count': 27, 'key': '/console/'},
                                      {'doc_count': 27,
                                       'key': '/index.php?s=/Index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=md5&vars[1][]=HelloThinkPHP21'},
                                      {'doc_count': 27,
                                       'key': '/wp-content/plugins/wp-file-manager/readme.txt'},
                                      {'doc_count': 22, 'key': '/index.php'},
                                      {'doc_count': 18,
                                       'key': '/solr/admin/info/system?wt=json'},
                                      {'doc_count': 17,
                                       'key': '/?a=fetch&content=<php>die(@md5(HelloThinkCMF))</php>'},
                                      {'doc_count': 10,
                                       'key': '/mifs/.;/services/LogService'}],
                          'doc_count_error_upper_bound': 0,
                          'sum_other_doc_count': 0},
                  'user-agent': {'buckets': [{'doc_count': 405,
                                              'key': 'Mozilla/5.0 (Windows NT '
                                                     '10.0; Win64; x64) '
                                                     'AppleWebKit/537.36 '
                                                     '(KHTML, like Gecko) '
                                                     'Chrome/78.0.3904.108 '
                                                     'Safari/537.36'}],
                                 'doc_count_error_upper_bound': 0,
                                 'sum_other_doc_count': 0}}}
```

## 展示效果

将所有这些信息收集，归类到新的分析库之后，就可以对ip信息进行更高层次的分析，比如使用faweb查看[45.146.164.110](https://faweb.fofa.so/ip_detail/?ip=45.146.164.110):

![45.146.164.110](45.146.164.110.png)

可以看到45.146.164.110访问了多个协议，而没有做端口探测，因此推测它很可能是一个协议分析工具，从端口访问记录来看，随着探测到的端口增多，协议识别访问次数也增多。 从http_url来看，它尝试识别几种web应用。

再来看一个[220.174.25.172](https://faweb.fofa.so/ip_detail/?ip=220.174.25.172):

![220.174.25.172](ssh_burte_220-174-25-172.png)

可以看到这是一个ssh爆破工具，可以看到它关心哪些端口，以及每天尝试爆破的次数。

至此，通过使用elastic查询建立规则，并入库，就可以实现一个你自己的[greynoise](https://www.greynoise.io/viz/ip/45.146.164.110)

在[fapro analysis](https://faweb.fofa.so/analysis/)可以看到每天、每周、每月的ip数据量统计及相关的top信息。
![fapro ana](analysis.jpg)
