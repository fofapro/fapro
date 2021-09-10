

# linux非root用户运行fapro
fapro为程序路径

sudo setcap cap_net_raw,cap_net_admin=eip fapro

# windows powershell下输出的配置文件运行错误
运行时提示
panic: Fatal error config file: While parsing config: invalid character 'ÿ' looking for beginning of value

因为powershell > 输出的文件包含UTF-8 BOM标记,程序读取错误，使用Out-File输出文件。
./fapro.exe genConfig -n 172.16.0.0/16 | Out-File -Encoding ASCII fapro.json
  
  
