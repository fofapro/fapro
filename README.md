
# FaPro

Fake Protocol Server, 用于创建虚拟网络及模拟网络协议的工具。使用跨平台、单文件部署的运行方式,可快速启动多个ip,多种协议。

目前已支持20多种协议。

## 使用方式

### 创建配置
   默认生成所有协议的配置
   
   指定使用172.16.0.0/16网段
```shell 
fapro genConfig -n 172.16.0.0/16 > fapro.json
```

或者使用本机地址，不使用虚拟网络
```shell 
fapro genConfig > fapro.json
```

### 启动协议模拟器
启动fapro,并开启web服务，指定端口为8080
```shell
fapro run -l :8080
```

## 协议演示
### rdp 
支持credssp ntlmv2 nla认证。
可以配置显示的图片文件。
![RDP演示](docs/rdp.gif)


## 配置文件格式
```json
{
     "version": "0.33",
     "network": "127.0.0.1/32",
     "network_build": "localhost",
     "storage": null,
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

 - version 指定配置文件版本号
 - network 指定生成的网段, localhost的网络模式下无效
 - network_build 网络模式(支持localhost, all, userdef)， localhost为本地模式,所有服务监听在本地; all 创建所有虚拟主机(整个网段的主机都可以ping通)，userdef只创建hosts中指定的主机(只有hosts中出现的ip可以ping通)
 - storage 指定日志收集的存储，支持sqlite3, mysql://, es://, 示例 es://http://127.0.0.1:9200 mysql://user:pass@tcp(127.0.0.1:3306)/logs sqlite3:logs.db
 - hosts 主机配置列表，每一项为一个ip配置
 - handlers 服务配置，ip上配置的服务，每一项为一个服务配置
 - handler 服务名，支持的服务可以使用
 - params 设置相应服务的参数列表
 

示例：创建自定义网络主机. 
网段为172.16.0.0/24, 其中有2台主机，
172.16.0.3开通dns, ssh服务
172.16.0.5开通rpc, rdp服务
存储协议访问日志到elasticsearch数据库
```json
{
    "version": "0.33",
    "network": "172.16.0.0/24",
    "network_build": "userdef",
    "storage": "es://http://127.0.0.1:9200",
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
                        "domain_name": "DESKTOP-Q1Test"
                    }
                }
            ]
        }
    ]
}

```


  
