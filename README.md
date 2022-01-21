
<h1 align="center">
<img src="docs/fapro.png" alt="" width="32" height="32"/>
  FaPro
  <br>
</h1>

<h5 align="center">Free,Cross-platform,Single-file mass network protocol server simulator</h5>

![platform](https://img.shields.io/badge/platform-cross-important?color=%23189000)
[![latest release version](https://img.shields.io/github/v/release/fofapro/fapro)](https://github.com/fofapro/fapro/releases)
[![discord](https://img.shields.io/discord/891889408524038155?label=discord&logo=Discord&color=blue)](https://discord.gg/Eaz9dzV4AP)

## [中文Readme](README-CN.md)

## Description 

FaPro is a Fake Protocol Server tool, Can easily start or stop multiple network services.

The goal is to support as many protocols as possible, and support as many deep interactions as possible for each protocol.

[Demo Site](https://faweb.fofapro.com/)

## Features

- Supported Running Modes:
  - [x] Local Machine
  - [x] Virtual Network
- Supported Protocols:
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
- Use TcpForward to forward network traffic
- Support tcp syn logging
- Support icmp ping logging 
- Support udp packet logging
- Support ja3 SSL Fingerprint
- Support IP Limiter 

## Protocol simulation demos
### Rdp
Support credssp ntlmv2 nla authentication. 

Support to configure the image displayed when user login.
![RDP demo](docs/rdp.gif)

### SSH 
Support user login.

Support fake terminal commands, such as id, uid, whoami, etc.

Account format: username:password:home:uid
![SSH demo](docs/ssh.gif)

### IMAP & SMTP 
Support user login and interaction.

![IMAP & SMTP demo](docs/imap_smtp.gif)

### Mysql 
Support sql statement query interaction

![Mysql demo](docs/mysql.gif)

### FTP 
Support user login and interaction.

![Ftp demo](docs/ftp.gif)

### Oracle and BACnet
Currently only support nmap fingerprint spoofing

![tns and BACnet demo](docs/oracle_bacnet.gif)

### Telnet
Support login and interaction.

![Telnet demo](docs/telnet.gif)

### Redis 
Support login and  interaction

![Redis demo](docs/redis.gif)

### Elasticsearch
Support basic info

![Elasticsearch demo](docs/elasticsearch.gif)

### AMQP 
Support login and interaction

![AMQP demo](docs/amqp.gif)

### COAP 
Currently only support nmap fingerprint spoofing

![COAP demo](docs/coap.gif)

### HTTP
Support website clone, You need to install the chrome browser and [chrome driver](https://chromedriver.chromium.org/downloads) to work.

## Quick Start

### Generate Config
The configuration of all protocols and parameters is generated by genConfig subcommand.
   
Use 172.16.0.0/16 subnet to generate the configuration file:
```shell 
fapro genConfig -n 172.16.0.0/16 > fapro.json
```

Or use local address instead of the virtual network:
```shell 
fapro genConfig > fapro.json
```

Only generate ssh protocol configuration:
```shell 
./fapro genConfig -p ssh
```

### Run the protocol simulator
Run FaPro in verbose mode and start the web service on port 8080:
```shell
fapro run -v -l :8080
```

### Tcp syn logging
For windows users, please install [winpcap](https://www.winpcap.org/install/) or [npcap](https://nmap.org/npcap/).

## Log analysis
Use ELK to analyze protocol logs:
![FaPro Kibana](docs/FaProLogs.jpg)

## Configuration
This section contains the sample configuration used by FaPro.

```json
{
     "version": "0.55",
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

 - version: Configuration version.
 - network: The subnet used by the virtual network or the address bound to the local machine(Local mode).
 - network_build: Network mode(supported value: localhost, all, userdef)
   - localhost: Local mode, all services are listening on the local machine
   - all: Create all hosts in the subnet(i.e., Can ping all the host in the subnet)
   - userdef: Create only the hosts specified in the hosts configuration.
 - storage: Specify the storage used for log collection, support sqlite, mysql, elasticsearch. e.g.
   - sqlite3:logs.db
   - mysql://user:password@tcp(127.0.0.1:3306)/logs
   - es://http://username:password@127.0.0.1:9200   (currently only supports Elasticsearch 7.x)
 - geo_db: MaxMind geoip2 database file path, used to generate ip geographic location information. if you use Elasticsearch storage, never need this field, it will be automatically generated using the geoip processor of Elasticsearch.
 - hostname: Specify the host field in the log.
 - use_logq: Use local disk message queue to save logs, and then send it to remote mysql or Elasticsearch to prevent remote log loss.
 - cert_name: Common name of the generated certificate.
 - syn_dev: Specify the network interface used to capture tcp syn packets. If it is empty, the tcp syn packet will not be recorded. On windows, the device name is like "\Device\NPF_{xxxx-xxxx}".
 - udp_dev: Same as syn_dev, but for udp packet.
 - icmp_dev: Same as syn_dev, but for icmp ping packet.
 - limiter: IP limiter configuration, in the specified time period (period) access more than times (count), then block specified time (block_period).
   - period: Time period for ip limiter (in minutes)
   - count: The maximum number of times the IP can be accessed within the specified time period
   - block_period: The ban time after exceeding the IP access limit (in minutes)
 - exclusions: Exclude remote ips from logs.
 - hosts: Each item is a host configuration.
 - handlers: Service configuration, the service configured on the host, each item is a service configuration.
 - handler: Service name (i.e., protocol name)
 - params: Set the parameters supported by the service.
 

### Example
Create a virtual network, The subnet is 172.16.0.0/24, include 2 hosts,

172.16.0.3 run dns, ssh service,

and 172.16.0.5 run rpc, rdp service,

protocol access logs are saved to elasticsearch, exclude the access log of 127.0.0.1 and 8.8.8.8.
```json
{
    "version": "0.55",
    "network": "172.16.0.0/24",
    "network_build": "userdef",
    "storage": "es://http://127.0.0.1:9200",
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
### Automatically generate service configuration

Use the **ipclone.py** script in [Scripts](scripts/README.md), You can clone the ip service configuration from [fofa](https://fofa.so) to quickly generate the service configuration of the real machine.

![fofa_clone](docs/fofa_clone.gif)

## Learn more
- [How to build a network scanning analysis platform - Part I](./howto/howto_1.md)
- [How to build a network scanning analysis platform - Part II](./howto/howto_2.md)
- [Discord](https://discord.gg/Eaz9dzV4AP)

## FAQ 
We have collected some [frequently asked questions](FAQ.md). Before reporting an issue, please search if the FAQ has the answer to your problem.

## Contributing
* Issues are welcome.
  
