<h1 align="center">
How to build a network scanning analysis platform - Part II
</h1>
<h5 align="right">How to analyze internet scan logs</h5>
<br/>

### [中文版](howto_CN_2.md)

## Description
In the [previous article](howto_1.md), we introduced how to build a distributed scan log collection system. Now that a lot of logs have been collected, how to obtain the desired knowledge from the logs? We need data analysis, ask a question, then find the answer from the data.

We try to answer some questions from the data statistics:

- How many IPs scanning the network every day?
![ip count by day](./ip_count_by_day.jpg)

It can be seen that from 2021–10–15, an average of 20,000 IPs are doing network scanning every day.

- The trend of IPs numbers who scan a a wide range of network.
![ip count by breadth gt 1](./breadth_gt_1_ips_by_day.jpg)
There are about 7,000 IPs doing massive scans every day.

- Look at the distribution of the number of scanner IPs by several Internet scanners:
![scanners](./scanners.png)
The data above shows that Censys scans nearly 280 IP addresses every day, and about 180 IP addresses are scanning a wide range. Shodan has 35 IPS being scanned every day, with an average of 25 IPS are scanning a wide range every day. Binaryedge is relatively unstable, with about 50 IP addresses and 10 IP addresses doing massive scanning.

- Let’s take a look at how Rapid7 doing scanning?
![rapid7 scanner by day](./rapid7_count_by_day.jpg)
The scanning strategy is a bit special; you can see that there will be a week of rest in the middle, and then suddenly, a large number of IPs are added for scanning.

- How is the scan breadth distributed in a day?
![scan breadth](./count_by_breadth.jpg)
The data above shows that most IPs have a relatively small coverage (number of hosts covered) in a day.
The scanning range of 60% and 70% is less than 100%. That is to say, the number of IPs in the middle and upper scanning range is relatively small, and most Internet scanners will scan all or limit a smaller target range.
It may also be that the scanner has limited capabilities or resources. So it’s either lightweight and faster to scan the entire network or slower but with more port or protocol identification.

- How many ports are scanned by IP in a day?
![port total by ip count](./port_total_by_ip_count.jpg)
Most IPs scan only a small number of ports in a day, and the number of IPs that scan more than 80 ports is minimal.

- Which ports do these IPs care about? Where are they from? How wide is the scanning range? Which protocols were accessed?
![ip summary](./summary.jpg)
You can view it on [faweb](https://faweb.fofa.so/analysis/)

- Using ports as clues, which ports are the massive scanners caring about?
![masser scanner port](./port_breadth_b5_ports.jpg)
The table above shows that most of the data is concentrated under port 10000. Port 27017 and 49152 have a relatively large number of visits. Let's find out why.

Search for [port:27017](https://faweb.fofa.so/result/?word=port%3A27017), you can see more than 2000 results, 27017 is a common port of MongoDB, so various Internet scanners are also paying attention.

Let's take a look at the IP that cares about port 27017, which ports will also be concerned:

![related 27017](./port_27017_result.jpg)

It is a common service port that Internet scanners will focus on it.

Lets take a look one of them's details:

![27017 detail ip](./port_27017_ip.jpg)

It is a Recyber scanner. Let's look at the behavior of several other IPs that are also scanners.

Let us focus [port:49152](https://faweb.fofa.so/result/?word=port%3A49152) again, choose an IP:
![167.248.133.18](./167.248.133.18.png)
By looking at the rdns information, you can determine that it should be the IP address of Censys. Look at the list of ports it cares about, find a few port composition samples, such as 50995, 20201, 40000, 17777, 47001, 49152; let's see how many independent IPs are included on each Internet scanning platform:

| port number/platform |     50995 |     20201 | 40000     |   17777 |     47001 | 49152     |
| ----                 |      ---- |      ---- | ----      |    ---- |      ---- | ----      |
| shodan               |         2 |        43 | 39        |       4 |         4 | 1,488,551 |
| censys               | 1,083,024 | 2,722,622 | 1,748,078 | 311,021 | 2,827,492 | 2,054,990 |
| fofa.so              |         1 |        82 | 1,280,784 |      26 |        39 | 5,497,110 |
| zoomeye.org          |         0 |         0 | 2,018,912 |       0 |         0 | 5,762,264 |
| quake.360.cn         |         7 |        18 | 47        |       2 |       483 | 3,546,927 |

This tutorial will introduce a simple analysis of the collected logs and create rules to provide higher-level data to answer these questions.

## Rules introduction
Elasticsearch has about 100G of logs for a month. Analyzing raw data directly in Elasticsearch will put a lot of pressure on elastic. The speed will be relatively slow, and doing complex aggregation queries will also exceed the various (bucket, request size, etc.) limits of Elasticsearch.

The logs collected by FaPro are also scattered. Because Fapro will spread the access request of each IP into many Logs, it is very inefficient to do an aggregate query from the original data and then analyze it. Therefore, it is necessary to establish an intermediate analysis library to aggregate the original logs according to periods and aggregate the behavior of a single IP according to specific rules.

We choose to aggregate the information of each IP by day, save it to the analysis database, and then analyze it. So what data should be stored in this database? What information will be aggregated? How to deal with this information? We call it a rule. How to define a rule? You need to analyze the definition yourself. Which dimensions of data do you want to see? Here are a few simple rule attributes.

The main log types are tcp_syn, icmp_ping, udp_packet, and protocol interaction logs, classified and summarized according to the information obtained from these types of Logs.

A list of fields that summarize the log data of IP according to the period:

- port: All ports accessed by day
- icmp_ping: The total number of all icmp ping messages accessed every day
- port_count: The total number of all ports accessed daily
- tcp_port: All tcp ports accessed every day
- udp_port: All udp ports accessed every day
- **scan_breadth**: Score the target range of the ip scanned every day as 1-10. For example, if there are 30 FaPro scan log collectors, it is (the number of hosts accessed in this ip day / 30) * 10
- http_url: List of URLs accessed by http
- http_user_agent: List of useragents accessed by http
- mysql_login_attempts: Number of login attempts for mysql protocol

Rules can define more fields. You can define some tags based on the protocol interaction log or define a series of indicators such as frequency and scope to facilitate subsequent analysis tasks.

In the next section, we will describe how to write Elasticsearch queries for these rules.

## Write rules

If you are not familiar with Elastic query, you can use Kibana to display the corresponding chart first, and then use inpect to view the corresponding query statement to obtain the elastic query statement.

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

However, this query is for all data; we need to query by day and perform paginating aggregations results to prevent too much data in one query, exceeding the Elasticsearch limit:
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
 'ports': {'buckets': [{'doc_count': 1937, 'key': 3389}, # port 3389 visits 1937 times
                       {'doc_count': 2, 'key': 3390}], # port 3390 visits 2 times
           'doc_count_error_upper_bound': 0,
           'sum_other_doc_count': 0}}
```

Take 94.232.47.190 as an example, it has visited ports 3389 and 3390, and now it obtains the information about whether to establish a TCP connection:
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
As you can see, ports 3389 and 3390 have carried out a TCP handshake and a connection is established.

Next, query the cookie information used by RDP to obtain further IP behavior:
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


Example to obtain the http access information with the IP address of 45.146.164.110:
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

Then apply these rules to query all IPs in a day in turn, and then put the final result into the analysis database.

In our [initial implementation](https://github.com/fasensor/faproana), we used Elasticsearch to store the analysis results of FaPro's original logs. However, the aggregation query speed is very slow, and it is not very convenient for historical data processing.

Then switch to  [xtdb](https://xtdb.com/), a bitemporal database, which can better process time history, but the learning curve of Datalog query syntax is higher, and the performance is not that good. To scale, using kafka+postgres as the back-end to store transactions and documents also increases the IT operational costs, and the API support for various languages ​​is also relatively weak.

Finally, we switch to  [clickhouse](https://clickhouse.com/), a database specially designed for OLAP. It can realize efficient aggregation queries, more general SQL syntax, more convenient service configuration, lower IT operation and maintenance cost, and perfect query performance. The efficiency is very high for direct batch insertion of data gathered for a day, and the API support in various languages ​​is also good.


## Visualization of results

After collecting all the IP information and categorizing it into the new analysis database, you can perform higher-level analysis of IP information, such as using Faweb to view [45.146.164.110](https://faweb.fofa.so/ip_detail/?ip=45.146.164.110):

![45.146.164.110](45.146.164.110.png)

The data shows that 45.146.164.110 accessed multiple protocols without port scan, so it is speculated that it may be a protocol analysis tool. From the ports and protocol line charts, the number of protocol identification accesses increases as the detected ports increases. From the http_url list, it tries to identify several web applications.

Let’s look at another IP [220.174.25.172](https://faweb.fofa.so/ip_detail/?ip=220.174.25.172):

![220.174.25.172](ssh_burte_220-174-25-172.png)

The data shows that this is an SSH brute force tool. You can see which ports it cares about and the number of login attempts per day.

At this point, using the Elasticsearch query to create rules and store results in the analysis database, you can implement your [greynoise](https://www.greynoise.io/viz/ip/45.146.164.110).

## Conclusion

In the end, we have completed the creation of some rules and saved the intermediate results as an analysis database and some data exploration for the analysis database. More work needs to be done for more in-depth behavior analysis, scanning intent recognition, etc., so stay tuned for the third article.
