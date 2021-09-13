

# Run FaPro without root privileges
like nmap:
sudo setcap cap_net_raw,cap_net_admin=eip fapro

# The configuration file generated under windows powershell cannot be run
./fapro run prompt:
panic: Fatal error config file: While parsing config: invalid character 'ÿ' looking for beginning of value

Because the output encoding of powershell stdout redirect is UTF-8 with BOM, Use Out-File command to save the configuration file.
./fapro.exe genConfig -n 172.16.0.0/16 | Out-File -Encoding ASCII fapro.json
  
  
