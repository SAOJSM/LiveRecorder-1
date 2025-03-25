![video_spider](https://socialify.git.ci/SAOJSM/LiveRecorder-1/image?font=Inter&forks=1&language=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Light)

## 💡簡介
[![Python Version](https://img.shields.io/badge/python-3.11.6-blue.svg)](https://www.python.org/downloads/release/python-3116/)
[![Supported Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-blue.svg)](https://github.com/SAOJSM/LiveRecorder-1)
[![Docker Pulls](https://img.shields.io/docker/pulls/SAOJSM/LiveRecorder-1?label=Docker%20Pulls&color=blue&logo=docker)](https://hub.docker.com/r/SAOJSM/LiveRecorder-1/tags)
![GitHub issues](https://img.shields.io/github/issues/SAOJSM/LiveRecorder-1.svg)
[![Latest Release](https://img.shields.io/github/v/release/SAOJSM/LiveRecorder-1)](https://github.com/SAOJSM/LiveRecorder-1/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/SAOJSM/LiveRecorder-1/total)](https://github.com/SAOJSM/LiveRecorder-1/releases/latest)

一款**簡易**的可循環值守的直播錄製工具，基於FFmpeg實現多平臺直播源錄製，支援自定義配置錄製以及直播狀態推送。


</div>

## 😺已支援平臺

- [x] 抖音
- [x] TikTok
- [x] 快手
- [x] 虎牙
- [x] 鬥魚
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
- [x] Shopee
- [x] Youtube
- [x] 淘寶
- [x] 京東
- [x] Faceit
- [ ] 更多平臺正在更新中

</div>

## 🎈專案結構

```
.
└── LiveRecorder-1/
    ├── /config -> (config record)
    ├── /logs -> (save runing log file)
    ├── /backup_config -> (backup file)
    ├── /streamget -> (package)
        ├── initializer.py-> (check and install nodejs)
    	├── spider.py-> (get live data)
    	├── stream.py-> (get live stream address)
    	├── utils.py -> (contains utility functions)
    	├── logger.py -> (logger handdle)
    	├── room.py -> (get room info)
    	├── /javascript -> (some decrypt code)
    ├── main.py -> (main file)
    ├── ffmpeg_install.py -> (ffmpeg install script)
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

- 對於只想使用錄製軟體的小白使用者，請進入[Releases](https://github.com/ihmily/DouyinLiveRecorder/releases) 中下載最新發布的 zip壓縮包即可(本專案目前沒有Release)，裡面有打包好的錄製軟體。（有些電腦可能會報毒，直接忽略即可，如果下載時被瀏覽器遮蔽，請更換瀏覽器下載）

- 壓縮包解壓後，在 `config` 資料夾內的 `URL_config.ini` 中新增錄製直播間地址，一行一個直播間地址。如果要自定義配置錄製，可以修改`config.ini` 檔案，推薦將錄製格式修改爲`ts`。
- 以上步驟都做好後，就可以執行`DouyinLiveRecorder.exe` 程式進行錄製了。錄製的視訊檔案儲存在同目錄下的 `downloads` 資料夾內。

- 另外，如果位於牆內，需要錄製TikTok、AfreecaTV等海外平臺，請在配置檔案中設定開啟代理並新增proxy_addr鏈接 如：`127.0.0.1:7890` （這只是示例地址，具體根據實際填寫）。

- 假如`URL_config.ini`檔案中新增的直播間地址，有個別直播間暫時不想錄製又不想移除鏈接，可以在對應直播間的鏈接開頭加上`#`，那麼將停止該直播間的監測以及錄製。

- 軟體預設錄製清晰度為 `原畫` ，如果要單獨設定某個直播間的錄製畫質，可以在新增直播間地址時前面加上畫質即可，如`超清，https://live.douyin.com/745964462470` 記得中間要有`,` 分隔。

- 如果要長時間掛著軟體循環監測直播，建議循環時間設定長一點（咱也不差沒錄製到的那幾分鐘），避免因請求頻繁導致被官方封禁IP 。

- 要停止直播錄製，Windows平臺可執行StopRecording.vbs指令碼檔案，或者在錄製界面使用 `Ctrl+C ` 組合鍵中斷錄製，若要停止其中某個直播間的錄製，可在`URL_config.ini`檔案中的地址前加#，會自動停止對應直播間的錄製並正常儲存已錄製的視訊。
- 最後，歡迎右上角給本專案一個star，同時也非常樂意大家提交pr。

&emsp;

直播間鏈接示例：

```
抖音:
https://live.douyin.com/745964462470
https://v.douyin.com/iQFeBnt/
https://live.douyin.com/yall1102  （鏈接+抖音號）
https://v.douyin.com/CeiU5cbX  （主播主頁地址）

TikTok:
https://www.tiktok.com/@pearlgaga88/live

快手:
https://live.kuaishou.com/u/yall1102

虎牙:
https://www.huya.com/52333

鬥魚:
https://www.douyu.com/3637778?dyshid=
https://www.douyu.com/topic/wzDBLS6?rid=4921614&dyshid=

YY:
https://www.yy.com/22490906/22490906

B站:
https://live.bilibili.com/320

小紅書（推薦使用主頁地址):
https://www.xiaohongshu.com/user/profile/6330049c000000002303c7ed?appuid=5f3f478a00000000010005b3
http://xhslink.com/xpJpfM

bigo直播:
https://www.bigo.tv/cn/716418802

buled直播:
https://app.blued.cn/live?id=Mp6G2R

SOOP:
https://play.sooplive.co.kr/sw7love

網易cc:
https://cc.163.com/583946984

千度熱播:
https://qiandurebo.com/web/video.php?roomnumber=33333

PandaTV:
https://www.pandalive.co.kr/live/play/bara0109

貓耳FM:
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

映客直播:
https://www.inke.cn/liveroom/index.html?uid=22954469&id=1720860391070904

音播直播:
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
https://live.tlclw.com/106188

飄飄直播:
https://m.pp.weimipopo.com/live/preview.html?uid=91648673&anchorUid=91625862&app=plpl

六間房直播:
https://v.6.cn/634435

樂嗨直播:
https://www.lehaitv.com/8059096

花貓直播:
https://h.catshow168.com/live/preview.html?uid=19066357&anchorUid=18895331

Shopee:
https://sg.shp.ee/GmpXeuf?uid=1006401066&session=802458

Youtube:
https://www.youtube.com/watch?v=cS6zS5hi1w0

淘寶(需cookie):
https://m.tb.cn/h.TWp0HTd

京東:
https://3.cn/28MLBy-E

Faceit:
https://www.faceit.com/zh/players/Compl1/stream
```

&emsp;

## 🎃原始碼執行
使用原始碼執行，前提要有**Python>=3.10**環境，如果沒有請先自行安裝Python，再執行下面步驟。

1.首先拉取或手動下載本倉庫專案程式碼

```bash
git clone https://github.com/SAOJSM/LiveRecorder-1.git
```

2.進入專案資料夾，安裝依賴

```bash
cd LiveRecorder-1
python -m pip3 install -r requirements.txt
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

4.執行程式

```python
python main.py
```

其中Linux系統請使用`python3 main.py` 執行。

&emsp;
## 🐋容器執行

在執行命令之前，請確保您的機器上安裝了 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/) 

1.快速啟動

最簡單方法是執行專案中的 [docker-compose.yaml](https://github.com/SAOJSM/LiveRecorder-1/blob/master/docker-compose.yaml) 檔案，只需簡單執行以下命令：

```bash
docker-compose up
```

可選 `-d` 在後臺執行。



2.構建映象(可選)

如果你只想簡單的執行程式，則不需要做這一步。Docker映象倉庫中程式碼版本可能不是最新的，如果要執行本倉庫主分支最新程式碼，可以本地自定義構建，通過修改 [docker-compose.yaml](https://github.com/SAOJSM/LiveRecorder-1/blob/master/docker-compose.yaml) 檔案，如將映象名修改爲 `douyin-live-recorder:latest`，並取消 `# build: .` 註釋，然後再執行

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

①在docker容器內執行本程式之前，請先在配置檔案中新增要錄製的直播間地址。

②在容器內時，如果手動中斷容器執行停止錄製，會導致正在錄製的視訊檔案損壞！

**無論哪種執行方式，為避免手動中斷或者異常中斷導致錄製的視訊檔案損壞的情況，推薦使用 `ts` 格式儲存**。

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

&ensp;&ensp; [![HoratioShaw](https://github.com/HoratioShaw.png?size=50)](https://github.com/HoratioShaw)
[![nov30th](https://github.com/nov30th.png?size=50)](https://github.com/nov30th)
&emsp;

## ⏳提交日誌

- 20250321
  - 完成專案繁體中文化
  - 優化使用者介面文字顯示
  - 修正部分亂碼問題
  - 更新專案資訊及相關連結

- 20250127
  - 新增淘寶、京東、faceit直播錄製
  - 修復小紅書直播流錄製以及轉碼問題
  - 修復暢聊、VV星球、flexTV直播錄製
  - 修復批量微信直播推送
  - 新增email發送ssl和port配置
  - 新增強制轉h264配置
  - 更新ffmpeg版本
  - 重構包為非同步函式！

- 20241130
  - 新增shopee、youtube直播錄製
  - 新增支援自定義m3u8、flv地址錄製
  - 新增自定義執行指令碼，支援python、bat、bash等
  - 修復YY直播、花椒直播和小紅書直播錄製
  - 修復b站標題獲取錯誤
  - 修復log日誌錯誤
- 20241030
  - 新增嗨秀直播、vv星球直播、17Live、浪Live、SOOP、暢聊直播(原時光直播)、飄飄直播、六間房直播、樂嗨直播、花貓直播等10個平臺直播錄製
  - 修復小紅書直播錄製，支援小紅書作者主頁地址錄製直播
  - 新增支援ntfy訊息推送，以及新增支援批量推送多個地址（逗號分隔多個推送地址)
  - 修復Liveme直播錄製、twitch直播錄製
  - 新增Windows平臺一鍵停止錄製VB指令碼程式
- 20241005
  - 新增郵箱和Bark推送
  - 新增直播註釋停止錄製
  - 優化分段錄製
  - 重構部分程式碼
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
  - 修復鬥魚直播60幀錄製
  - 修復酷狗直播錄製
  - 修復TikTok部分無法解析直播源
  - 修復抖音無法錄製連麥直播
- 20240510
  - 修復部分虎牙直播間錄製錯誤
- 20240508
  - 修復花椒直播錄製
  - 更改檔案路徑解析方式 [@kaine1973](https://github.com/kaine1973)
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
  - 修復鬥魚錄製直播回放的問題
  - 新增直播源地址顯示以及輸出到日誌檔案設定
- 20240311
  - 修復海外平臺錄製bug，增加畫質選擇，增強錄製穩定性
  - 修復虎牙錄製bug (虎牙`一起看`頻道 有特殊限制，有時無法錄製)
- 20240309
  - 修復虎牙直播、小紅書直播和B站直播錄製
  - 新增5個直播平臺錄製，包括winktv、flextv、look、popkontv、twitcasting
  - 新增部分海外平臺賬號密碼配置，實現自動登錄並更新配置檔案中的cookie
  - 新增自定義配置需要使用代理錄製的平臺
  - 新增只推送開播訊息不進行錄製設定
  - 修復了一些bug
- 20240209
  - 優化AfreecaTV錄製，新增賬號密碼登錄獲取cookie以及持久儲存
  - 修復了小紅書直播因官方更新直播域名，導致無法錄製直播的問題
  - 修復了更新URL配置檔案的bug
  - 最後，祝大家新年快樂！

<details><summary>點選展開更多提交日誌</summary>

- 20240129
  - 新增貓耳FM直播錄製
- 20240127
  - 新增千度熱播直播錄製、新增pandaTV(韓國)直播錄製
  - 新增telegram直播狀態訊息推送，修復了某些bug
  - 新增自定義設定不同直播間的錄製畫質(即每個直播間錄製畫質可不同)
  - 修改錄製視訊儲存路徑為 `downloads` 資料夾，並且分平臺進行儲存。
- 20240114
  - 新增網易cc直播錄製，優化ffmpeg參數，修改AfreecaTV輸入直播地址格式
  - 修改日誌記錄器 @[iridescentGray](https://github.com/iridescentGray)
- 20240102
  - 修復Linux上執行，新增docker配置檔案
- 20231210
  - 修復錄製分段bug，修復bigo錄製檢測bug
  - 新增自定義修改錄製主播名
  - 新增AfreecaTV直播錄製，修復某些可能會發生的bug
- 20231207
  - 新增blued直播錄製，修復YY直播錄製，新增直播結束訊息推送
- 20231206
  - 新增bigo直播錄製
- 20231203
  - 新增小紅書直播錄製（全網首發），目前小紅書官方沒有切換清晰度功能，因此直播錄製也只有預設畫質
  - 小紅書錄制暫時無法循環監測，每次主播開啟直播，都要重新獲取一次鏈接
  - 獲取鏈接的方式為 將直播間轉發到微信，在微信中打開後，複製頁面的鏈接。
- 20231030
  - 本次更新只是進行修復，沒時間新增功能。
  - 歡迎各位大佬提pr 幫忙更新維護
- 20230930
  - 新增抖音從介面獲取直播流，增強穩定性
  - 修改快手獲取直播流的方式，改用從官方介面獲取
  - 祝大家中秋節快樂！
- 20230919
  - 修復了快手版本更新後錄製出錯的問題，增加了其自動獲取cookie(~~穩定性未知~~)
  - 修復了TikTok顯示正在直播但不進行錄製的問題
- 20230907
  - 修復了因抖音官方更新了版本導致的錄製出錯以及短鏈接轉換出錯
  - 修復B站無法錄製原畫視訊的bug
  - 修改了配置檔案欄位，新增各平臺自定義設定Cookie
- 20230903
  - 修復了TikTok錄製時報644無法錄製的問題
  - 新增直播狀態推送到釘釘和微信的功能，如有需要請看 [設定推送教程](https://d04vqdiqwr3.feishu.cn/docx/XFPwdDDvfobbzlxhmMYcvouynDh?from=from_copylink)
  - 最近比較忙，其他問題有時間再更新
- 20230816
  - 修復鬥魚直播（官方更新了欄位）和快手直播錄製出錯的問題
- 20230814
  - 新增B站直播錄製
  - 寫了一個線上播放M3U8和FLV視訊的網頁原始碼，打開即可食用
- 20230812
  - 新增YY直播錄製
- 20230808
  - 修復主播重新開播無法再次錄製的問題
- 20230807
  - 新增了鬥魚直播錄製
  - 修復顯示錄製完成之後會重新開始錄製的問題
- 20230805
  - 新增了虎牙直播錄製，其暫時只能用flv視訊流進行錄製
  - Web API 新增了快手和虎牙這兩個平臺的直播流解析（TikTok要代理）
- 20230804
  - 新增了快手直播錄製，優化了部分程式碼
  - 上傳了一個自動化獲取抖音直播間頁面Cookie的程式碼，可以用於錄製
- 20230803
  - 通宵更新 
  - 新增了國際版抖音TikTok的直播錄製，去除冗餘 簡化了部分程式碼
- 20230724	
  - 新增了一個通過抖音直播間地址獲取直播視訊流鏈接的API介面，上傳即可用
  </details>
  &emsp;

## 有問題可以提issue, 我會在這裡持續新增更多直播平臺的錄製 歡迎Star
#### 
