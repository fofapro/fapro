
<h1 align="center">
  FaPro
  <br>
</h1>

<h5 align="center">免费、跨平台、单文件部署的网络协议服务端模拟器</h5>

![platform](https://img.shields.io/badge/platform-cross-important?color=%23189000)

## [README of English](README.md)

## 简介

FaPro是一个服务端协议模拟工具,可以轻松启停多个网络服务。

目标是支持尽可能多的协议，每个协议尽可能提供深度的交互支持。

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
- 使用TcpForward进行端口转发

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

### HTTP
支持网站克隆。
需要安装chrome浏览器和![chrome driver](https://chromedriver.chromium.org/downloads)才能使用。

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

### 运行协议模拟器
使用Verbose模式运行FaPro, 并在8080端口启动web服务:
```shell
fapro run -v -l :8080
```

## 日志分析
使用ELK分析协议日志，例如:
![FaPro Kibana](docs/FaProLogs.jpg)


## 配置文件
配置文件的简单介绍:

```json
{
     "version": "0.33",
     "network": "127.0.0.1/32",
     "network_build": "localhost",
     "storage": null,
     "geo_db": "/tmp/geoip_city.mmdb",
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
   - es://http://127.0.0.1:9200 (目前只支持Elasticsearch v7.x)
 - geo_db: MaxMind geoip2数据库的文件路径, 用于生成ip地理位置信息. 如果使用了Elasticsearch日志存储,则不需要此字段，将会使用Elasticsearch自带的geoip生成地理位置。
 - hosts: 主机列表，每一项为一个主机配置
 - handlers: 服务列表，每一项为一个服务配置
 - handler: 服务名(协议名)
 - params: 设置服务支持的参数
 

### 示例
使用子网172.16.0.0/24创建一个虚拟网络，包含2个主机:

172.16.0.3 运行dns、ssh服务

172.16.0.5 运行rpc、rdp服务

协议访问支持保存到elasticsearch。
```json
{
    "version": "0.33",
    "network": "172.16.0.0/24",
    "network_build": "userdef",
    "storage": "es://http://127.0.0.1:9200",
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

## 常见问题
我们收集了一些[常见问题](FAQ.md). 报告issue前，请先看看常见问题集中是否有你要找的答案。

## 贡献
* 欢迎提issue。
  

