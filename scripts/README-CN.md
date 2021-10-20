# 简介
用于搭建网络扫描分析平台的相关配置及脚本

## [README of English](README.md)

## ipclone.py 
从[fofa](https://fofa.so/)克隆服务配置的python脚本

使用前需要先设置FOFA_EMAIL和FOFA_KEY环境变量,并下载fapro

本地要安装chrome浏览器和chromedriver，用于网站克隆

使用方式:
```shell
# 查看使用帮助
./ipclone.py -h

# 克隆ip xx.xx.xx.xx的服务配置，保存为sensor01
./ipclone.py -i xx.xx.xx.xx -n sensor01
```

## docker-compose.yml 
配置ELK的docker-compose模板，注意：

- 修改**ELASTIC_PASSWORD**设置项的密码
- 修改**network.publish_host**为服务器的公网ip
- 根据需要修改公网映射的端口

使用方式:
```shell 
docker-compose up -d
```

## update_sensor.yml 
配置或更新sensor服务器的ansbile脚本

使用方式:
```shell 
# 下载最新版本的FaPro Release,保存为fapro.tgz,
wget https://github.com/fofapro/fapro/releases/latest/download/fapro_linux_x86_64.tar.gz -O fapro.tgz

# 使用ansible进行部署
ansible-playbook update_sensor.yml
```

## check.yml
监控sensor服务进程的ansible脚本

安装norecon,用于微信消息通知:
```shell 
pip3 install norecon

# 配置微信通知,根据提示设置微信push token。
nowx 
```

使用方式：
```shell 
ansible-playbook check.yml
```

可以加入crontab定时执行,如果发现进程没有启动，自动重启，并进行微信通知。



