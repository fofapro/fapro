
<h1 align="center">
<img src="docs/fapro.png" alt="" width="32" height="32"/>
  FaPro
  <br>
</h1>

<h5 align="center">免费、跨平台、单文件部署的网络协议服务端模拟器</h5>

![platform](https://img.shields.io/badge/platform-cross-important?color=%23189000)
[![latest release version](https://img.shields.io/github/v/release/fofapro/fapro)](https://github.com/fofapro/fapro/releases)
[![discord](https://img.shields.io/discord/891889408524038155?label=discord&logo=Discord&color=blue)](https://discord.gg/Eaz9dzV4AP)

## [README of English](README.md)

## 简介

FaPro是一个服务端协议模拟工具,可以轻松启停多个网络服务。

目标是支持尽可能多的协议，每个协议尽可能提供深度的交互支持。

[示例网站](https://faweb.fofapro.com/)

## 特性

- 支持的运行模式
  - [x] 本地模式
  - [x] 虚拟网络
- 支持的网络协议
  - [x] DNS
  - [x] DCE/RPC
  - [x] EIP
  - [x] Elasticsearch
  - [x] FTP
  - [x] HTTP
  - [x] IEC 104
  - [x] Memcached
  - [x] Modbus
  - [x] MQTT
  - [x] MySQL
  - [x] RDP
  - [x] Redis 
  - [x] S7 
  - [x] SMB
  - [x] SMTP
  - [x] SNMP
  - [x] SSH 
  - [x] Telnet 
  - [x] VNC
  - [x] IMAP
  - [x] POP3
  - [x] NTP
  - [x] RTSP
  - [x] PORTMAP
  - [x] PostgreSQL
  - [x] SIP
  - [x] SSDP
  - [x] BACnet
  - [x] Oracle TNS
  - [x] AMQP
  - [x] NFS
  - [x] COAP
  - [x] WEMO
  - [x] DHT
  - [x] Ethereum
  - [x] SOCKS5 
  - [x] EOS.IO
  - [x] ONVIF
  - [x] NetBIOS
  - [x] WebLogic
  - [x] ICAP
  - [x] MSSQL
  - [x] LDAP
  - [x] IKE
  - [x] Fox
  - [x] DNP3
  - [x] OMRON
  - [x] GE-SRTP
  - [x] MongoDB
  - [x] Java-RMI
  - [x] PCWorx
  - [x] Cassandra
  - [x] RedLion-Crimson3
  - [x] PPTP
  - [x] L2TP
  - [x] Melsecq-discover
  - [x] Winbox

- 使用TcpForward进行端口转发
- 支持tcp syn请求记录
- 支持ping请求记录
- 支持udp数据包记录
- 支持SSL ja3指纹
- 支持ip限速控制

## 协议模拟演示
### Rdp
支持 credssp ntlmv2 nla 认证。

支持配置用户登陆时的图片。
![RDP demo](docs/rdp.gif)

### SSH 
支持用户登陆。
支持部分终端命令，比如id、uid、whoami等。

账户格式: username:password:home:uid
![SSH demo](docs/ssh.gif)

### IMAP & SMTP 
支持用户登陆并进行交互。

![IMAP & SMTP demo](docs/imap_smtp.gif)

### Mysql 
支持sql语句查询交互。

![Mysql demo](docs/mysql.gif)

### FTP 
支持用户登陆并进行交互。

![Ftp demo](docs/ftp.gif)

### Oracle and BACnet
当前只支持nmap指纹欺骗

![tns and BACnet demo](docs/oracle_bacnet.gif)

### Telnet
支持登录与交互

![Telnet demo](docs/telnet.gif)

### Redis 
支持登录与交互

![Redis demo](docs/redis.gif)

### Elasticsearch
支持基本信息

![Elasticsearch demo](docs/elasticsearch.gif)

### AMQP 
支持登录与交互

![AMQP demo](docs/amqp.gif)

### COAP 
当前只支持nmap指纹欺骗

![COAP demo](docs/coap.gif)

### HTTP
支持网站克隆。
需要安装chrome浏览器和[chrome driver](https://chromedriver.chromium.org/downloads)才能使用。

## 使用指南

### 生成配置
可以使用genConfig子命令生成所有协议和参数的配置文件。
   
使用172.16.0.0/16子网生成配置文件:
```shell 
fapro genConfig -n 172.16.0.0/16 > fapro.json
```

或者使用本机地址，不创建虚拟网络:
```shell 
fapro genConfig > fapro.json
```

只创建ssh协议的配置:
```shell 
./fapro genConfig -p ssh
```

### 运行协议模拟器
使用Verbose模式运行FaPro, 并在8080端口启动web服务:
```shell
fapro run -v -l :8080
```

### Tcp syn记录
对于windows用户，请先安装[winpcap](https://www.winpcap.org/install/)或[npcap](https://nmap.org/npcap/)。


## 日志分析
使用ELK分析协议日志，例如:
![FaPro Kibana](docs/FaProLogs.jpg)


## 配置文件
配置文件的简单介绍:

```json
{
     "version": "0.65",
     "network": "127.0.0.1/32",
     "network_build": "localhost",
     "storage": null,
     "geo_db": "/tmp/geoip_city.mmdb",
     "hostname": "fapro1",
     "use_logq": true,
     "cert_name": "unknown",
     "syn_dev": "any",
     "udp_dev": "any",
     "icmp_dev": "any",
     "limiter": {
         "period": 10,
         "count": 3,
         "block_period": 20
     },
     "exclusions": [],
     "hosts": [
         {
             "ip": "127.0.0.1",
             "handlers": [
                 {
                     "handler": "dcerpc",
                     "port": 135,
                     "params": {
                         "accounts": [
                             "administrator:123456",
                         ],
                         "domain_name": "DESKTOP-Q1Test"
                     }
                 }
             ]
         }
     ]
}
```

 - version: 配置文件版本号
 - network: 虚拟网络使用的子网，或者本机模式下绑定的ip地址
 - network_build: 网络模式(支持: localhost, all, userdef)
   - localhost: 本地模式，所有服务在本机监听
   - all: 创建虚拟网络中的所有主机(子网中的所有主机都可以ping通)
   - userdef: 只创建hosts配置中指定的主机
 - storage: 指定日志收集的存储, 支持sqlite, mysql, elasticsearch. 示例:
   - sqlite3:logs.db
   - mysql://user:password@tcp(127.0.0.1:3306)/logs
   - es://http://username:password@127.0.0.1:9200  (目前只支持Elasticsearch v7.x)
 - geo_db: MaxMind geoip2数据库的文件路径, 用于生成ip地理位置信息. 如果使用了Elasticsearch日志存储,则不需要此字段，将会使用Elasticsearch自带的geoip生成地理位置。
 - hostname: 指定日志中的host字段。
 - use_logq: 使用基于本地磁盘的消息队列保存日志，然后发送到远程mysql或Elasticsearch,防止日志丢失。
 - cert_name: 指定生成证书的公共名。
 - syn_dev: 指定捕获tcp syn包使用的网卡，如果为空则不记录tcp syn包。在windows上，网卡名称类似于 "\Device\NPF_{xxxx-xxxx}"。
 - udp_dev: 与syn_dev相同，记录udp数据包。
 - icmp_dev: 与syn_dev相同，记录icmp ping数据包。
 - limiter: ip限速配置,在指定时间段内(period)访问超过设定的次数(count)则封禁指定的时间(block_period)。
   - period: ip限制访问的时间段(单位为分钟)
   - count: ip在时间段内访问的最大次数
   - block_period: 超过ip访问限制后的封禁时间(单位为分钟)
 - exclusions: 从日志记录中排除指定的remote ip。
 - hosts: 主机列表，每一项为一个主机配置
 - handlers: 服务列表，每一项为一个服务配置
 - handler: 服务名(协议名)
 - params: 设置服务支持的参数
 
### 示例
使用子网172.16.0.0/24创建一个虚拟网络，包含2个主机:

172.16.0.3 运行dns、ssh服务

172.16.0.5 运行rpc、rdp服务

协议访问日志保存到elasticsearch，排除远程ip为127.0.0.1和8.8.8.8的日志。
```json
{
    "version": "0.65",
    "network": "172.16.0.0/24",
    "network_build": "userdef",
    "storage": "es://http://127.0.0.1:9200",
    "use_logq": true,
    "cert_name": "unknown",
    "syn_dev": "any",
    "udp_dev": "any",
    "icmp_dev": "any",
    "exclusions": ["127.0.0.1", "8.8.8.8"],
    "geo_db": "",
    "hosts": [
        {
            "ip": "172.16.0.3",
            "handlers": [
               {
                    "handler": "dns",
                    "port": 53,
                    "params": {
                        "accounts": [
                            "admin:123456"
                        ],
                        "appname": "domain"
                    }
                },
                {
                    "handler": "ssh",
                    "port": 22,
                    "params": {
                        "accounts": [
                            "root:5555555:/root:0"
                        ],
                        "prompt": "$ ",
                        "server_version": "SSH-2.0-OpenSSH_7.4"
                    }
                }
            ]
        },
        {
            "ip": "172.16.0.5",
            "handlers": [
                {
                    "handler": "dcerpc",
                    "port": 135,
                    "params": {
                        "accounts": [
                            "administrator:123456"
                        ],
                        "domain_name": "DESKTOP-Q1Test"
                    }
                },
                {
                    "handler": "rdp",
                    "port": 3389,
                    "params": {
                        "accounts": [  
                            "administrator:123456"
                        ],
                        "auth": false,
                        "domain_name": "DESKTOP-Q1Test",
                        "image": "rdp.jpg",
                        "sec_layer": "auto"
                    }
                }
            ]
        }
    ]
}

```

### 一键克隆ip服务配置

使用[脚本](scripts/README-CN.md)中的ipclone.py脚本，可以实现从[fofa](https://fofa.so)中克隆ip服务配置，快速生成真实设备的服务配置。

![fofa_clone](docs/fofa_clone.gif)

## 学习更多
- [如何打造一个网络扫描分析平台 - Part I](./howto/howto_CN_1.md)
- [如何打造一个网络扫描分析平台 - Part II](./howto/howto_CN_2.md)
- [如何使用FaPro批量模拟设备](./howto/rule.md)
- [Discord](https://discord.gg/Eaz9dzV4AP)

## 常见问题
我们收集了一些[常见问题](FAQ.md). 报告issue前，请先看看常见问题集中是否有你要找的答案。

## 贡献
* 欢迎提issue。
  

