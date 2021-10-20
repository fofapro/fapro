# Description
Configurations and scripts for building a network scanning analysis platform.

## [中文Readme](README-CN.md)

## ipclone.py 

Python script for cloning service configuration from [fofa](https://fofa.so/)

You need:
- a fofa account to set the FOFA_EMAIL and FOFA_KEY environment variables
- fapro binary file in PATH
- chrome browser and chromedriver for website cloning

Usage:
```
# display usage help
./ipclone.py -h

# clone the service configuration with ip xx.xx.xx.xx，save it to sensor01
./ipclone.py -i xx.xx.xx.xx -n sensor01
```

## docker-compose.yml 
docker-compose template for ELK configuration.

**Notice:**
- change **ELASTIC_PASSWORD** to you own password,
- change **network.publish_host** to the server's public network ip address
- change the port mapping if you need

Usage:
```shell 
docker-compose up -d
```

## update_sensor.yml 
Ansible script for configure or update the sensor server.

Usage:
```shell 
# Download the latest version of FaPro, save it to fapro.tgz.
wget https://github.com/fofapro/fapro/releases/latest/download/fapro_linux_x86_64.tar.gz -O fapro.tgz

# Use ansible for sensor server deployment
ansible-playbook update_sensor.yml
```

## check.yml
Ansible script for monitoring the fapro process of the sensor server.

install norecon for wechat message notification, 

if you need other message notification, change nowx to other message notification command.
```shell 
pip3 install norecon

# Configure WeChat notification and set up WeChat message push token
nowx 
```

Usage：
```shell 
ansible-playbook check.yml
```

You can set up a cron job to execute it.
