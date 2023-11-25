<!--
Title: macOS에서 부팅 시 자동으로 MAC 주소와 호스트 이름을 무작위로 변조하는 방법
Description: Learn how to spoof MAC address and hostname automatically at boot on macOS.
Author: Sun Knudsen <https://github.com/sunknudsen>
Contributors: Yunseo Kim <https://github.com/yunseo-kim>
Reviewers:
Publication date: 2020-11-26T00:00:00.000Z
Listed: true
Pinned:
-->

# macOS에서 부팅 시 자동으로 MAC 주소와 호스트 이름을 무작위로 변조하는 방법 (ko)

[![How to spoof MAC address and hostname automatically at boot on macOS](how-to-spoof-mac-address-and-hostname-automatically-at-boot-on-macos.jpg)](https://www.youtube.com/watch?v=ASXANpr_zX8 "How to spoof MAC address and hostname automatically at boot on macOS")

> 주의: 몇몇 맥에서는 MAC 주소 변조가 불가능 ([issue](https://github.com/sunknudsen/privacy-guides/issues/15)).

> For the English version of this guide, go [here](https://github.com/yunseo-kim/privacy-guides/blob/main/how-to-spoof-mac-address-and-hostname-automatically-at-boot-on-macos/README.md).

## 요구사항

- macOS Catalina 혹은 그 이후 버전을 구동하는 컴퓨터

update-korean-first-names 스크립트를 직접 실행할 경우, 다음 사항들을 추가로 충족해야 합니다.
- Python3 및 다음 라이브러리
  - requests
  - bs4 (BeautifulsSoup)
- [jq](https://jqlang.github.io/jq/)
- 인터넷 연결 (스크래핑을 위해 <https://www.namechart.kr/>에 접속 가능해야 함)

## 주의사항

- `$`로 시작하는 명령어를 복사/붙여넣기 할 때는, 이 문자는 명령어의 일부가 아니므로 `$`를 제거하십시오.
- `cat << "EOF"`로 시작하는 명령어를 복사/붙여넣기 할 때는, `cat << "EOF"`부터 `EOF`까지 포함한 모든 줄을 한번에 선택하십시오.

## 가이드

### 1단계: `/usr/local/sbin` 디렉터리 생성

```shell
sudo mkdir -p /usr/local/sbin
sudo chown ${USER}:admin /usr/local/sbin
```

### 2단계: `/usr/local/sbin` 디렉터리를 `PATH` 환경변수에 추가

```shell
echo 'export PATH=$PATH:/usr/local/sbin' >> ~/.zshrc
source ~/.zshrc
```

### 3단계: [korean-first-names.txt](./korean-first-names.txt) 다운로드

2008년생 한국인 중 가장 흔한 1000개 이름을 [네임차트 - 한국인 아기 이름 인기 순위 통계](https://www.namechart.kr/chart/2008)로부터 스크래핑하여 얻은 목록입니다 (2023년 11월 26일에 마지막으로 [갱신](./misc/update-korean-first-names.sh)).

```shell
curl --fail --output /usr/local/sbin/korean-first-names.txt https://raw.githubusercontent.com/yunseo-kim/privacy-guides/main/how-to-spoof-mac-address-and-hostname-automatically-at-boot-on-macos/korean-first-names.txt
```

### 4단계: `spoof.sh` 스크립트 생성

```shell
cat << "EOF" > /usr/local/sbin/spoof.sh
#! /bin/sh

set -e
set -o pipefail

export LC_CTYPE=C

basedir=$(dirname "$0")

# Spoof computer name
first_name=$(sed "$(jot -r 1 1 1000)q;d" $basedir/korean-first-names.txt | sed -e 's/[^a-zA-Z]//g')
first_name_lower=$(echo $first_name | tr '[:upper:]' '[:lower:]')
model_name=$(system_profiler SPHardwareDataType | awk '/Model Name/ {$1=$2=""; print $0}' | sed -e 's/^[ ]*//')
model_name_without_space=$(echo $model_name | sed -e 's/ //g')
computer_name="$first_name의 $model_name"
host_name=$(echo "$first_name_lower의 $model_name_without_space" | sed -e 's/’//g' | sed -e 's/ /-/g' | sed -e 's/의/ui/g')
sudo scutil --set ComputerName "$computer_name"
sudo scutil --set LocalHostName "$host_name"
sudo scutil --set HostName "$host_name"
printf "%s\n" "Spoofed hostname to $host_name"

# Spoof MAC address of Wi-Fi interface
mac_address_prefix=$(networksetup -listallhardwareports | awk -v RS= '/en0/{print $NF}' | head -c 8)
mac_address_suffix=$(openssl rand -hex 3 | sed 's/\(..\)/\1:/g; s/.$//')
mac_address=$(echo "$mac_address_prefix:$mac_address_suffix" | awk '{print tolower($0)}')
networksetup -setairportpower en0 on
sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport --disassociate
sudo ifconfig en0 ether "$mac_address"
printf "%s\n" "Spoofed MAC address of en0 interface to $mac_address"
EOF
```

### 5단계: `spoof.sh` 실행 권한 부여

```shell
chmod +x /usr/local/sbin/spoof.sh
```

### 6단계: `local.spoof.plist` launch daemon 생성

```shell
cat << "EOF" | sudo tee /Library/LaunchDaemons/local.spoof.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>local.spoof</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/sbin/spoof.sh</string>
    </array>

    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
EOF
```

### 7단계: `spoof-hook.sh` 스크립트 생성

```shell
cat << "EOF" > /usr/local/sbin/spoof-hook.sh
#! /bin/sh

# Turn off Wi-Fi interface
networksetup -setairportpower en0 off
EOF
```

### 8단계: `spoof-hook.sh` 실행 권한 부여

```shell
chmod +x /usr/local/sbin/spoof-hook.sh
```

### 9단계: `com.apple.loginwindow`가 존재하지 않는지 확인

> Heads-up: 만약 `com.apple.loginwindow`가 존재하는 경우, 사용자 기본값을 신중하게 백업하고 현재 `LogoutHook` 스크립트와 `/usr/local/sbin/spoof-hook.sh`를 모두 실행하는 추상화 사용을 고려해야 합니다.

```console
$ sudo defaults read com.apple.loginwindow
2021-09-27 06:58:02.301 defaults[2267:25227]
Domain com.apple.loginwindow does not exist
```

com.apple.loginwindow 도메인이 존재하지 않네요 👍

### 10단계: 사용자 설정 구성 (로그아웃 시 Wi-Fi 인터페이스를 비활성화하는 데 사용)

```shell
sudo defaults write com.apple.loginwindow LogoutHook "/usr/local/sbin/spoof-hook.sh"
```

### 11단계: 재부팅한 후 호스트 이름 및 MAC 주소 변조가 성공했는지 확인

#### Spoofed hostname

```console
$ scutil --get HostName
chaewonui-MacBookAir
```

#### Spoofed MAC address

```console
$ ifconfig en0 | grep ether | awk '{print $2}'
98:01:a7:8e:0f:51
```

#### Hardware MAC address

```console
$ networksetup -listallhardwareports | awk -v RS= '/en0/{print $NF}'
98:01:a7:5e:d0:c2
```

“Spoofed hostname”이 랜덤하고 “Spoofed MAC address”와 “Hardware MAC address”가 일치하지 않나요?

👍

---

## 원래대로 되돌리고 싶으신가요? 다음과 같이 하시면 됩니다!

### 1단계: 파일 삭제

```shell
rm /usr/local/sbin/first-names.txt
rm /usr/local/sbin/spoof-hook.sh
rm /usr/local/sbin/spoof.sh
sudo rm /Library/LaunchDaemons/local.spoof.plist
```

### 2단계: 사용자 설정 삭제

```shell
sudo defaults delete com.apple.loginwindow LogoutHook
```

### 3단계: 컴퓨터 이름과 로컬 호스트 이름, 호스트 이름 설정

> 주의: `Yunseo` 위치에 본인 이름을 넣으세요.

```shell
sudo scutil --set ComputerName "Yunseo의 MacBook Air"
sudo scutil --set LocalHostName "Yunseoui-MacBookAir"
sudo scutil --set HostName "Yunseoui-MacBookAir"
```

### 4단계: 재부팅

👍
