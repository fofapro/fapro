#!/usr/bin/env python3

# clone fapro ip config from fofa
# please set fofa_email and fofa_key first

import requests
import os
import sys
import base64
import json
import re
import argparse

fofa_email = os.environ.get('FOFA_EMAIL')
fofa_key = os.environ.get('FOFA_KEY')

if (not fofa_email) or (not fofa_key):
    print("please set FOFA_EMAIL and FOFA_KEY env first.")
    sys.exit(1)

import shutil

def get_fapro():
    return shutil.which("fapro") or shutil.which("./fapro")

fapro_bin = get_fapro()
if not fapro_bin:
    print("can't find fapro binary")
    sys.exit(1)

def fofa_query(ip):
    query = f'ip="{ip}"'.encode('ascii')
    r = requests.get(url="https://fofa.so/api/v1/search/all",
                     params={"email": fofa_email,
                             "key": fofa_key,
                             "size": 1000,
                             "fields": "port,protocol,banner,cert",
                             "qbase64": base64.b64encode(query)})
    if r.status_code == 200:
        return r.json()['results']
    else:
        print("error request fofa api:", r.text)
        return None

def get_cert_name(datas):
    for d in datas:
        if d[3]:
            return re.search('CommonName:\s+(.*)', d[3]).group(1)
    return "unknown"

def get_server(data):
    r = re.search("[Ss]erver:\s*([^\s]+)", data)
    if r:
        return r.group(1)
    return "Apache"

def get_ftp_welcome(data):
    r = re.search("220(.+)[\r\n]", data)
    if r:
        return r.group(1).strip()
    return "Welcome to Pure-FTPd [privsep]"

def get_mysql_version(data):
    r = re.search("(\d+\.\d+\.\d+)", data)
    if r:
        return r.group(1)
    return "5.5.62"

def get_ssh_version(data):
    r = re.search("(.*?)[\r\n]", data)
    if r:
        return r.group(1)
    return "SSH-2.0-OpenSSH_5.3"

def get_redis_version(data):
    r = re.search("redis_version:(\d+\.\d+\.\d+)", data)
    if r:
        return r.group(1)
    return "6.2.3"

def get_rtsp_server(data):
    r = re.search("Server: (.*?)[\r\n]", data)
    if r:
        return r.group(1)
    return ""

def get_port_mapping(data):
    result = []
    for row in data.split(','):
        r = re.search("(\d+) v(\d) (\w+)\((\d+)\)", row)
        if r:
            result.append(f'{r.group(1)},{r.group(2)},{r.group(3).lower()},{r.group(4)}')
    return result

def get_eip_info(banner):
    ip = re.search("Device IP:\s+(\d+\.\d+\.\d+\.\d+)", banner)
    product = re.search("Product:\s+(.+)[\r\n]?", banner)
    if ip and product:
        return {"ip": ip.group(1),
                "product_name": product.group(1)}
    return None

def gen_handler(ip, port, service, banner, deep_dump=True):
    print(f'gen handler for {ip} - {port} - {service}')
    handler = {"port": port}
    deep_arg = ''
    if deep_dump:
        deep_arg = '-d'
    if service == "http":
        app_name = f'clone_{ip}_{port}'
        os.system(f'{fapro_bin} dumpWeb -u http://{ip}:{port} -a {app_name} {deep_arg}')
        handler['handler'] = 'http'
        handler['params'] = {"ssl": False,
                             "server_version": get_server(banner),
                             "fa_path": "webapps/" + app_name,
                             }
    elif service == "https":
        app_name = f'clone_{ip}_{port}_https'
        os.system(f'{fapro_bin} dumpWeb -u https://{ip}:{port} -a {app_name} {deep_arg}')
        handler['handler'] = 'http'
        handler['params'] = {"ssl": True,
                             "server_version": get_server(banner),
                             "fa_path": "webapps/" + app_name,
                             }
    elif service == "ftp":
        handler['handler'] = 'ftp'
        handler['params'] = {"welcome_message": get_ftp_welcome(banner)}
    elif service == "ssh":
        handler['handler'] = 'ssh'
        handler['params'] = {"server_version": get_ssh_version(banner)}
    elif service == "mysql":
        handler['handler'] = 'mysql'
        handler['params'] = {"server_version": get_mysql_version(banner)}
    elif service == "redis":
        handler['handler'] = 'redis'
        handler['params'] = {"server_version": get_redis_version(banner)}
    elif service == "rtsp":
        handler['handler'] = 'rtsp'
        handler['params'] = {"server": get_rtsp_server(banner)}
    elif service == "portmap":
        handler['handler'] = 'portmap'
        handler['params'] = {"mapping_table": get_port_mapping(banner)}
    elif service == "elastic":
        handler['handler'] = 'elasticsearch'
    elif service == "mqtt":
        handler['handler'] = 'mqtt'
        handler['params'] = {"ssl": False}
    elif service == "mqtt-ssl":
        handler['handler'] = 'mqtt'
        handler['params'] = {"ssl": True}
    elif service == "iec-104":
        handler['handler'] = 'iec104'
    elif service == "ethernetip":
        handler['handler'] = 'eip'
        params = get_eip_info(banner)
        if params:
            handler['params'] = params
    elif service in ["smtp", "pop3", "imap"]:
        handler['handler'] = service
        print(f'please config {service} params')
    elif service in ["smtps", "pop3s", "imaps"]:
        handler['handler'] = service[:-1]
        handler['params'] = {"ssl": True}
        print(f'please config {service} params')
    elif service in ["dns", "ntp", "s7", "snmp", "memcache", "vnc", "modbus",  "telnet", "rdp", "smb", "dcerpc"]:
        handler['handler'] = service
    else:
        print(f'unsupport service {service}')
        return

    return handler

def clone_device(ip, hostname, store, deep_dump):
    data = fofa_query(ip)
    handlers = []
    proced = []
    for d in data:
        if d[1] and (not d[1] in proced):
            h = gen_handler(ip, d[0], d[1], d[2], deep_dump)
            if h:
                handlers.append(h)
                proced.append(d[1])
    result = {"version": "0.40",
              "network": "127.0.0.1/32",
              "network_build": "localhost",
              "hostname": hostname,
              "use_logq": True,
              "storage": store,
              "cert_name": get_cert_name(data),
              "exclusions": ["8.8.8.8"],
              "syn_dev": "any",
              "udp_dev": "any",
              "icmp_dev": "any",
              "hosts": [{"ip": "0.0.0.0",
                         "handlers": handlers}],
              }
    return result

def parse_args():
    parser = argparse.ArgumentParser("ip device clone",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--storage',
                        default="es://http://elastic:your_password@127.0.0.1:9200",
                        help='storage config')
    parser.add_argument('-n', '--name',
                        default="sensor",
                        help='hostname')
    parser.add_argument('-i', '--ip',
                        default="92.205.17.233",
                        help='ip address to clone')
    parser.add_argument('-d', '--deep-dump',
                        action='store_true',
                        default=False,
                        help="deep dump web page")
    return parser.parse_args()


args = parse_args()
r = clone_device(args.ip, args.name, args.storage, args.deep_dump)
out_file = args.name+'.json'
with open(out_file, "w") as w:
    json.dump(r, w, ensure_ascii=True, indent=2)
    print(f'clone ip config to {out_file} over.')
