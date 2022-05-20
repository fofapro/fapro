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
from urllib.parse import urlparse
from os import path

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
    r = requests.get(url="https://fofa.info/api/v1/search/all",
                     params={"email": fofa_email,
                             "key": fofa_key,
                             "size": 1000,
                             "fields": "port,protocol,banner,cert,header",
                             "qbase64": base64.b64encode(query)})
    if r.status_code == 200:
        return r.json()['results']
    else:
        print("error request fofa api:", r.text)
        return None


def get_amqp_info(banner):
    result = {}
    copyright = re.search("copyright:(.*)[\r\n]?", banner)
    host = re.search("cluster_name:(.*)[\r\n]?", banner)
    platform = re.search("platform:(.*)[\r\n]?", banner)
    product = re.search("product:(.*)[\r\n]?", banner)
    version = re.search("version:(\d+.\d+.\d+)", banner)
    if copyright: result['copyright'] = copyright.group(1)
    result['host'] = host.group(1) if host else ""
    result['platform'] = platform.group(1) if platform else ""
    result['product'] = product.group(1) if product else ""
    if version: result['version'] = version.group(1)
    result['accounts'] = ["guest:guest"]
    return result


def get_bacnet_info(banner):
    result = {}
    vender_name = re.search("vendor_name:(.*)[\r\n]?", banner)
    firmware_ver = re.search("firmware_version:(.*)[\r\n]?", banner)
    object_name = re.search("object_name:(.*)[\r\n]?", banner)
    model_name = re.search("model_name:(.*)[\r\n]?", banner)
    if vender_name: result['vender_name'] = vender_name.group(1)
    if firmware_ver: result['firmware_ver'] = firmware_ver.group(1)
    if object_name: result['object_name'] = object_name.group(1)
    if model_name: result['model_name'] = model_name.group(1)
    return result


def get_dcerpc_info(banner):
    domain_name = ""
    if 'NTLMSSP' in banner:
        domain_name = re.search('DNS_Domain_Name:\s+(.*)', banner).group(1)
    return {"accounts":["administrator:123456"], "domain_name": domain_name}


def get_eos_info(header):
    server_version = re.search('Server:\s+(.*)', header)
    if server_version:
        with open("eos.json", "w") as in_file:
            in_file.write('{"code":404,"error":{"code":0,"details":[{"file":"http_plugin.cpp","line_number":244,'
                          '"message":"Unknown Endpoint","method":"handle_http_request"}],"name":"exception",'
                          '"what":"unspecified"},"message":"Not Found"}')
        return {
            "config_file": "eos.json",
            "server_version": server_version.group(1).strip('\r')
        }

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


def get_memcache_version(data):
    r = re.search("STAT version (\d+\.\d+\.\d+)", data)
    if r:
        return r.group(1)
    return "1.5.16"


def get_pop3_version(data):
    r = re.search("\+OK (.*) ready.", data)
    if r:
        return r.group(1)
    return "Dovecot"


def get_smtp_param(data):
    data = data.replace('220-', '220 ')
    params = data.split('\r\n')[0].split(' ')
    if len(params) >= 3:
        return {
            "accounts": [
                "admin:123456"
            ],
            "appname": params[2],
            "auth": False,
            "banner": params[3:],
            "hostname": params[1],
            "ssl": False,
            "timeout": 3
        }


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

def get_rtsp_paras(data):
    hdrs = parse_http_headers(data, lower=False)
    server = ''
    headers = []
    for [k, v] in hdrs:
        if k.lower() == 'server':
            server = v
        elif k.lower() == 'cseq':
            continue
        else:
            headers.append(f'{k}: {v}')
    return {"server": server,
            "headers": headers}

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

def parse_http_headers(banner, lower = True):
    lines = banner.split('\r\n')
    hdr = []
    for l in lines[1:]:
        kv = l.split(':', 1)
        if len(kv) > 1:
            k = kv[0].strip()
            v = kv[1].strip()
            if lower:
                k = k.lower()
                v = v.lower()
            hdr.append([k, v])
    return hdr

def get_upnp_info(banner):
    hdrs = parse_http_headers(banner)
    hdrs = {l[0]: l[1] for l in hdrs}
    max_age = 1800
    if 'cache-control' in hdrs and hdrs['cache-control']:
        ma = re.search('max-age=(\d+)', hdrs['cache-control'])
        if ma:
            max_age = int(ma.group(1))
    if 'location' in hdrs:
        return {'dev_location': hdrs['location'],
                'dev_type': hdrs['st'],
                'dev_usn': hdrs['usn'],
                'max_age': max_age,
                'server_version': hdrs['server'],}

def get_sip_body(banner):
    body = re.search("\r\n\r\n(.*)$", banner, re.MULTILINE | re.DOTALL)
    if body:
        return body.group(1)
    return ""

def get_socks5_auth(banner):
    method = re.search("USERNAME/PASSWORD", banner)
    return method != None

def get_postgres_auth(banner):
    method = re.search("Authentication type:\s+(\w+)", banner)
    if method:
        auth = method.group(1).lower()
        if auth == "plaintext":
            return "plain"
        elif auth == "md5":
            return "md5"
        else:
            return "none"
    return "none"

def get_postgres_version(banner):
    method = re.search("- VERSION: :\s+(.*),", banner)
    if method:
        return method.group(1)
    return "14.0"

def host_replace(url, new_ip):
    u = re.sub(r'(https?://)(.+?)(:\d+)?/(.*)',
               r'\1%s\3/\4',
               url)
    return u % new_ip

def fapro_dump(url, app_name, p='http', deep = True):
    deep_arg = ''
    if deep:
        deep_arg = '-d'
    run = f'{fapro_bin} dumpWeb -p {p} -u {url} -a {app_name} {deep_arg}'
    print("run: ", run)
    r = os.system(run)
    print("fapro dump return:", r)


def gen_handlers(ip, port, service, banner, header, deep_dump=True):
    print(f'gen handler for {ip} - {port} - {service}')
    handler = {"port": port}
    if service == "http":
        app_name = f'clone_{ip}_{port}'
        fapro_dump(f'http://{ip}:{port}', app_name, deep = deep_dump)
        handler['handler'] = 'http'
        handler['params'] = {"ssl": False,
                             "server_version": get_server(banner),
                             "fs_path": "webapps/" + app_name,
                             }
    elif service == "https":
        app_name = f'clone_{ip}_{port}_https'
        fapro_dump('https://{ip}:{port}', app_name, deep = deep_dump)
        handler['handler'] = 'http'
        handler['params'] = {"ssl": True,
                             "server_version": get_server(banner),
                             "fs_path": "webapps/" + app_name,
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
        handler['params'] = get_rtsp_paras(banner)
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
    elif service == "sip":
        handler['handler'] = 'sip'
        handler['params'] = {"body": get_sip_body(banner)}
    elif service == "postgres":
        handler['handler'] = 'postgres'
        handler['params'] = {"auth": get_postgres_auth(banner),
                             "server_version": get_postgres_version(banner),
                             "accounts": ["postgres:123456", "root:postgres"]}
    elif service == "iec-104":
        handler['handler'] = 'iec104'
    elif service == "ethernetip":
        handler['handler'] = 'eip'
        params = get_eip_info(banner)
        if params:
            handler['params'] = params
    elif service == "pop3":
        handler['handler'] = 'pop3'
        params = get_pop3_version(banner)
        if params:
            handler['params'] = {
                "accounts": ["admin:123456", "guest:guest"],
                "server_version": params,
                "ssl": False}
    elif service == "smtp":
        handler['handler'] = service
        params = get_smtp_param(banner)
        if params:
            handler['params'] = params
    elif service in ["smtp", "imap"]:
        handler['handler'] = service
        print(f'please config {service} params')
    elif service == "oracle":
        handler['handler'] = 'tns'
    elif service == 'ethereumrpc':
        handler['handler'] = 'ethereum'
    elif service in ["smtps", "pop3s", "imaps"]:
        handler['handler'] = service[:-1]
        handler['params'] = {"ssl": True}
        print(f'please config {service} params')
    elif service == "upnp":
        handler['handler'] = 'ssdp'
        ssdp_info = get_upnp_info(banner)
        if ssdp_info:
            handler['params'] = ssdp_info
            wemo_url = host_replace(ssdp_info['dev_location'], ip)
            u = urlparse(wemo_url)
            wemo_handler = {'port': u.port,
                            'handler': 'wemo'}
            app_name = f'wemo_{ip}_{u.port}'
            fapro_dump(wemo_url, app_name, p='wemo')
            if os.path.exists('./webapps/%s' % app_name):
                if 'server_version' in ssdp_info:
                    wemo_handler["params"] = {
                        "server_version": ssdp_info['server_version'],
                        'fs_path': app_name}
                else:
                    wemo_handler["params"] = {
                        "server_version": "OS 1.0 UPnP/1.0 Realtek/V1.0",
                        'fs_path': app_name}
                return [handler, wemo_handler]
    elif service == "coap":
        handler['handler'] = 'coap'
        app_name = f'coap_{ip}_{port}'
        app_conf = app_name + '.json'
        url = f'{ip}:{port}'
        fapro_dump(url, app_name, p='coap')
        if path.exists(app_conf):
            handler['params'] = {"config_file":app_conf}
        else:
            return
    elif service == "amqp":
        handler['handler'] = 'amqp'
        params = get_amqp_info(banner)
        if params:
            handler['params'] = params
    elif service == "bacnet":
        handler['handler'] = 'bacnet'
        params = get_bacnet_info(banner)
        if params:
            handler['params'] = params
    elif service == "dcerpc":
        handler['handler'] = 'dcerpc'
        params = get_dcerpc_info(banner)
        if params:
            handler['params'] = params
    elif service == "eos":
        handler['handler'] = 'eos'
        params = get_eos_info(header)
        if params:
            handler['params'] = params
    elif service == "memcache":
        handler['handler'] = 'memcache'
        params = get_memcache_version(banner)
        if params:
            handler['params'] = {'server_version': params}
    elif service in ["dns", "ntp", "s7", "snmp", "vnc", "modbus",  "telnet", "rdp", "smb", "dht", "nfs", "socks5", "onvif"]:
        handler['handler'] = service
    else:
        print(f'unsupport service {service}')
        return

    return [handler]

def clone_device(ip, hostname, store, deep_dump):
    data = fofa_query(ip)
    handlers = []
    proced = []
    for d in data:
        if d[1] and (not d[0] in proced):
            hs = gen_handlers(ip, d[0], d[1], d[2], d[3], deep_dump)
            if hs:
                handlers += hs
                proced += [h['port'] for h in hs]
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


if __name__ == "__main__":
    args = parse_args()
    r = clone_device(args.ip, args.name, args.storage, args.deep_dump)
    out_file = args.name+'.json'
    with open(out_file, "w") as w:
        json.dump(r, w, ensure_ascii=True, indent=2)
        print(f'clone ip config to {out_file} over.')
