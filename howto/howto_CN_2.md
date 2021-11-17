
<h1 align="center">
如何打造一个网络扫描分析平台 - Part II
</h1>
<h5 align="right">如何分析扫描日志</h5>
<br/>

### [English version](howto_2.md)

## 简介
在[上一篇](howto_CN_1.md)我们介绍了如何搭建分布式网络扫描日志收集系统, 现在已经收集了大量的日志，如何从日志中获取想要的知识？需要进行数据分析，提出一个问题，然后从数据中去寻找答案。

我们尝试着从数据中回答一些问题：

- 每天有多少ip在进行扫描？
![ip count by day](./ip_count_by_day.jpg)

- 那么进行大范围ip扫描的数量趋势呢？
![ip count by breadth gt 1](./breadth_gt_1_ips_by_day.jpg)

- 再来看看censys每天扫描的ip数量是多少？
![censys ip by day](./censys_count_by_day.jpg)

- censys每天进行大范围扫描的ip数量是多少？
![censys massive scanner by day](./censys_massive_count_by_day.jpg)

- shodan进行扫描的ip数量是多少？
![shodan scanner by day](./shodan_count_by_day.jpg)

- shodan进行大范围扫描的ip数量呢？
![shodan massive scanner by day](./shodan_massive_count_by_day.jpg)

- binaryedge进行扫描的ip数量是多少？
![binaryedge scanner by day](./binaryedge_count_by_day.jpg)

- binaryedge大范围扫描的ip数量？
![binaryedge massive scanner by day](./binaryedge_massive_count_by_day.jpg)

- rapid7是怎么进行扫描的？
![rapid7 scanner by day](./rapid7_count_by_day.jpg)

- 这些ip都在关心哪些端口？来自哪个国家？扫描范围有多广？访问了哪些服务？
![ip summary](./summary.jpg)
可以在[faweb](https://faweb.fofa.so/analysis/)上查看


- 再以端口为线索，大范围扫描器都在关心哪些端口？ 
![masser scanner port](./port_breadth_b5_ports.jpg)
能看到大部分都集中在10000端口以下。 后面的27017、49152端口访问数量也比较大，我们来找找原因。

在[faweb中搜索port:27017](https://faweb.fofa.so/result/?word=port%3A27017),能看到有2000多条结果，
27017是mongodb的常用端口，因此各家的互联网扫描引擎也比较关注。
再看看关心27017端口的ip还会关心哪些端口:
![related 27017](./port_27017_result.jpg)

基本上是互联网扫描器会关心的常见服务端口。

来看下其中的一个ip:
![27017 detail ip](./port_27017_ip.jpg)
它是recyber的一个扫描器。再看其它几个ip也是扫描器的行为。

再看看[port:49152](https://faweb.fofa.so/result/?word=port%3A49152), 看看其中一个ip:
![167.248.133.18](./167.248.133.18.png)
看rdns信息，应该是censys的ip地址，再看看它关心的端口列表，找几个端口,比如50995, 20201, 40000, 17777, 47001, 49152,来看看各个互联网扫描平台上有多少条独立ip的收录:

| 平台               |     50995 |     20201 | 40000     |   17777 |     47001 | 49152      |
| shodan             |         2 |        43 | 39        |       4 |         4 | 1,488,551  |
| censys             | 1,083,024 | 2,722,622 | 1,748,078 | 311,021 | 2,827,492 | 2,054,990  |
| fofa.so            |         1 |        82 | 1,280,784 |      26 |        39 | 5,497,110  |
| zoomeye.org        |         0 |         0 | 2,018,912 |       0 |         0 | 5,762,264  |
| quake.360.cn       |         7 |        18 | 47        |       2 |       483 | 3,546,927  |

下面来介绍如何对收集到的原始日志进行简单的分析，并创建规则来提供更高层次的数据以回答上面这些问题。
    
## 规则介绍
因为FaPro收集的日志是分散的，每个ip的访问请求会分散为很多条日志，目前主要的日志种类有tcp_syn, icmp_ping, udp_packet,以及协议交互的日志。

针对单个ip的行为分析，就需要把这些分散的日志按照一定的规则进行聚合，如何定义规则？我们想看到哪些维度的数据？就需要自己去分析，这里介绍几种简单的规则。

首先根据时间段对ip的日志数据进行汇总，比如tcp_syn访问次数，访问了哪些端口; icmp_ping访问次数，udp_packet访问的端口，及每个端口对应的访问次数等，为了方便，这里统一按天进行归类。

## 编写规则
如果对elastic查询不熟悉，可以先借助kibana查询相应的图表，再使用inpect查看相应的查询语句，来获取elastic查询。

比如统计查询每个ip的icmp_ping次数，借助kibana的图表功能:
![icmp ping count](icmp_ping_count.gif)

获取elastic查询语句后，把它转换为python代码:
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

不过这个查询的是所有日期的数据，我们需要按天查询，并且对聚合结果进行分页查询，防止一次查询的数据过多，超过elastic的限制:
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

## 获取2021-10-20的每个ip的icmp_ping消息计数
ping_info = all_ip_count("2021-10-20", 'message.keyword:"icmp_ping"')

## 获取2021-10-20的每个ip的tcp_syn消息计数
syn_info = all_ip_count("2021-10-20", 'message.keyword:"tcp_syn"')

local_port_agg = {"ports": {"terms": {"field": "local_port",
                                      "size": 1000}}}

## 获取2021-10-20的每个ip的tcp_syn消息的本地端口计数 (即这个ip通过tcp syn访问了本地端口多少次)
ip_port_info = all_ip_count("2021-10-20", 'message.keyword:"tcp_syn"', ip_aggs = local_port_agg, page_size = 100)

pprint.pprint(ip_port_info[0])
### 输出结果
{'doc_count': 1939, # tcp_syn消息次数
 'key': '94.232.47.190',
 'ports': {'buckets': [{'doc_count': 1937, 'key': 3389}, # 3389访问了1937次
                       {'doc_count': 2, 'key': 3390}], # 3390访问了2次
           'doc_count_error_upper_bound': 0,
           'sum_other_doc_count': 0}}
```

以94.232.47.190为例，访问了3389和3390端口,现在获取是否建立tcp连接信息:
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
可以看到，3389和3390的端口进行了tcp握手，建立了连接。

接下来，查询rdp访问使用的cookie信息，以获取更进一步的行为:
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

# 结语

至此，已经完成了初步的规则分析以及数据探索。更深入的行为分析，扫描意图识别还需要更多工作要做，敬请期待第三篇。
