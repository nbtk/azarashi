[azarashi](../README.md) / Preparation

# Preparation
デバイスに災危通報メッセージを出力させるための設定例です。
## u-blox M10S < UART > Raspberry Pi 4 + Ubuntu 22.04 + ubxtool (CLI)
UARTを有効にするため、設定ファイルの末尾に `enable_uart=1` を追記します。
```shell
$ sudo vi /boot/firmware/config.txt
```
```shell
[all]
...

# Enable the UART port
enable_uart=1
```
再起動して、シリアルデバイスが認識されていることを確認します。
```shell
$ sudo reboot
```
`/dev/ttyS0` の状態を確認しましょう。
```shell
$ stat /dev/ttyS0
```
```shell
  File: /dev/ttyS0
  Size: 0         	Blocks: 0          IO Block: 4096   character special file
Device: 5h/5d	Inode: 602         Links: 1     Device type: 4,40
Access: (0660/crw-rw----)  Uid: (    0/    root)   Gid: (   20/ dialout)
...
```
`/dev/ttyS0` が存在しないときは、dmesg コマンドでシリアルデバイスがどう認識されているかを確認しましょう。デバイスのファイル名が違う、UART を有効にする設定が間違っている、有効化に失敗している、といった原因が考えられます。
```shell
$ sudo dmesg | grep serial
```
```shell
[    0.525432] bcm2835-aux-uart fe215040.serial: there is not valid maps for state default
[    0.527303] fe215040.serial: ttyS0 at MMIO 0xfe215040 (irq = 21, base_baud = 62500000) is a 16550
```
シリアルデバイスに `sudo` コマンドを使わずに読み書きしたいときは、ユーザを `dialout` グループに追加します。
```shell
$ sudo usermod -a -G dialout $USER
$ logout # then re-login to the machine
```
次に、SFRBX メッセージの出力を有効にします。データシートを見て設定コマンドを直接送るか、設定ツールを使ってください。ここでは設定ツール ubxtool を使います。ubxtool は次のようにインストールします。
```shell
$ sudo apt update
$ sudo apt install gpsd gpsd-clients
```
SFRBX メッセージの出力に関連する設定コマンドの例です。
```shell
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,1,1 # sets 'enable'  to ram
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,0,1 # sets 'disable' to ram
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,1,2 # sets 'enable'  to bbr (battery-backed ram)
$ ubxtool -f /dev/ttyS0 -s 9600 -z CFG-MSGOUT-UBX_RXM_SFRBX_UART1,0,2 # sets 'disable' to bbr (battery-backed ram)
$ ubxtool -f /dev/ttyS0 -s 9600 -g CFG-MSGOUT-UBX_RXM_SFRBX_UART1 | grep -A3 UBX-CFG-VALGET # gets the state
```
デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。
## u-blox F9P < USB > Windows + u-center (GUI)
設定ツール [u-center](https://www.u-blox.com/en/product/u-center) をダウンロードし、インストールしてください。

u-center で SFRBX メッセージを出力するように設定してください。下記は SFRBX メッセージを USB に出力するための参考設定手順です。
```
Open u-center ->
  View -> Configuration View ->
    CFG (Configuration) -> Revert to default configuration -> Send
    MSG (Messages) -> Messages -> 02-13 RXM-SFRBX ->
      Check the "USB" box and type 1 in the "on" box -> Send
    NMEA (NMEA Protocol) -> NMEA Version -> Select 4.11 -> Send
    CFG (Configuration) -> Save current configuration -> Send
```
u-center で QZSS の L1S シグナル受信機能を有効にしてください。下記は GPS と QZSS のメッセージをすべて受信するための参考設定手順です。
```
Open u-center ->
  View -> Generation 9 Configuration View -> GNSS Configuration ->
    Check All the "GPS" and "QZSS" boxes ->
  　　  Check the "RAM" and "Flash" boxes in the "Write to layer" ->
 　　　　   Send Configuration
```
設定は永続化され、他の機器に接続し直しても災危通報メッセージを出力します。デバイスに通電してから災危通報メッセージを出力し始めるまでしばらく時間がかかります。
## Sony Spresense
[QZSS 災危通報 (QZQSM) の NMEA センテンスを出力するように設定してください。](https://developer.sony.com/develop/spresense/docs/arduino_tutorials_ja.html#_qzss_災危通報を出力する)
