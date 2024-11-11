![video_spider](https://socialify.git.ci/ihmily/DouyinLiveRecorder/image?font=Inter&forks=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Light)

## 💡簡介
[![Python Version](https://img.shields.io/badge/python-3.11.6-blue.svg)](https://www.python.org/downloads/release/python-3116/)
[![Supported Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-blue.svg)](https://github.com/ihmily/DouyinLiveRecorder)
[![Docker Pulls](https://img.shields.io/docker/pulls/ihmily/douyin-live-recorder?label=Docker%20Pulls&color=blue&logo=docker)](https://hub.docker.com/r/ihmily/douyin-live-recorder/tags)
![GitHub issues](https://img.shields.io/github/issues/ihmily/DouyinLiveRecorder.svg)
[![Latest Release](https://img.shields.io/github/v/release/ihmily/DouyinLiveRecorder)](https://github.com/ihmily/DouyinLiveRecorder/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/ihmily/DouyinLiveRecorder/total)](https://github.com/ihmily/DouyinLiveRecorder/releases/latest)

一款**簡易**的可循環值守的直播錄製工具，基於FFmpeg實現多平台直播源錄製，支持自定義配置錄製以及直播狀態推送。

</div>

## 😺已支持平台

- [x] 抖音
- [x] TikTok
- [x] 快手
- [x] 虎牙
- [x] 斗魚
- [x] YY
- [x] B站
- [x] 小紅書
- [x] bigo 
- [x] blued
- [x] SOOP(原AfreecaTV)
- [x] 網易cc
- [x] 千度熱播
- [x] PandaTV
- [x] 貓耳FM
- [x] Look直播
- [x] WinkTV
- [x] FlexTV
- [x] PopkonTV
- [x] TwitCasting
- [x] 百度直播
- [x] 微博直播
- [x] 酷狗直播
- [x] TwitchTV
- [x] LiveMe
- [x] 花椒直播
- [x] 流星直播
- [x] ShowRoom
- [x] Acfun
- [x] 映客直播
- [x] 音播直播
- [x] 知乎直播
- [x] CHZZK
- [x] 嗨秀直播
- [x] vv星球直播
- [x] 17Live
- [x] 浪Live
- [x] 暢聊直播
- [x] 飄飄直播
- [x] 六間房直播
- [x] 樂嗨直播
- [x] 花貓直播
- [ ] 更多平台正在更新中

</div>

## 🎈項目結構

```
.
└── DouyinLiveRecorder/
    ├── /config -> (config record)
    ├── /logs -> (save runing log file)
    ├── /backup_config -> (backup file)
    ├── /douyinliverecorder -> (package)
        ├── initializer.py-> (check and install nodejs)
    	├── spider.py-> (get live data)
    	├── stream.py-> (get live stream address)
    	├── utils.py -> (contains utility functions)
    	├── logger.py -> (logger handdle)
    	├── room.py -> (get room info)
    	├── /javascript -> (some decrypt code)
    ├── main.py -> (main file)
    ├── demo.py -> (call package test demo)
    ├── msg_push.py -> (send live status update message)
    ├── ffmpeg.exe -> (record video)
    ├── index.html -> (play m3u8 and flv video)
    ├── requirements.txt -> (library dependencies)
    ├── docker-compose.yaml -> (Container Orchestration File)
    ├── Dockerfile -> (Application Build Recipe)
    ├── StopRecording.vbs -> (stop recording script on Windows)
    ...
```

</div>

## 🌱使用說明

- 對於只想使用錄製軟體的小白用戶，進入[Releases](https://github.com/ihmily/DouyinLiveRecorder/releases) 中下載最新發布的 zip壓縮包即可，裡面有打包好的錄製軟體。（有些電腦可能會報毒，直接忽略即可，如果下載時被瀏覽器屏蔽，請更換瀏覽器下載）

- 壓縮包解壓後，在 `config` 文件夾內的 `URL_config.ini` 中添加錄製直播間地址，一行一個直播間地址。如果要自定義配置錄製，可以修改`config.ini` 文件，推薦將錄製格式修改為`ts`。
- 以上步驟都做好後，就可以運行`DouyinLiveRecorder.exe` 程序進行錄製了。錄製的視頻文件保存在同目錄下的 `downloads` 文件夾內。

- 另外，如果需要錄製TikTok、AfreecaTV等海外平台，請在配置文件中設置開啟代理並添加proxy_addr鏈接 如：`127.0.0.1:7890` （這只是示例地址，具體根據實際填寫）。

- 假如`URL_config.ini`文件中添加的直播間地址，有個別直播間暫時不想錄製又不想移除鏈接，可以在對應直播間的鏈接開頭加上`#`，那麼將停止該直播間的監測以及錄製。

- 軟體默認錄製清晰度為 `原畫` ，如果要單獨設置某個直播間的錄製畫質，可以在添加直播間地址時前面加上畫質即可，如`超清，https://live.douyin.com/745964462470` 記得中間要有`,` 分隔。

- 如果要長時間掛著軟體循環監測直播，最好循環時間設置長一點（咱也不差沒錄製到的那幾分鐘），避免因請求頻繁導致被官方封禁IP 。

- 要停止直播錄製，Windows平台可執行StopRecording.vbs腳本文件，或者在錄製界面使用 `Ctrl+C ` 組合鍵中斷錄製，若要停止其中某個直播間的錄製，可在`URL_config.ini`文件中的地址前加#，會自動停止對應直播間的錄製並正常保存已錄製的視頻。
- 最後，歡迎右上角給本項目一個star，同時也非常樂意大家提交pr。

&emsp;

直播間鏈接示例：

```
抖音：
https://live.douyin.com/745964462470
https://v.douyin.com/iQFeBnt/
https://live.douyin.com/yall1102  （鏈接+抖音號）
https://v.douyin.com/CeiU5cbX  （主播主頁地址）

TikTok：
https://www.tiktok.com/@pearlgaga88/live

快手：
https://live.kuaishou.com/u/yall1102

虎牙：
https://www.huya.com/52333

斗魚：
https://www.douyu.com/3637778?dyshid=
https://www.douyu.com/topic/wzDBLS6?rid=4921614&dyshid=

YY:
https://www.yy.com/22490906/22490906

B站：
https://live.bilibili.com/320

小紅書：
http://xhslink.com/xpJpfM
https://www.xiaohongshu.com/user/profile/6330049c000000002303c7ed?appuid=5f3f478a00000000010005b3

bigo直播：
https://www.bigo.tv/cn/716418802

buled直播：
https://app.blued.cn/live?id=Mp6G2R

SOOP：
https://play.sooplive.co.kr/sw7love

網易cc：
https://cc.163.com/583946984

千度熱播：
https://qiandurebo.com/web/video.php?roomnumber=33333

PandaTV：
https://www.pandalive.co.kr/live/play/bara0109

貓耳FM：
https://fm.missevan.com/live/868895007

Look直播:
https://look.163.com/live?id=65108820&position=3

WinkTV:
https://www.winktv.co.kr/live/play/anjer1004

FlexTV:
https://www.flextv.co.kr/channels/593127/live

PopkonTV:
https://www.popkontv.com/live/view?castId=wjfal007&partnerCode=P-00117
https://www.popkontv.com/channel/notices?mcid=wjfal007&mcPartnerCode=P-00117

TwitCasting:
https://twitcasting.tv/c:uonq

百度直播:
https://live.baidu.com/m/media/pclive/pchome/live.html?room_id=9175031377&tab_category

微博直播:
https://weibo.com/l/wblive/p/show/1022:2321325026370190442592

酷狗直播:
https://fanxing2.kugou.com/50428671?refer=2177&sourceFrom=

TwitchTV:
https://www.twitch.tv/gamerbee

LiveMe:
https://www.liveme.com/zh/v/17141543493018047815/index.html

花椒直播:
https://www.huajiao.com/l/345096174

流星直播:
https://www.7u66.com/100960

ShowRoom:
https://www.showroom-live.com/room/profile?room_id=480206  （主播主頁地址）

Acfun:
https://live.acfun.cn/live/179922

映客直播：
https://www.inke.cn/liveroom/index.html?uid=22954469&id=1720860391070904

音播直播：
https://live.ybw1666.com/800002949

知乎直播:
https://www.zhihu.com/people/ac3a467005c5d20381a82230101308e9 (主播主頁地址)

CHZZK:
https://chzzk.naver.com/live/458f6ec20b034f49e0fc6d03921646d2

嗨秀直播:
https://www.haixiutv.com/6095106

VV星球直播:
https://h5webcdn-pro.vvxqiu.com//activity/videoShare/videoShare.html?h5Server=https://h5p.vvxqiu.com&roomId=LP115924473&platformId=vvstar

17Live:
https://17.live/en/live/6302408

浪Live:
https://www.lang.live/en-US/room/3349463

暢聊直播:
https://www.tlclw.com/801044397

飄飄直播:
https://m.pp.weimipopo.com/live/preview.html?uid=91648673&anchorUid=91625862&app=plpl

六間房直播:
https://v.6.cn/634435

樂嗨直播:
https://www.lehaitv.com/8059096

花貓直播:
https://h.catshow168.com/live/preview.html?uid=19066357&anchorUid=18895331
```

&emsp;

## 🎃源碼運行
使用源碼運行，前提要有**Python>=3.10**環境，如果沒有請先自行安裝Python，再執行下面步驟。

1.首先拉取或手動下載本倉庫項目代碼

```bash
git clone https://github.com/SAOJSM/LiveRecorder-1.git
```

2.進入項目文件夾，安裝依賴

```bash
cd LiveRecorder-1
pip3 install -r requirements.txt
```

3.安裝[FFmpeg](https://ffmpeg.org/download.html#build-linux)，如果是Windows系統，這一步可跳過。對於Linux系統，執行以下命令安裝

CentOS執行

```bash
yum install epel-release
yum install ffmpeg
```

Ubuntu則執行

```bash
apt update
apt install ffmpeg
```

macOS 執行

**如果已經安裝 Homebrew 請跳過這一步**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```bash
brew install ffmpeg
```

4.運行程序

```python
python main.py
```

其中Linux系統請使用`python3 main.py` 運行。

## 避坑指南
若要用上面的方式執行
請先查看本避坑指南
1.Python版本請>3.10
如果沒有將會報錯
請透過此方法安裝3.10版本
並設定3.10版本設定為預設使用
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --config python3
```

2.請一併升級PIP包並升級，安裝後檢查版本是否正確
```bash
sudo apt install python3.10-distutils
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
python3.10 -m pip install --upgrade pip
python3.10 -m pip --version
```

3.如果你在執行安裝requirements.txt時獲得以下錯誤
(常見於Oracle VPS或是安裝了純淨版Linux系統)

pip3: can't open file '/LiveRecorder-1/install': [Errno 2] No such file or directory
請依照以下修正方法操作
```bash
python3.10 -m pip install -r requirements.txt
```

&emsp;
## 🐋容器運行

在運行命令之前，請確保您的機器上安裝了 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/) 

1.快速啟動

最簡單方法是運行項目中的 [docker-compose.yaml](https://github.com/ihmily/DouyinLiveRecorder/blob/main/docker-compose.yaml) 文件，只需簡單執行以下命令：

```bash
docker-compose up
```

可選 `-d` 在後台運行。



2.構建鏡像(可選)

如果你只想簡單的運行程序，則不需要做這一步。Docker鏡像倉庫中代碼版本可能不是最新的，如果要運行本倉庫主分支最新代碼，可以本地自定義構建，通過修改 [docker-compose.yaml](https://github.com/ihmily/DouyinLiveRecorder/blob/main/docker-compose.yaml) 文件，如將鏡像名修改為 `douyin-live-recorder:latest`，並取消 `# build: .` 註釋，然後再執行

```bash
docker build -t douyin-live-recorder:latest .
docker-compose up
```

或者直接使用下面命令進行構建並啟動

```bash
docker-compose -f docker-compose.yaml up
```



3.停止容器實例

```bash
docker-compose stop
```



4.注意事項

①在docker容器內運行本程序之前，請先在配置文件中添加要錄製的直播間地址。

②在容器內時，如果手動中斷容器運行停止錄製，會導致正在錄製的視頻文件損壞！

**無論哪種運行方式，為避免手動中斷或者異常中斷導致錄製的視頻文件損壞的情況，推薦使用 `ts` 格式保存**。

&emsp;

## ❤️貢獻者

&ensp;&ensp; [![Hmily](https://github.com/ihmily.png?size=50)](https://github.com/ihmily)
[![iridescentGray](https://github.com/iridescentGray.png?size=50)](https://github.com/iridescentGray)
[![annidy](https://github.com/annidy.png?size=50)](https://github.com/annidy)
[![wwkk2580](https://github.com/wwkk2580.png?size=50)](https://github.com/wwkk2580)
[![missuo](https://github.com/missuo.png?size=50)](https://github.com/missuo)
<a href="https://github.com/xueli12" target="_blank"><img src="https://github.com/xueli12.png?size=50" alt="xueli12" style="width:53px; height:51px;" /></a>
<a href="https://github.com/kaine1973" target="_blank"><img src="https://github.com/kaine1973.png?size=50" alt="kaine1973" style="width:53px; height:51px;" /></a>
<a href="https://github.com/yinruiqing" target="_blank"><img src="https://github.com/yinruiqing.png?size=50" alt="yinruiqing" style="width:53px; height:51px;" /></a>
<a href="https://github.com/Max-Tortoise" target="_blank"><img src="https://github.com/Max-Tortoise.png?size=50" alt="Max-Tortoise" style="width:53px; height:51px;" /></a>
[![justdoiting](https://github.com/justdoiting.png?size=50)](https://github.com/justdoiting)
[![dhbxs](https://github.com/dhbxs.png?size=50)](https://github.com/dhbxs)
[![wujiyu115](https://github.com/wujiyu115.png?size=50)](https://github.com/wujiyu115)
[![zhanghao333](https://github.com/zhanghao333.png?size=50)](https://github.com/zhanghao333)
<a href="https://github.com/gyc0123" target="_blank"><img src="https://github.com/gyc0123.png?size=50" alt="gyc0123" style="width:53px; height:51px;" /></a>

&emsp;

## ⏳提交日誌
- 20241111
  - 優化代碼
  - 將程式碼中簡體中文部分轉換為繁體中文(持續編修中)
  - 重構部分代碼
- 20241030
  - 新增嗨秀直播、vv星球直播、17Live、浪Live、SOOP、暢聊直播(原時光直播)、飄飄直播、六間房直播、樂嗨直播、花貓直播等10個平台直播錄製
  - 修復小紅書直播錄製，支持小紅書作者主頁地址錄製直播
  - 新增支持ntfy消息推送，以及新增支持批量推送多個地址（逗號分隔多個推送地址)
  - 修復Liveme直播錄製、twitch直播錄製
  - 新增Windows平台一鍵停止錄製VB腳本程序
- 20241005
  - 新增郵箱和Bark推送
  - 新增直播註釋停止錄製
  - 優化分段錄製
  - 重構部分代碼
- 20240928
  - 新增知乎直播、CHZZK直播錄製
  - 修復音播直播錄製
- 20240903
  - 新增抖音雙屏錄製、音播直播錄製
  - 修復PandaTV、bigo直播錄製
- 20240713
  - 新增映客直播錄製
- 20240705
  - 新增時光直播錄製
- 20240701
  - 修復虎牙直播錄製2分鐘斷流問題
  - 新增自定義直播推送內容
- 20240621
  - 新增Acfun、ShowRoom直播錄製
  - 修復微博錄製、新增直播源線路
  - 修復斗魚直播60幀錄製
  - 修復酷狗直播錄製
  - 修復TikTok部分無法解析直播源
  - 修復抖音無法錄製連麥直播
- 20240510
  - 修復部分虎牙直播間錄製錯誤
- 20240508
  - 修復花椒直播錄製
  - 更改文件路徑解析方式 [@kaine1973](https://github.com/kaine1973)
- 20240506
  - 修復抖音錄製畫質解析bug
  - 修復虎牙錄製 60幀最高畫質問題
  - 新增流星直播錄製
- 20240427
  - 新增LiveMe、花椒直播錄製
- 20240425
  - 新增TwitchTV直播錄製
- 20240424
  - 新增酷狗直播錄製、優化PopkonTV直播錄製
- 20240423
  - 新增百度直播錄製、微博直播錄製
  - 修復斗魚錄製直播回放的問題
  - 新增直播源地址顯示以及輸出到日誌文件設置
- 20240311
  - 修復海外平台錄製bug，增加畫質選擇，增強錄製穩定性
  - 修復虎牙錄製bug (虎牙`一起看`頻道 有特殊限制，有時無法錄製)
- 20240309
  - 修復虎牙直播、小紅書直播和B站直播錄製
  - 新增5個直播平台錄製，包括winktv、flextv、look、popkontv、twitcasting
  - 新增部分海外平台賬號密碼配置，實現自動登錄並更新配置文件中的cookie
  - 新增自定義配置需要使用代理錄製的平台
  - 新增只推送開播消息不進行錄製設置
  - 修復了一些bug
- 20240209
  - 優化AfreecaTV錄製，新增賬號密碼登錄獲取cookie以及持久保存
  - 修復了小紅書直播因官方更新直播域名，導致無法錄製直播的問題
  - 修復了更新URL配置文件的bug
  - 最後，祝大家新年快樂！

<details><summary>點擊展開更多提交日誌</summary>

- 20240129
  - 新增貓耳FM直播錄製
- 20240127
  - 新增千度熱播直播錄製、新增pandaTV(韓國)直播錄製
  - 新增telegram直播狀態消息推送，修復了某些bug
  - 新增自定義設置不同直播間的錄製畫質(即每個直播間錄製畫質可不同)
  - 修改錄製視頻保存路徑為 `downloads` 文件夾，並且分平台進行保存。
- 20240114
  - 新增網易cc直播錄製，優化ffmpeg參數，修改AfreecaTV輸入直播地址格式
  - 修改日誌記錄器 @[iridescentGray](https://github.com/iridescentGray)
- 20240102
  - 修復Linux上運行，新增docker配置文件
- 20231210
  - 修復錄製分段bug，修復bigo錄製檢測bug
  - 新增自定義修改錄製主播名
  - 新增AfreecaTV直播錄製，修復某些可能會發生的bug
- 20231207
  - 新增blued直播錄製，修復YY直播錄製，新增直播結束消息推送
- 20231206
  - 新增bigo直播錄製
- 20231203
  - 新增小紅書直播錄製（全網首發），目前小紅書官方沒有切換清晰度功能，因此直播錄製也只有默認畫質
  - 小紅書錄製暫時無法循環監測，每次主播開啟直播，都要重新獲取一次鏈接
  - 獲取鏈接的方式為 將直播間轉發到微信，在微信中打開後，複製頁面的鏈接。
- 20231030
  - 本次更新只是進行修復，沒時間新增功能。
  - 歡迎各位大佬提pr 幫忙更新維護
- 20230930
  - 新增抖音從接口獲取直播流，增強穩定性
  - 修改快手獲取直播流的方式，改用從官方接口獲取
  - 祝大家中秋節快樂！
- 20230919
  - 修復了快手版本更新後錄製出錯的問題，增加了其自動獲取cookie(~~穩定性未知~~)
  - 修復了TikTok顯示正在直播但不進行錄製的問題
- 20230907
  - 修復了因抖音官方更新了版本導致的錄製出錯以及短鏈接轉換出錯
  - 修復B站無法錄製原畫視頻的bug
  - 修改了配置文件字段，新增各平台自定義設置Cookie
- 20230903
  - 修復了TikTok錄製時報644無法錄製的問題
  - 新增直播狀態推送到釘釘和微信的功能，如有需要請看 [設置推送教程](https://d04vqdiqwr3.feishu.cn/docx/XFPwdDDvfobbzlxhmMYcvouynDh?from=from_copylink)
  - 最近比較忙，其他問題有時間再更新
- 20230816
  - 修復斗魚直播（官方更新了字段）和快手直播錄製出錯的問題
- 20230814
  - 新增B站直播錄製
  - 寫了一個在線播放M3U8和FLV視頻的網頁源碼，打開即可食用
- 20230812
  - 新增YY直播錄製
- 20230808
  - 修復主播重新開播無法再次錄製的問題
- 20230807
  - 新增了斗魚直播錄製
  - 修復顯示錄製完成之後會重新開始錄製的問題
- 20230805
  - 新增了虎牙直播錄製，其暫時只能用flv視頻流進行錄製
  - Web API 新增了快手和虎牙這兩個平台的直播流解析（TikTok要代理）
- 20230804
  - 新增了快手直播錄製，優化了部分代碼
  - 上傳了一個自動化獲取抖音直播間頁面Cookie的代碼，可以用於錄製
- 20230803
  - 通宵更新 
  - 新增了國際版抖音TikTok的直播錄製，去除冗餘 簡化了部分代碼
- 20230724	
  - 新增了一個通過抖音直播間地址獲取直播視頻流鏈接的API接口，上傳即可用
  </details>
  &emsp;

## 有問題可以提issue, 我會在這裡持續添加更多直播平台的錄製 歡迎Star
