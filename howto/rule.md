<h1 align="center">
如何使用FaPro批量模拟设备
</h1>
<br/>

## 简介

使用FaPro已经可以实现网络与服务的模拟。但是在真实的环境中，往往是一个网络中存在多个不同的设备，每个设备上运行不同的服务，要模拟真实的网络环境就需要对这些设备进行模拟。

为了模拟一个完整的设备，我们需要模拟该设备上所有开放端口的服务。因此引入了设备规则，一条规则包含一个设备开放的端口上的一系列服务特征。

现在通过FaPro，可以使用一条命令，直接创建一个虚拟网络，并在其中模拟多个不同的设备。

我们创建了一个包含30多个厂商的视频监控设备的示例规则库：
```
ABUS IP Camera
ADT NVR
ADT DVR
AJA-Video-Converter
Advidia IP Camera
AirSpace DVR2
AirSpace DVR
Alibi IP Camera
CP Plus DVR2
CP Plus DVR
Canon VB-H610
Clare Control IP Camera
Dahua IP Camera2
Dahua DHI-XVR4104C-N
Dahua IP Camera
Eyesonic IP Camera
GRUNDIG IP Camera
GeoVision-Camera
HIKVISION-Camera2
HIKVISION-Camera
HUAWEI IVS
IC Realtime NVR6000K
IC Realtime NVR7000K
Illustra-camera2
Illustra-camera
InVid Tech IP Camera2
InVid Tech IP Camera
JXJ-Camera2
JXJ-Camera
KB Vision DVR
KT&C IP Camera
KT&C IP Camera2
LG-Smart-IP-Device
Lorex DVR2
Lorex DVR
Lorex DVR3
Luma IP Camera
Luma 310 IP Camera
PARTIZAN-Cameras
Q-See NVR2
Q-See NVR
TRENDnet NVR408
TRENDnet TV-IP862IC
TRENDnet NVR2208
The Surveillance Shop IP Camera
The Surveillance Shop IP Camera2
TruVision TVR Camera
TruVision NVR Camera
WebWarrior IP Camera
WebWarrior IP Camera2
WebWarrior IP Camera3
```
目前仅支持web服务的模拟，只支持登录页面显示，不支持登录功能。

## 使用方式
首先下载[视频监控设备规则库](https://github.com/fofapro/fapro/raw/master/rules/camera.pak)

然后使用管理员权限运行fapro，从规则库创建模拟设备。
```shell
sudo ./fapro run -f camera.pak -v
```
会创建一个8.0.0.0/8的虚拟网络，并随机生成设备ip。

![camera rules demo](../docs/camera.gif)

使用web界面可以查看ip端口对应的设备规则。

