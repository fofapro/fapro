

## 常见问题
<details>
<summary>使用非root权限运行FaPro</summary>


和nmap类似:

sudo setcap cap_net_raw,cap_net_admin=eip fapro
</details>

<details>
<summary>windows powershell下生成的配置文件无法运行</summary>


运行./fapro run提示如下:

panic: Fatal error config file: While parsing config: invalid character 'ÿ' looking for beginning of value

因为powershell的输出编码是UTF-8 with BOM,程序读取失败,可以使用Out-File命令保存配置文件:

./fapro.exe genConfig -n 172.16.0.0/16 | Out-File -Encoding ASCII fapro.json
</details>

## FAQ
<details>
<summary>Run FaPro without root privileges</summary>


like nmap:

sudo setcap cap_net_raw,cap_net_admin=eip fapro
</details>

<details>
<summary>The configuration file generated under windows powershell cannot be run</summary>


./fapro run prompt:

panic: Fatal error config file: While parsing config: invalid character 'ÿ' looking for beginning of value

Because the output encoding of powershell stdout redirect is UTF-8 with BOM, Use Out-File command to save the configuration file.

./fapro.exe genConfig -n 172.16.0.0/16 | Out-File -Encoding ASCII fapro.json
</details>
