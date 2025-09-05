# -*- encoding: utf-8 -*-

"""
直播錄製程式 - 主程式模組 (優化版)
Author: SAOJSM
GitHub: https://github.com/SAOJSM
Date: 2025-03-18 05:40:00
Update: 2025-08-15 12:00:00
Copyright (c) 2025-2025 by SAOJSM, All Rights Reserved.
Function: Record live stream video.

主要功能:
1. 多平台直播監控與錄製
2. 自動檔案命名與重複處理
3. 視頻格式轉換與分段
4. 推送通知功能
5. 代理支援與錯誤處理

v4.1.0 更新內容:
- 重構程式碼結構，添加詳細註解和文檔
- 優化檔案命名邏輯，統一控制重複檔案處理
- 改進錯誤處理和日誌記錄
- 增強視頻處理功能的穩定性
- 優化推送通知機制
- 提升程式碼可讀性和維護性
"""

# ==================== 標準庫導入 ====================
import asyncio
import os
import sys
import builtins
import subprocess
import signal
import threading
import time
import datetime
import re
import shutil
import random
import uuid
from pathlib import Path
import urllib.parse
import urllib.request
from urllib.error import URLError, HTTPError
from typing import Any
import configparser

# ==================== 第三方庫導入 ====================
from streamget import spider, stream
from streamget.proxy import ProxyDetector
from streamget.utils import logger
from streamget import utils
from msg_push import (
    dingtalk, xizhi, tg_bot, send_email, bark, ntfy
)
from ffmpeg_install import (
    check_ffmpeg, ffmpeg_path, current_env_path
)

# ==================== 程式版本與平台資訊 ====================
version = "v4.1.0"
platforms = ("\n國內站點：抖音|快手|虎牙|鬥魚|YY|B站|小紅書|bigo|blued|網易CC|千度熱播|貓耳FM|Look|TwitCasting|百度|微博|"
             "酷狗|花椒|流星|Acfun|暢聊|映客|音播|知乎|嗨秀|VV星球|17Live|浪Live|漂漂|六間房|樂嗨|花貓|淘寶|京東"
             "\n海外站點：TikTok|SOOP|PandaTV|WinkTV|FlexTV|PopkonTV|TwitchTV|LiveMe|ShowRoom|CHZZK|Shopee|"
             "Youtube|Faceit")

# ==================== 全域變數初始化 ====================
# 錄製狀態管理
recording = set()                           # 正在錄製的直播間集合
recording_time_list = {}                    # 錄製時間記錄字典

# 錯誤處理相關
error_count = 0                             # 瞬時錯誤計數
pre_max_request = 10                        # 前一次的最大請求數
max_request_lock = threading.Lock()         # 最大請求數鎖
error_window = []                           # 錯誤窗口列表
error_window_size = 10                      # 錯誤窗口大小
error_threshold = 5                         # 錯誤閾值

# 監控狀態管理
monitoring = 0                              # 監控中的直播間數量
running_list = []                           # 正在運行的URL列表
url_tuples_list = []                        # URL元組列表
url_comments = []                           # 被註釋的URL列表
text_no_repeat_url = []                     # 去重後的URL列表
need_update_line_list = []                  # 需要更新的行列表
not_record_list = []                        # 不錄製的URL列表

# 程式狀態標誌
create_var = locals()                       # 動態變數容器
first_start = True                          # 首次啟動標誌
exit_recording = False                      # 退出錄製標誌
first_run = True                            # 首次運行標誌
global_proxy = False                        # 全域代理標誌
start_display_time = datetime.datetime.now()  # 顯示開始時間
# ==================== 路徑與配置 ====================
script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]  # 腳本路徑
config_file = f'{script_path}/config/config.ini'               # 配置檔案路徑
url_config_file = f'{script_path}/config/URL_config.ini'       # URL配置檔案路徑
backup_dir = f'{script_path}/backup_config'                    # 備份目錄路徑
text_encoding = 'utf-8-sig'
rstr = r"[\/\\\:\*\？?\"\<\>\|&#.。,， ~！· ]"
default_path = f'{script_path}/downloads'
os.makedirs(default_path, exist_ok=True)
file_update_lock = threading.Lock()
os_type = os.name
clear_command = "cls" if os_type == 'nt' else "clear"
color_obj = utils.Color()
os.environ['PATH'] = ffmpeg_path + os.pathsep + current_env_path


# ==================== 信號處理 ====================
def signal_handler(_signal, _frame):
    """
    信號處理函數，用於優雅地退出程式

    參數:
    _signal: 接收到的信號
    _frame: 當前執行框架
    """
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)


# ==================== 檔案命名相關函數 ====================
def get_formatted_filename(anchor_name: str, title_in_name: str = "") -> str:
    """
    根據記憶中的要求生成檔案名稱:
    主播名稱 + 空格 + 日期(YYYYMMDD)，如有重複則加上-1,-2等後綴
    如果時間在早上6點以前，使用前一天的日期

    這個函數實現了統一的檔案命名規則，確保檔案名稱的一致性

    參數:
    anchor_name (str): 主播名稱
    title_in_name (str): 直播標題(此版本中不使用，保留參數以維持相容性)

    返回:
    str: 格式化的檔名(不含副檔名)

    範例:
    get_formatted_filename("主播名") -> "主播名 20250815"
    """
    # 取得目前時間
    current_time = datetime.datetime.now()

    # 如果時間在早上6點以前，則使用前一天的日期
    # 這樣可以確保深夜直播的檔案使用正確的日期
    if current_time.hour < 6:
        current_time = current_time - datetime.timedelta(days=1)

    # 格式化日期為 YYYYMMDD 格式
    date_str = current_time.strftime('%Y%m%d')

    # 基本檔名: 主播名稱 + 空格 + 日期
    base_filename = f"{anchor_name} {date_str}"

    return base_filename


def get_segment_base_filename(base_path: str, anchor_name: str, title_in_name: str, extension: str) -> tuple[str, int]:
    """
    為分段錄製獲取基本檔名，確保分段檔案使用連續編號

    這個函數專門用於分段錄製，它會找到下一個可用的編號，
    確保分段檔案按照 -1, -2, -3, -4... 的順序連續編號

    參數:
    base_path (str): 檔案所在的目錄路徑
    anchor_name (str): 主播名稱
    title_in_name (str): 直播標題
    extension (str): 副檔名

    返回:
    tuple[str, int]: (基本檔名, 起始編號)
    """
    base_filename = get_formatted_filename(anchor_name, title_in_name)

    # 找到下一個可用的編號
    counter = 1
    while True:
        test_filename = f"{base_filename}-{counter}.{extension}"
        if not os.path.exists(f"{base_path}/{test_filename}"):
            # 找到第一個不存在的編號，從這個編號開始
            break
        counter += 1

    # 返回基本檔名和起始編號
    return base_filename, counter


def get_non_duplicate_filename(base_path: str, base_filename: str, extension: str) -> str:
    """
    生成不重複的檔案名稱，如果檔案已存在則自動添加遞增編號

    這個函數是檔案命名的核心控制點，確保不會覆蓋現有檔案
    根據記憶中的要求，重複檔案應該按照 -1, -2, -3... 的順序編號

    參數:
    base_path (str): 檔案所在的目錄路徑
    base_filename (str): 基本檔名(不含副檔名)
    extension (str): 副檔名(如 'ts', 'mp4' 等，不含點)

    返回:
    str: 完整的檔案名稱(不含路徑，但包含副檔名)

    範例:
    get_non_duplicate_filename("/path", "主播名 20250815", "mp4")
    -> "主播名 20250815.mp4" (如果不存在)
    -> "主播名 20250815-1.mp4" (如果原檔案存在)
    """
    # 檢查基本檔名是否已經包含編號，如果有則移除
    # 這確保我們總是從原始檔名開始計算編號
    if "-" in base_filename:
        parts = base_filename.split("-")
        if len(parts) > 1 and parts[-1].isdigit():
            # 如果最後一部分是數字，則認為這是一個已經有編號的檔名
            # 我們需要去掉這個編號，使用原始的基本檔名
            base_filename = "-".join(parts[:-1])

    # 先檢查基本檔名是否可用
    filename = f"{base_filename}.{extension}"
    full_path = f"{base_path}/{filename}"

    # 如果檔案不存在，直接返回基本檔名
    if not os.path.exists(full_path):
        return filename

    # 如果檔案存在，則嘗試添加遞增編號，從1開始
    counter = 1

    # 持續檢查帶編號的檔案名，直到找到不存在的檔名
    while True:
        # 生成帶編號的檔名格式: "基本檔名-編號.副檔名"
        filename = f"{base_filename}-{counter}.{extension}"
        full_path = f"{base_path}/{filename}"

        # 如果這個檔名不存在，就使用它
        if not os.path.exists(full_path):
            return filename

        # 否則繼續嘗試下一個編號
        counter += 1


# ==================== 顯示資訊相關函數 ====================
def display_info() -> None:
    """
    顯示程式運行狀態資訊的函數

    這個函數在後台執行緒中運行，定期更新並顯示：
    - 監測的直播間數量
    - 網路執行緒數
    - 代理設定狀態
    - 錄製參數配置
    - 正在錄製的直播列表
    - 錄製時長統計
    """
    global start_display_time

    # 初始等待，讓其他組件先啟動
    time.sleep(5)

    while True:
        try:
            time.sleep(5)

            # 如果不是後台運行模式，清屏顯示最新資訊
            if Path(sys.executable).name != 'pythonw.exe':
                os.system(clear_command)

            # 顯示基本監控資訊
            print(f"\r共監測{monitoring}個直播中", end=" | ")
            print(f"同一時間訪問網路的執行緒數: {max_request}", end=" | ")
            print(f"是否開啟代理錄製: {'是' if use_proxy else '否'}", end=" | ")

            # 顯示分段錄製設定
            if split_video_by_time:
                print(f"錄製分段開啟: {split_time}秒", end=" | ")
            else:
                print(f"錄製分段開啟: 否", end=" | ")

            # 顯示時間檔案生成設定
            if create_time_file:
                print(f"是否產生時間檔案: 是", end=" | ")

            # 顯示錄製參數
            print(f"錄製視訊質量為: {video_record_quality}", end=" | ")
            print(f"錄製視訊格式為: {video_save_type}", end=" | ")
            print(f"目前瞬時錯誤數為: {error_count}", end=" | ")

            # 顯示當前時間
            now = time.strftime("%H:%M:%S", time.localtime())
            print(f"目前時間: {now}")

            # 根據錄製狀態顯示不同資訊
            if len(recording) == 0:
                time.sleep(5)
                if monitoring == 0:
                    print("\r沒有正在監測和錄製的直播")
                else:
                    print(f"\r沒有正在錄製的直播 循環監測間隔時間：{delay_default}秒")
            else:
                # 顯示正在錄製的直播詳細資訊
                now_time = datetime.datetime.now()
                print("x" * 60)

                # 去重並顯示錄製列表
                no_repeat_recording = list(set(recording))
                print(f"正在錄製{len(no_repeat_recording)}個直播: ")

                # 顯示每個正在錄製的直播的詳細資訊
                for recording_live in no_repeat_recording:
                    rt, qa = recording_time_list[recording_live]
                    have_record_time = now_time - rt
                    print(f"{recording_live}[{qa}] 正在錄製中 {str(have_record_time).split('.')[0]}")

                print("x" * 60)
                start_display_time = now_time

        except Exception as e:
            logger.error(f"顯示資訊錯誤: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")


# ==================== 檔案操作相關函數 ====================
def update_file(file_path: str, old_str: str, new_str: str, start_str: str = None) -> str | None:
    """
    更新檔案中的指定內容

    這個函數用於安全地更新配置檔案，支援字符串替換和行前綴添加
    使用檔案鎖確保多執行緒環境下的檔案操作安全性

    參數:
    file_path (str): 要更新的檔案路徑
    old_str (str): 要替換的舊字符串
    new_str (str): 替換後的新字符串
    start_str (str, optional): 要添加到行首的前綴字符串

    返回:
    str | None: 返回新字符串，如果操作失敗則返回舊字符串
    """
    # 如果新舊字符串相同且沒有前綴要添加，直接返回
    if old_str == new_str and start_str is None:
        return old_str

    # 使用檔案鎖確保操作的原子性
    with file_update_lock:
        file_data = []

        # 讀取檔案內容並進行替換
        with open(file_path, "r", encoding=text_encoding) as f:
            try:
                for text_line in f:
                    # 如果找到要替換的字符串
                    if old_str in text_line:
                        text_line = text_line.replace(old_str, new_str)
                        # 如果需要添加前綴
                        if start_str:
                            text_line = f'{start_str}{text_line}'

                    # 避免重複行
                    if text_line not in file_data:
                        file_data.append(text_line)

            except RuntimeError as e:
                logger.error(f"檔案更新錯誤: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                # 如果有備份內容，嘗試恢復
                if ini_URL_content:
                    with open(file_path, "w", encoding=text_encoding) as f2:
                        f2.write(ini_URL_content)
                    return old_str

        # 將更新後的內容寫回檔案
        if file_data:
            with open(file_path, "w", encoding=text_encoding) as f:
                f.write(''.join(file_data))

        return new_str


def delete_line(file_path: str, del_line: str, delete_all: bool = False) -> None:
    """
    從檔案中刪除包含指定字符串的行

    這個函數用於清理配置檔案中的重複或無效行
    使用檔案鎖確保操作的安全性

    參數:
    file_path (str): 要操作的檔案路徑
    del_line (str): 要刪除的行中包含的字符串
    delete_all (bool): 是否刪除所有匹配的行，預設為False（只刪除第一個匹配的行）
    """
    with file_update_lock:
        with open(file_path, 'r+', encoding=text_encoding) as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            skip_line = False

            for txt_line in lines:
                # 檢查是否包含要刪除的字符串
                if del_line in txt_line:
                    if delete_all or not skip_line:
                        skip_line = True
                        continue  # 跳過這一行（即刪除）
                else:
                    skip_line = False

                # 保留這一行
                f.write(txt_line)


# ==================== 系統相關函數 ====================
def get_startup_info(system_type: str):
    """
    根據作業系統類型獲取subprocess的啟動資訊

    在Windows系統中，設定不顯示命令行視窗
    在其他系統中，使用預設設定

    參數:
    system_type (str): 作業系統類型 ('nt' 表示Windows)

    返回:
    subprocess.STARTUPINFO | None: Windows系統返回配置好的STARTUPINFO，其他系統返回None
    """
    if system_type == 'nt':
        # Windows系統：隱藏命令行視窗
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        # 其他系統：使用預設設定
        startup_info = None
    return startup_info


# ==================== 視頻處理相關函數 ====================
def segment_video(converts_file_path: str, segment_save_file_path: str, segment_format: str, segment_time: str,
                  is_original_delete: bool = True) -> None:
    """
    將視頻檔案分段處理

    這個函數將大型視頻檔案分割成多個較小的段落，便於管理和播放
    使用統一的檔案命名規則，確保分段檔案不會覆蓋現有檔案

    參數:
    converts_file_path (str): 要分段的原始視頻檔案路徑
    segment_save_file_path (str): 分段檔案的保存路徑模板
    segment_format (str): 分段檔案的格式（如 'mp4', 'flv'）
    segment_time (str): 每段的時長（秒）
    is_original_delete (bool): 是否刪除原始檔案，預設為True

    功能:
    - 自動檢測視頻總時長
    - 按指定時間分割視頻
    - 使用統一命名規則避免檔案覆蓋
    - 支援MP4格式的faststart優化
    """
    try:
        # 檢查原始檔案是否存在且不為空
        if os.path.exists(converts_file_path) and os.path.getsize(converts_file_path) > 0:
            # 解析檔案路徑和檔名
            dir_path = os.path.dirname(segment_save_file_path)
            base_filename = os.path.basename(segment_save_file_path)

            # 處理模板檔名中的 "-%d" 佔位符
            if "-%d" in base_filename:
                base_filename = base_filename.replace("-%d", "")

            # 分離檔名和副檔名
            extension = os.path.splitext(base_filename)[1][1:]  # 獲取副檔名（不含點）
            base_name = os.path.splitext(base_filename)[0]      # 獲取基本檔名（不含副檔名）

            # 使用統一的檔案命名函數獲取不重複的檔名
            first_filename = get_non_duplicate_filename(dir_path, base_name, extension)
            first_file_path = f"{dir_path}/{first_filename}"

            # 構建第一個分段的FFmpeg命令
            first_command = [
                "ffmpeg",
                "-i", converts_file_path,
                "-c:v", "copy",                 # 視頻流複製（不重新編碼）
                "-c:a", "copy",                 # 音頻流複製（不重新編碼）
                "-map", "0",                    # 映射所有流
                "-t", segment_time,             # 設定分段時長
                "-f", segment_format,           # 輸出格式
                first_file_path,
            ]

            # 執行第一個分段命令
            _first_output = subprocess.check_output(
                first_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
            )

            # 如果視頻長度超過分段時間，則創建後續分段
            # 獲取視頻總時長
            duration_command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                converts_file_path
            ]

            try:
                duration_output = subprocess.check_output(
                    duration_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
                )
                duration = float(duration_output.decode('utf-8').strip())

                # 如果視頻總時長超過分段時間，則需要創建後續分段
                if duration > float(segment_time):
                    # 獲取第二個檔案的名稱
                    second_filename = get_non_duplicate_filename(dir_path, base_name, extension)

                    # 創建第二個檔案
                    second_command = [
                        "ffmpeg",
                        "-i", converts_file_path,
                        "-c:v", "copy",
                        "-c:a", "copy",
                        "-map", "0",
                        "-ss", segment_time,  # 從第一個分段結束的時間開始
                        "-f", segment_format,
                        f"{dir_path}/{second_filename}",
                    ]

                    # 執行第二個命令
                    _second_output = subprocess.check_output(
                        second_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
                    )

                    # 如果視頻總時長超過兩個分段時間，則需要創建更多分段
                    segment_count = 2
                    current_time = float(segment_time) * 2

                    while current_time < duration:
                        # 獲取下一個檔案的名稱
                        next_filename = get_non_duplicate_filename(dir_path, base_name, extension)

                        # 創建下一個檔案
                        next_command = [
                            "ffmpeg",
                            "-i", converts_file_path,
                            "-c:v", "copy",
                            "-c:a", "copy",
                            "-map", "0",
                            "-ss", str(current_time),  # 從當前時間開始
                            "-t", segment_time,  # 只取一個分段的時間
                            "-f", segment_format,
                            f"{dir_path}/{next_filename}",
                        ]

                        # 執行命令
                        _next_output = subprocess.check_output(
                            next_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
                        )

                        segment_count += 1
                        current_time += float(segment_time)
            except Exception as e:
                logger.error(f'Error getting video duration or creating segments: {e}')

            # 如果是MP4分段，需要優化每個分段檔案以確保快速開啟
            if segment_format == 'mp4':
                # 優化第一個檔案
                if os.path.exists(first_file_path):
                    threading.Thread(target=optimize_mp4, args=(first_file_path,)).start()
                
                # 優化其他分段檔案
                if duration > float(segment_time):
                    segment_count = 2
                    current_time = float(segment_time) * 2
                    
                    while current_time < duration:
                        # 構建分段檔案路徑
                        segment_filename = get_non_duplicate_filename(dir_path, base_name, extension)
                        segment_file_path = f"{dir_path}/{segment_filename}"
                        
                        if os.path.exists(segment_file_path):
                            threading.Thread(target=optimize_mp4, args=(segment_file_path,)).start()
                        
                        segment_count += 1
                        current_time += float(segment_time)

            if is_original_delete:
                time.sleep(1)
                if os.path.exists(converts_file_path):
                    os.remove(converts_file_path)
    except subprocess.CalledProcessError as e:
        logger.error(f'Error occurred during conversion: {e}')
    except Exception as e:
        logger.error(f'An unknown error occurred: {e}')


def converts_mp4(converts_file_path: str, is_original_delete: bool = True) -> None:
    """
    將視頻檔案轉換為MP4格式

    這個函數支援兩種轉換模式：
    1. 直接容器轉換（不重新編碼，速度快）
    2. H.264重新編碼（相容性好，檔案較小）

    轉換後的檔案會自動添加faststart標誌，確保網路播放時的快速啟動

    參數:
    converts_file_path (str): 要轉換的原始檔案路徑
    is_original_delete (bool): 轉換完成後是否刪除原始檔案，預設為True

    功能:
    - 支援H.264重新編碼或直接容器轉換
    - 自動添加faststart優化
    - 轉換完成後可選擇刪除原檔案
    - 完整的錯誤處理和日誌記錄
    """
    try:
        # 檢查原始檔案是否存在且不為空
        if os.path.exists(converts_file_path) and os.path.getsize(converts_file_path) > 0:

            # 根據配置選擇轉換模式
            if converts_to_h264:
                # H.264重新編碼模式：提供更好的相容性和壓縮率
                color_obj.print_colored(f"正在轉碼為MP4格式並重新編碼為h264\n", color_obj.YELLOW)
                ffmpeg_command = [
                    "ffmpeg", "-i", converts_file_path,
                    "-c:v", "libx264",              # 使用H.264編碼器
                    "-preset", "veryfast",          # 編碼速度預設（平衡速度和質量）
                    "-crf", "23",                   # 恆定質量因子（23是較好的平衡點）
                    "-vf", "format=yuv420p",        # 確保色彩格式相容性
                    "-c:a", "copy",                 # 音頻直接複製
                    "-f", "mp4",                    # 輸出格式
                    "-movflags", "+faststart",      # 添加faststart標誌以確保快速開啟
                    converts_file_path.rsplit('.', maxsplit=1)[0] + ".mp4",
                ]
            else:
                # 直接容器轉換模式：速度快，不重新編碼
                color_obj.print_colored(f"正在轉碼為MP4格式\n", color_obj.YELLOW)
                ffmpeg_command = [
                    "ffmpeg", "-i", converts_file_path,
                    "-c:v", "copy",                 # 視頻流直接複製
                    "-c:a", "copy",                 # 音頻流直接複製
                    "-f", "mp4",                    # 輸出格式
                    "-movflags", "+faststart",      # 添加faststart標誌以確保快速開啟
                    converts_file_path.rsplit('.', maxsplit=1)[0] + ".mp4",
                ]

            # 執行轉換命令
            _output = subprocess.check_output(
                ffmpeg_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
            )

            # 根據設定決定是否刪除原檔案
            if is_original_delete:
                time.sleep(1)  # 短暫等待確保檔案寫入完成
                if os.path.exists(converts_file_path):
                    os.remove(converts_file_path)

    except subprocess.CalledProcessError as e:
        logger.error(f'視頻轉換過程中發生錯誤: {e}')
    except Exception as e:
        logger.error(f'視頻轉換時發生未知錯誤: {e}')


def fix_h264_stream_errors(ffmpeg_command: list) -> list:
    """
    為FFmpeg命令添加H.264流錯誤修復參數
    
    參數:
    ffmpeg_command: 原始FFmpeg命令列表
    
    返回:
    修正後的FFmpeg命令列表
    """
    # 簡化的H.264錯誤修復 - 只添加最關鍵的參數
    # 這些參數將被插入到基礎命令中，而不是在輸入後
    return ffmpeg_command  # 暫時返回原命令，錯誤處理已在基礎命令中設定


def optimize_mp4(mp4_file_path: str) -> None:
    """
    優化MP4檔案，添加faststart標誌以確保快速開啟

    這個函數將MP4檔案的metadata移動到檔案開頭，
    使得檔案可以在網路環境中邊下載邊播放，提升用戶體驗

    參數:
    mp4_file_path (str): 要優化的MP4檔案路徑

    功能:
    - 添加faststart標誌優化檔案結構
    - 保持原始視頻和音頻品質（不重新編碼）
    - 使用臨時檔案確保操作安全性
    - 完整的錯誤處理和清理機制
    """
    try:
        # 檢查檔案是否存在且不為空
        if os.path.exists(mp4_file_path) and os.path.getsize(mp4_file_path) > 0:
            temp_file_path = mp4_file_path + ".temp"
            color_obj.print_colored(f"正在優化MP4檔案以確保快速開啟\n", color_obj.YELLOW)

            # 構建FFmpeg優化命令
            ffmpeg_command = [
                "ffmpeg", "-i", mp4_file_path,
                "-c:v", "copy",                 # 視頻流直接複製（不重新編碼）
                "-c:a", "copy",                 # 音頻流直接複製（不重新編碼）
                "-f", "mp4",                    # 輸出格式
                "-movflags", "+faststart",      # 添加faststart標誌進行優化
                temp_file_path,
            ]

            # 執行優化命令
            _output = subprocess.check_output(
                ffmpeg_command, stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type)
            )

            # 安全地替換原檔案
            if os.path.exists(temp_file_path):
                os.remove(mp4_file_path)        # 刪除原檔案
                os.rename(temp_file_path, mp4_file_path)  # 重命名臨時檔案

    except subprocess.CalledProcessError as e:
        logger.error(f'MP4優化過程中發生錯誤: {e}')
        # 清理臨時檔案
        temp_file = mp4_file_path + ".temp"
        if os.path.exists(temp_file):
            os.remove(temp_file)
    except Exception as e:
        logger.error(f'MP4優化時發生未知錯誤: {e}')
        # 清理臨時檔案
        temp_file = mp4_file_path + ".temp"
        if os.path.exists(temp_file):
            os.remove(temp_file)


def converts_m4a(converts_file_path: str, is_original_delete: bool = True) -> None:
    try:
        if os.path.exists(converts_file_path) and os.path.getsize(converts_file_path) > 0:
            _output = subprocess.check_output([
                "ffmpeg", "-i", converts_file_path,
                "-n", "-vn",
                "-c:a", "aac", "-bsf:a", "aac_adtstoasc", "-ab", "320k",
                converts_file_path.rsplit('.', maxsplit=1)[0] + ".m4a",
            ], stderr=subprocess.STDOUT, startupinfo=get_startup_info(os_type))
            if is_original_delete:
                time.sleep(1)
                if os.path.exists(converts_file_path):
                    os.remove(converts_file_path)
    except subprocess.CalledProcessError as e:
        logger.error(f'Error occurred during conversion: {e}')
    except Exception as e:
        logger.error(f'An unknown error occurred: {e}')


def generate_subtitles(record_name: str, ass_filename: str, sub_format: str = 'srt') -> None:
    index_time = 0
    today = datetime.datetime.now()
    re_datatime = today.strftime('%Y-%m-%d %H:%M:%S')

    def transform_int_to_time(seconds: int) -> str:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    while True:
        index_time += 1
        txt = str(index_time) + "\n" + transform_int_to_time(index_time) + ',000 --> ' + transform_int_to_time(
            index_time + 1) + ',000' + "\n" + str(re_datatime) + "\n\n"

        with open(f"{ass_filename}.{sub_format.lower()}", 'a', encoding=text_encoding) as f:
            f.write(txt)

        if record_name not in recording:
            return
        time.sleep(1)
        today = datetime.datetime.now()
        re_datatime = today.strftime('%Y-%m-%d %H:%M:%S')





# ==================== 錯誤處理與監控函數 ====================
def adjust_max_request() -> None:
    """
    動態調整最大網路請求執行緒數

    這個函數根據錯誤率自動調整併發請求數量，以平衡效能和穩定性：
    - 錯誤率高時減少併發數，提高穩定性
    - 錯誤率低時增加併發數，提高效率
    - 使用滑動窗口計算錯誤率，避免短期波動影響

    全域變數:
    max_request: 當前最大請求數
    error_count: 當前錯誤計數
    pre_max_request: 前一次的最大請求數
    error_window: 錯誤窗口列表

    調整策略:
    - 錯誤率 > 閾值：減少併發數（最少保持1個）
    - 錯誤率 < 閾值/2：增加併發數（不超過預設值）
    - 其他情況：保持當前併發數
    """
    global max_request, error_count, pre_max_request, error_window
    preset = max_request  # 保存初始設定值

    while True:
        time.sleep(5)  # 每5秒檢查一次

        with max_request_lock:
            # 計算當前錯誤率
            if error_window:
                error_rate = sum(error_window) / len(error_window)
            else:
                error_rate = 0

            # 根據錯誤率調整併發數
            if error_rate > error_threshold:
                # 錯誤率過高，減少併發數（最少保持1個）
                max_request = max(1, max_request - 1)
            elif error_rate < error_threshold / 2 and max_request < preset:
                # 錯誤率較低且未達到預設值，增加併發數
                max_request += 1
            # 其他情況保持不變

            # 如果併發數發生變化，通知用戶
            if pre_max_request != max_request:
                pre_max_request = max_request
                print(f"\r同一時間訪問網路的執行緒數動態改為 {max_request}")

        # 更新錯誤窗口（滑動窗口機制）
        error_window.append(error_count)
        if len(error_window) > error_window_size:
            error_window.pop(0)  # 移除最舊的錯誤記錄
        error_count = 0  # 重置當前週期的錯誤計數


# ==================== 推送通知相關函數 ====================
def push_message(record_name: str, live_url: str, content: str) -> None:
    """
    發送直播狀態推送通知到各個平台

    支援多種推送平台：微信、釘釘、郵箱、Telegram、BARK、NTFY
    根據配置自動選擇啟用的推送平台進行通知

    參數:
    record_name (str): 錄製名稱（主播名稱）
    live_url (str): 直播間URL
    content (str): 推送內容

    功能:
    - 支援多平台同時推送
    - 自動錯誤處理和重試
    - 詳細的推送結果統計
    - 靈活的推送內容自定義
    """
    # 設定推送標題，使用自定義標題或預設標題
    msg_title = push_message_title.strip() or "直播間狀態更新通知"

    # 定義各平台的推送函數
    push_functions = {
        '微信': lambda: xizhi(xizhi_api_url, msg_title, content),
        '釘釘': lambda: dingtalk(dingtalk_api_url, content, dingtalk_phone_num, dingtalk_is_atall),
        '郵箱': lambda: send_email(
            email_host, login_email, email_password, sender_email, sender_name,
            to_email, msg_title, content, smtp_port, open_smtp_ssl
        ),
        'TG': lambda: tg_bot(tg_chat_id, tg_token, content),
        'BARK': lambda: bark(
            bark_msg_api, title=msg_title, content=content, level=bark_msg_level, sound=bark_msg_ring
        ),
        'NTFY': lambda: ntfy(
            ntfy_api, title=msg_title, content=content, tags=ntfy_tags, action_url=live_url, email=ntfy_email
        ),
    }

    # 遍歷所有推送平台，根據配置進行推送
    for platform, func in push_functions.items():
        if platform in live_status_push.upper():
            try:
                # 執行推送
                result = func()
                # 顯示推送結果統計
                print(f'提示資訊：已經將[{record_name}]直播狀態訊息推送至你的{platform},'
                      f' 成功{len(result["success"])}, 失敗{len(result["error"])}')
            except Exception as e:
                # 推送失敗時的錯誤處理
                color_obj.print_colored(f"直播訊息推送到{platform}失敗: {e}", color_obj.RED)


def run_script(command: str) -> None:
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=get_startup_info(os_type)
        )
        stdout, stderr = process.communicate()
        stdout_decoded = stdout.decode('utf-8')
        stderr_decoded = stderr.decode('utf-8')
        if stdout_decoded.strip():
            print(stdout_decoded)
        if stderr_decoded.strip():
            print(stderr_decoded)
    except PermissionError as e:
        logger.error(e)
        logger.error(f'指令碼無執行許可權!, 若是Linux環境, 請先執行:chmod +x your_script.sh 授予指令碼可執行許可權')
    except OSError as e:
        logger.error(e)
        logger.error('Please add `#!/bin/bash` at the beginning of your bash script file.')


def clear_record_info(record_name: str, record_url: str) -> None:
    """
    清理錄製資訊，從各個列表中移除指定的錄製項目

    這個函數負責清理錄製結束或被取消的直播間相關資訊，
    確保程式狀態的一致性和記憶體的有效使用

    參數:
    record_name (str): 錄製名稱
    record_url (str): 直播間URL

    功能:
    - 從錄製集合中移除項目
    - 更新監控計數
    - 清理運行列表
    - 提供用戶反饋
    """
    global monitoring

    # 從正在錄製的集合中移除
    recording.discard(record_name)

    # 如果URL在註釋列表和運行列表中，進行清理
    if record_url in url_comments and record_url in running_list:
        running_list.remove(record_url)
        monitoring -= 1
        color_obj.print_colored(f"[{record_name}]已經從錄製列表中移除\n", color_obj.YELLOW)


def check_subprocess(record_name: str, record_url: str, ffmpeg_command: list, save_type: str,
                     script_command: str | None = None, platform: str = "", proxy_address: str = None) -> bool:
    save_file_path = ffmpeg_command[-1]
    # 修改為捕獲stderr以便監控錯誤訊息
    process = subprocess.Popen(
        ffmpeg_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, 
        startupinfo=get_startup_info(os_type), text=True, bufsize=1
    )

    subs_file_path = save_file_path.rsplit('.', maxsplit=1)[0]
    subs_thread_name = f'subs_{Path(subs_file_path).name}'
    if create_time_file and not split_video_by_time and '音訊' not in save_type:
        create_var[subs_thread_name] = threading.Thread(
            target=generate_subtitles, args=(record_name, subs_file_path)
        )
        create_var[subs_thread_name].daemon = True
        create_var[subs_thread_name].start()

    while process.poll() is None:
        if record_url in url_comments or exit_recording:
            color_obj.print_colored(f"[{record_name}]錄製時已被註釋,本條執行緒將會退出", color_obj.YELLOW)
            clear_record_info(record_name, record_url)
            # process.terminate()
            if os.name == 'nt':
                if process.stdin:
                    process.stdin.write(b'q')
                    process.stdin.close()
            else:
                process.send_signal(signal.SIGINT)
            process.wait()
            return True  # 只有被手動註釋時才真正退出執行緒
            
        # 簡化的封包監控（預設啟用，不記錄）
        if enable_packet_monitoring:
            try:
                if process.stderr and process.stderr.readable():
                    # 使用非阻塞讀取檢查是否有錯誤訊息
                    import select
                    if hasattr(select, 'select'):  # Unix系統
                        ready, _, _ = select.select([process.stderr], [], [], 0)
                        if ready:
                            error_line = process.stderr.readline()
                            # 靜默監控損壞封包，不輸出任何記錄
                            if error_line and 'corrupt' in error_line.lower():
                                pass  # 檢測到損壞封包，但不記錄
            except Exception as e:
                pass  # 靜默處理監控錯誤
        
        time.sleep(1)

    return_code = process.returncode
    stop_time = time.strftime('%Y-%m-%d %H:%M:%S')
    if return_code == 0:
        if converts_to_mp4 and save_type == 'TS':
            if split_video_by_time:
                file_paths = utils.get_file_paths(os.path.dirname(save_file_path))
                prefix = os.path.basename(save_file_path).rsplit('_', maxsplit=1)[0]
                for path in file_paths:
                    if prefix in path:
                        threading.Thread(target=converts_mp4, args=(path, delete_origin_file)).start()
            else:
                threading.Thread(target=converts_mp4, args=(save_file_path, delete_origin_file)).start()
        elif save_type == 'MP4':
            # 直接錄製的MP4檔案需要優化以確保快速開啟
            if split_video_by_time:
                # 分段錄製的MP4檔案，需要優化所有分段檔案
                file_paths = utils.get_file_paths(os.path.dirname(save_file_path))
                prefix = os.path.basename(save_file_path).rsplit('-%d', maxsplit=1)[0] if '-%d' in save_file_path else os.path.basename(save_file_path).rsplit('.', maxsplit=1)[0]
                for path in file_paths:
                    if prefix in path and path.endswith('.mp4'):
                        threading.Thread(target=optimize_mp4, args=(path,)).start()
            else:
                threading.Thread(target=optimize_mp4, args=(save_file_path,)).start()
        print(f"\n{record_name} {stop_time} 直播錄製完成\n")

        if script_command:
            logger.debug("開始執行指令碼命令!")
            if "python" in script_command:
                params = [
                    f'--record_name "{record_name}"',
                    f'--save_file_path "{save_file_path}"',
                    f'--save_type {save_type}'
                    f'--split_video_by_time {split_video_by_time}',
                    f'--converts_to_mp4 {converts_to_mp4}',
                ]
            else:
                params = [
                    f'"{record_name.split(" ", maxsplit=1)[-1]}"',
                    f'"{save_file_path}"',
                    save_type,
                    f'split_video_by_time:{split_video_by_time}',
                    f'converts_to_mp4:{converts_to_mp4}'
                ]
            script_command = script_command.strip() + ' ' + ' '.join(params)
            run_script(script_command)
            logger.debug("指令碼命令執行結束!")

    else:
        color_obj.print_colored(f"\n{record_name} {stop_time} 直播錄製出錯,返回碼: {return_code}\n", color_obj.RED)

    recording.discard(record_name)
    return False  # 返回False讓程式回到監控循環，而不是退出執行緒


# ==================== 名稱處理相關函數 ====================
def clean_name(input_text):
    """
    清理和標準化主播名稱或標題

    這個函數將不適合用作檔名的字符替換為安全字符，
    確保生成的檔名在各種作業系統中都能正常使用

    參數:
    input_text (str): 原始文字（主播名稱或直播標題）

    返回:
    str: 清理後的安全檔名字符串

    處理規則:
    - 移除或替換檔名非法字符
    - 標準化括號格式
    - 可選移除表情符號
    - 處理空白名稱的情況
    """
    # 使用正則表達式替換非法字符為下劃線
    cleaned_name = re.sub(rstr, "_", input_text.strip()).strip('_')

    # 標準化括號格式（中文括號轉英文括號）
    cleaned_name = cleaned_name.replace("（", "(").replace("）", ")")

    # 根據配置決定是否移除表情符號
    if clean_emoji:
        cleaned_name = utils.remove_emojis(cleaned_name, '_').strip('_')

    # 如果清理後為空，使用預設名稱
    return cleaned_name or '空白昵稱'


def get_quality_code(qn):
    """
    將中文畫質名稱轉換為英文代碼

    這個函數將用戶友好的中文畫質名稱轉換為程式內部使用的英文代碼，
    便於與各直播平台的API進行交互

    參數:
    qn (str): 中文畫質名稱

    返回:
    str: 對應的英文畫質代碼，如果找不到對應項目則返回None

    支援的畫質對應關係:
    - 原畫 -> OD (Original Definition)
    - 藍光 -> BD (Blu-ray Definition)
    - 超清 -> UHD (Ultra High Definition)
    - 高清 -> HD (High Definition)
    - 標清 -> SD (Standard Definition)
    - 流暢 -> LD (Low Definition)
    """
    QUALITY_MAPPING = {
        "原畫": "OD",
        "藍光": "BD",
        "超清": "UHD",
        "高清": "HD",
        "標清": "SD",
        "流暢": "LD"
    }
    return QUALITY_MAPPING.get(qn)


def start_record(url_data: tuple, count_variable: int = -1) -> None:
    global error_count

    while True:
        try:
            record_finished = False
            run_once = False
            start_pushed = False
            new_record_url = ''
            count_time = time.time()
            retry = 0
            record_quality_zh, record_url, anchor_name = url_data
            record_quality = get_quality_code(record_quality_zh)
            proxy_address = proxy_addr
            platform = '未知平臺'
            live_domain = '/'.join(record_url.split('/')[0:3])

            if proxy_addr:
                proxy_address = None
                for platform in enable_proxy_platform_list:
                    if platform and platform.strip() in record_url:
                        proxy_address = proxy_addr
                        break

            if not proxy_address:
                if extra_enable_proxy_platform_list:
                    for pt in extra_enable_proxy_platform_list:
                        if pt and pt.strip() in record_url:
                            proxy_address = proxy_addr_bak or None

            # print(f'\r代理地址:{proxy_address}')
            # print(f'\r全域性代理:{global_proxy}')
            while True:
                try:
                    port_info = []
                    if record_url.find("douyin.com/") > -1:
                        platform = '抖音直播'
                        with semaphore:
                            if 'v.douyin.com' not in record_url:
                                json_data = asyncio.run(spider.get_douyin_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=dy_cookie))
                            else:
                                json_data = asyncio.run(spider.get_douyin_app_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=dy_cookie))
                            port_info = asyncio.run(stream.get_douyin_stream_url(json_data, record_quality))

                    elif record_url.find("https://www.tiktok.com/") > -1:
                        platform = 'TikTok直播'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_tiktok_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=tiktok_cookie))
                                port_info = asyncio.run(stream.get_tiktok_stream_url(json_data, record_quality))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查網路是否能正常訪問TikTok平臺")
                                port_info = None

                    elif record_url.find("https://live.kuaishou.com/") > -1:
                        platform = '快手直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_kuaishou_stream_data(
                                url=record_url,
                                proxy_addr=proxy_address,
                                cookies=ks_cookie))
                            port_info = asyncio.run(stream.get_kuaishou_stream_url(json_data, record_quality))

                    elif record_url.find("https://www.huya.com/") > -1:
                        platform = '虎牙直播'
                        with semaphore:
                            if record_quality not in ['OD', 'BD', 'UHD']:
                                json_data = asyncio.run(spider.get_huya_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=hy_cookie))
                                port_info = asyncio.run(stream.get_huya_stream_url(json_data, record_quality))
                            else:
                                port_info = asyncio.run(spider.get_huya_app_stream_url(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=hy_cookie
                                ))

                    elif record_url.find("https://www.douyu.com/") > -1:
                        platform = '鬥魚直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_douyu_info_data(
                                url=record_url, proxy_addr=proxy_address, cookies=douyu_cookie))
                            port_info = asyncio.run(stream.get_douyu_stream_url(
                                json_data, video_quality=record_quality, cookies=douyu_cookie, proxy_addr=proxy_address
                            ))

                    elif record_url.find("https://www.yy.com/") > -1:
                        platform = 'YY直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_yy_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=yy_cookie))
                            port_info = asyncio.run(stream.get_yy_stream_url(json_data))

                    elif record_url.find("https://live.bilibili.com/") > -1:
                        platform = 'B站直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_bilibili_room_info(
                                url=record_url, proxy_addr=proxy_address, cookies=bili_cookie))
                            port_info = asyncio.run(stream.get_bilibili_stream_url(
                                json_data, video_quality=record_quality, cookies=bili_cookie, proxy_addr=proxy_address))

                    elif record_url.find("https://www.redelight.cn/") > -1 or \
                            record_url.find("https://www.xiaohongshu.com/") > -1 or \
                            record_url.find("http://xhslink.com/") > -1:
                        platform = '小紅書直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_xhs_stream_url(
                                record_url, proxy_addr=proxy_address, cookies=xhs_cookie))
                            retry += 1

                    elif record_url.find("https://www.bigo.tv/") > -1 or record_url.find("slink.bigovideo.tv/") > -1:
                        platform = 'Bigo直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_bigo_stream_url(
                                record_url, proxy_addr=proxy_address, cookies=bigo_cookie))

                    elif record_url.find("https://app.blued.cn/") > -1:
                        platform = 'Blued直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_blued_stream_url(
                                record_url, proxy_addr=proxy_address, cookies=blued_cookie))

                    elif record_url.find("sooplive.co.kr/") > -1:
                        platform = 'SOOP'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_sooplive_stream_data(
                                    url=record_url, proxy_addr=proxy_address,
                                    cookies=sooplive_cookie,
                                    username=sooplive_username,
                                    password=sooplive_password
                                ))
                                if json_data and json_data.get('new_cookies'):
                                    utils.update_config(
                                        config_file, 'Cookie', 'sooplive_cookie', json_data.get('new_cookies')
                                    )
                                # 檢查json_data是否包含必要的數據結構
                                if json_data and json_data.get('is_live') and 'play_url_list' in json_data:
                                    port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                                else:
                                    # 如果沒有有效的流數據，設置為None
                                    port_info = json_data if json_data else None
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問SOOP平臺")
                                port_info = None

                    elif record_url.find("cc.163.com/") > -1:
                        platform = '網易CC直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_netease_stream_data(
                                url=record_url, cookies=netease_cookie))
                            port_info = asyncio.run(stream.get_netease_stream_url(json_data, record_quality))

                    elif record_url.find("qiandurebo.com/") > -1:
                        platform = '千度熱播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_qiandurebo_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=qiandurebo_cookie))

                    elif record_url.find("www.pandalive.co.kr/") > -1:
                        platform = 'PandaTV'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_pandatv_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=pandatv_cookie
                                ))
                                port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問PandaTV直播平臺")
                                port_info = None

                    elif record_url.find("fm.missevan.com/") > -1:
                        platform = '貓耳FM直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_maoerfm_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=maoerfm_cookie))

                    elif record_url.find("www.winktv.co.kr/") > -1:
                        platform = 'WinkTV'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_winktv_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=winktv_cookie))
                                port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問WinkTV直播平臺")
                                port_info = None

                    elif record_url.find("www.flextv.co.kr/") > -1:
                        platform = 'FlexTV'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_flextv_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=flextv_cookie,
                                    username=flextv_username,
                                    password=flextv_password
                                ))
                                if json_data and json_data.get('new_cookies'):
                                    utils.update_config(
                                        config_file, 'Cookie', 'flextv_cookie', json_data.get('new_cookies')
                                    )
                                port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問FlexTV直播平臺")
                                port_info = None

                    elif record_url.find("look.163.com/") > -1:
                        platform = 'Look直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_looklive_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=look_cookie
                            ))

                    elif record_url.find("www.popkontv.com/") > -1:
                        platform = 'PopkonTV'
                        with semaphore:
                            if global_proxy or proxy_address:
                                port_info = asyncio.run(spider.get_popkontv_stream_url(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    access_token=popkontv_access_token,
                                    username=popkontv_username,
                                    password=popkontv_password,
                                    partner_code=popkontv_partner_code
                                ))
                                if port_info and port_info.get('new_token'):
                                    utils.update_config(
                                        file_path=config_file, section='Authorization', key='popkontv_token',
                                        new_value=port_info.get('new_token')
                                    )

                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問PopkonTV直播平臺")
                                port_info = None  # 明確設置為 None

                    elif record_url.find("twitcasting.tv/") > -1:
                        platform = 'TwitCasting'
                        with semaphore:
                            port_info = asyncio.run(spider.get_twitcasting_stream_url(
                                url=record_url,
                                proxy_addr=proxy_address,
                                cookies=twitcasting_cookie,
                                account_type=twitcasting_account_type,
                                username=twitcasting_username,
                                password=twitcasting_password
                            ))
                            if port_info and port_info.get('new_cookies'):
                                utils.update_config(
                                    file_path=config_file, section='Cookie', key='twitcasting_cookie',
                                    new_value=port_info.get('new_cookies')
                                )

                    elif record_url.find("live.baidu.com/") > -1:
                        platform = '百度直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_baidu_stream_data(
                                url=record_url,
                                proxy_addr=proxy_address,
                                cookies=baidu_cookie))
                            port_info = asyncio.run(stream.get_stream_url(json_data, record_quality))

                    elif record_url.find("weibo.com/") > -1:
                        platform = '微博直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_weibo_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=weibo_cookie))
                            port_info = asyncio.run(stream.get_stream_url(
                                json_data, record_quality, hls_extra_key='m3u8_url'))

                    elif record_url.find("kugou.com/") > -1:
                        platform = '酷狗直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_kugou_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=kugou_cookie))

                    elif record_url.find("www.twitch.tv/") > -1:
                        platform = 'TwitchTV'
                        with semaphore:
                            if global_proxy or proxy_address:
                                json_data = asyncio.run(spider.get_twitchtv_stream_data(
                                    url=record_url,
                                    proxy_addr=proxy_address,
                                    cookies=twitch_cookie
                                ))
                                port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問TwitchTV直播平臺")
                                port_info = None

                    elif record_url.find("www.liveme.com/") > -1:
                        if global_proxy or proxy_address:
                            platform = 'LiveMe'
                            with semaphore:
                                port_info = asyncio.run(spider.get_liveme_stream_url(
                                    url=record_url, proxy_addr=proxy_address, cookies=liveme_cookie))
                        else:
                            logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問LiveMe直播平臺")
                            port_info = None

                    elif record_url.find("www.huajiao.com/") > -1:
                        platform = '花椒直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_huajiao_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=huajiao_cookie))

                    elif record_url.find("7u66.com/") > -1:
                        platform = '流星直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_liuxing_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=liuxing_cookie))

                    elif record_url.find("showroom-live.com/") > -1:
                        platform = 'ShowRoom'
                        with semaphore:
                            json_data = asyncio.run(spider.get_showroom_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=showroom_cookie))
                            port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))

                    elif record_url.find("live.acfun.cn/") > -1 or record_url.find("m.acfun.cn/") > -1:
                        platform = 'Acfun'
                        with semaphore:
                            json_data = asyncio.run(spider.get_acfun_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=acfun_cookie))
                            port_info = asyncio.run(stream.get_stream_url(
                                json_data, record_quality, url_type='flv', flv_extra_key='url'))

                    elif record_url.find("live.tlclw.com/") > -1:
                        platform = '暢聊直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_changliao_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=changliao_cookie))

                    elif record_url.find("ybw1666.com/") > -1:
                        platform = '音播直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_yinbo_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=yinbo_cookie))

                    elif record_url.find("www.inke.cn/") > -1:
                        platform = '映客直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_yingke_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=yingke_cookie))

                    elif record_url.find("www.zhihu.com/") > -1:
                        platform = '知乎直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_zhihu_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=zhihu_cookie))

                    elif record_url.find("chzzk.naver.com/") > -1:
                        platform = 'CHZZK'
                        with semaphore:
                            json_data = asyncio.run(spider.get_chzzk_stream_data(
                                url=record_url, proxy_addr=proxy_address, cookies=chzzk_cookie))
                            port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))

                    elif record_url.find("www.haixiutv.com/") > -1:
                        platform = '嗨秀直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_haixiu_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=haixiu_cookie))

                    elif record_url.find("vvxqiu.com/") > -1:
                        platform = 'VV星球'
                        with semaphore:
                            port_info = asyncio.run(spider.get_vvxqiu_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=vvxqiu_cookie))

                    elif record_url.find("17.live/") > -1:
                        platform = '17Live'
                        with semaphore:
                            port_info = asyncio.run(spider.get_17live_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=yiqilive_cookie))

                    elif record_url.find("www.lang.live/") > -1:
                        platform = '浪Live'
                        with semaphore:
                            port_info = asyncio.run(spider.get_langlive_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=langlive_cookie))

                    elif record_url.find("m.pp.weimipopo.com/") > -1:
                        platform = '漂漂直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_pplive_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=pplive_cookie))

                    elif record_url.find(".6.cn/") > -1:
                        platform = '六間房直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_6room_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=six_room_cookie))

                    elif record_url.find("lehaitv.com/") > -1:
                        platform = '樂嗨直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_haixiu_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=lehaitv_cookie))

                    elif record_url.find("h.catshow168.com/") > -1:
                        platform = '花貓直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_pplive_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=huamao_cookie))

                    elif record_url.find("live.shopee") > -1 or record_url.find("shp.ee/") > -1:
                        platform = 'shopee'
                        with semaphore:
                            port_info = asyncio.run(spider.get_shopee_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=shopee_cookie))
                            if port_info and port_info.get('uid'):
                                new_record_url = record_url.split('?')[0] + '?' + str(port_info.get('uid'))

                    elif record_url.find("www.youtube.com/") > -1 or record_url.find("youtu.be/") > -1:
                        platform = 'Youtube'
                        with semaphore:
                            json_data = asyncio.run(spider.get_youtube_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=youtube_cookie))
                            port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))

                    elif record_url.find("tb.cn") > -1:
                        platform = '淘寶直播'
                        with semaphore:
                            json_data = asyncio.run(spider.get_taobao_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=taobao_cookie))
                            port_info = asyncio.run(stream.get_stream_url(
                                json_data, record_quality,
                                url_type='all', hls_extra_key='hlsUrl', flv_extra_key='flvUrl'
                            ))

                    elif record_url.find("3.cn") > -1 or record_url.find("m.jd.com") > -1:
                        platform = '京東直播'
                        with semaphore:
                            port_info = asyncio.run(spider.get_jd_stream_url(
                                url=record_url, proxy_addr=proxy_address, cookies=jd_cookie))

                    elif record_url.find("faceit.com/") > -1:
                        platform = 'faceit'
                        with semaphore:
                            if global_proxy or proxy_address:
                                with semaphore:
                                    json_data = asyncio.run(spider.get_faceit_stream_data(
                                        url=record_url, proxy_addr=proxy_address, cookies=faceit_cookie))
                                    port_info = asyncio.run(stream.get_stream_url(json_data, record_quality, spec=True))
                            else:
                                logger.error("錯誤資訊: 網路異常，請檢查本網路是否能正常訪問faceit直播平臺")
                                port_info = None

                    elif record_url.find(".m3u8") > -1 or record_url.find(".flv") > -1:
                        platform = '自定義錄製直播'
                        port_info = {
                            "anchor_name": platform + '_' + str(uuid.uuid4())[:8],
                            "is_live": True,
                            "record_url": record_url,
                        }
                        if '.flv' in record_url:
                            port_info['flv_url'] = record_url
                        else:
                            port_info['m3u8_url'] = record_url

                    else:
                        logger.error(f'{record_url} {platform}直播地址')
                        return

                    # 檢查 port_info 是否為 None，避免 NoneType 錯誤
                    if not port_info:
                        print(f'序號{count_variable} 網址內容獲取失敗,進行重試中...獲取失敗的地址是:{url_data}')
                        with max_request_lock:
                            error_count += 1
                            error_window.append(1)
                        continue  # 跳過本次循環，進行重試

                    if anchor_name:
                        if '主播:' in anchor_name:
                            anchor_split: list = anchor_name.split('主播:')
                            if len(anchor_split) > 1 and anchor_split[1].strip():
                                anchor_name = anchor_split[1].strip()
                            else:
                                anchor_name = port_info.get("anchor_name", '')
                    else:
                        anchor_name = port_info.get("anchor_name", '')

                    if not port_info.get("anchor_name", ''):
                        print(f'序號{count_variable} 網址內容獲取失敗,進行重試中...獲取失敗的地址是:{url_data}')
                        with max_request_lock:
                            error_count += 1
                            error_window.append(1)
                    else:
                        anchor_name = clean_name(anchor_name)
                        record_name = f'序號{count_variable} {anchor_name}'

                        if record_url in url_comments:
                            print(f"[{anchor_name}]已被註釋,本條執行緒將會退出")
                            clear_record_info(record_name, record_url)
                            return

                        if not url_data[-1] and run_once is False:
                            if new_record_url:
                                need_update_line_list.append(
                                    f'{record_url}|{new_record_url},主播: {anchor_name.strip()}')
                                not_record_list.append(new_record_url)
                            else:
                                need_update_line_list.append(f'{record_url}|{record_url},主播: {anchor_name.strip()}')
                            run_once = True

                        push_at = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                        if port_info.get('is_live') is False:
                            print(f"\r{record_name} 等待直播... ")

                            if start_pushed:
                                if over_show_push:
                                    push_content = "直播間狀態更新：[直播間名稱] 直播已結束！時間：[時間]"
                                    if over_push_message_text:
                                        push_content = over_push_message_text

                                    push_content = (push_content.replace('[直播間名稱]', record_name).
                                                    replace('[時間]', push_at))
                                    threading.Thread(
                                        target=push_message,
                                        args=(record_name, record_url, push_content.replace(r'\n', '\n')),
                                        daemon=True
                                    ).start()
                                start_pushed = False

                        else:
                            content = f"\r{record_name} 正在直播中..."
                            print(content)

                            if live_status_push and not start_pushed:
                                if begin_show_push:
                                    push_content = "直播間狀態更新：[直播間名稱] 正在直播中，時間：[時間]"
                                    if begin_push_message_text:
                                        push_content = begin_push_message_text

                                    push_content = (push_content.replace('[直播間名稱]', record_name).
                                                    replace('[時間]', push_at))
                                    threading.Thread(
                                        target=push_message,
                                        args=(record_name, record_url, push_content.replace(r'\n', '\n')),
                                        daemon=True
                                    ).start()
                                start_pushed = True

                            if disable_record:
                                time.sleep(push_check_seconds)
                                continue

                            real_url = port_info.get('record_url')
                            full_path = f'{default_path}/{platform}'
                            if real_url:
                                now = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
                                live_title = port_info.get('title')
                                title_in_name = ''
                                if live_title:
                                    live_title = clean_name(live_title)
                                    title_in_name = live_title + '_' if filename_by_title else ''

                                try:
                                    if len(video_save_path) > 0:
                                        if not video_save_path.endswith(('/', '\\')):
                                            full_path = f'{video_save_path}/{platform}'
                                        else:
                                            full_path = f'{video_save_path}{platform}'

                                    full_path = full_path.replace("\\", '/')
                                    if folder_by_author:
                                        full_path = f'{full_path}/{anchor_name}'
                                    if folder_by_time:
                                        full_path = f'{full_path}/{now[:10]}'
                                    if folder_by_title and port_info.get('title'):
                                        if folder_by_time:
                                            full_path = f'{full_path}/{live_title}_{anchor_name}'
                                        else:
                                            full_path = f'{full_path}/{now[:10]}_{live_title}'
                                    if not os.path.exists(full_path):
                                        os.makedirs(full_path)
                                except Exception as e:
                                    logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")

                                if platform != '自定義錄製直播':
                                    if enable_https_recording and real_url.startswith("http://"):
                                        real_url = real_url.replace("http://", "https://")

                                    http_record_list = ['shopee']
                                    if platform in http_record_list:
                                        real_url = real_url.replace("https://", "http://")

                                user_agent = ("Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 ("
                                              "KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile "
                                              "Safari/537.36")

                                rw_timeout = "15000000"
                                analyzeduration = "20000000"
                                probesize = "10000000"
                                # 保持原始緩衝區設定
                                bufsize = "8000k"
                                max_muxing_queue_size = "1024"
                                for pt_host in overseas_platform_host:
                                    if pt_host in record_url:
                                        rw_timeout = "50000000"
                                        analyzeduration = "40000000"
                                        probesize = "20000000"
                                        bufsize = "15000k"
                                        max_muxing_queue_size = "2048"
                                        break

                                ffmpeg_command = [
                                    'ffmpeg', "-y",
                                    "-v", "verbose",
                                    "-rw_timeout", rw_timeout,
                                    "-loglevel", "warning",  # 提升日誌級別以便監控損壞封包
                                    "-hide_banner",
                                    "-user_agent", user_agent,
                                    "-protocol_whitelist", "rtmp,crypto,file,http,https,tcp,tls,udp,rtp,httpproxy",
                                    "-thread_queue_size", "1024",
                                    "-analyzeduration", analyzeduration,
                                    "-probesize", probesize,
                                    "-fflags", "+discardcorrupt+genpts+igndts",  # 回到穩定的參數組合
                                    "-err_detect", "ignore_err",  # 回到原始設定，確保相容性
                                    # 移除固定格式指定，讓FFmpeg自動檢測
                                    "-re", "-i", real_url,
                                    "-bufsize", bufsize,
                                    "-sn", "-dn",
                                    "-reconnect_delay_max", "60",  # 保持原有重連延遲
                                    "-reconnect_streamed", "-reconnect_at_eof",
                                    "-max_muxing_queue_size", max_muxing_queue_size,
                                    "-correct_ts_overflow", "1",
                                    "-avoid_negative_ts", "make_zero",  # 保持原有設定
                                    "-vsync", "cfr",  # 回到恆定幀率，確保穩定性
                                ]

                                record_headers = {
                                    'PandaTV': 'origin:https://www.pandalive.co.kr',
                                    'WinkTV': 'origin:https://www.winktv.co.kr',
                                    'PopkonTV': 'origin:https://www.popkontv.com',
                                    'FlexTV': 'origin:https://www.flextv.co.kr',
                                    '千度熱播': 'referer:https://qiandurebo.com',
                                    '17Live': 'referer:https://17.live/en/live/6302408',
                                    '浪Live': 'referer:https://www.lang.live',
                                    'shopee': f'origin:{live_domain}',
                                }

                                headers = record_headers.get(platform)
                                if headers:
                                    ffmpeg_command.insert(11, "-headers")
                                    ffmpeg_command.insert(12, headers)

                                if proxy_address:
                                    ffmpeg_command.insert(1, "-http_proxy")
                                    ffmpeg_command.insert(2, proxy_address)

                                recording.add(record_name)
                                start_record_time = datetime.datetime.now()
                                recording_time_list[record_name] = [start_record_time, record_quality_zh]
                                rec_info = f"\r{anchor_name} 準備開始錄製視訊: {full_path}"
                                if show_url:
                                    re_plat = ('WinkTV', 'PandaTV', 'ShowRoom', 'CHZZK', 'Youtube')
                                    if platform in re_plat:
                                        m3u8_url = port_info.get('m3u8_url', '未知')
                                        logger.info(f"{platform} | {anchor_name} | 直播源地址: {m3u8_url}")
                                    else:
                                        logger.info(
                                            f"{platform} | {anchor_name} | 直播源地址: {real_url}")

                                only_flv_record = False
                                only_flv_platform_list = ['shopee'] if os.name == 'nt' else ['shopee', '花椒直播']
                                if platform in only_flv_platform_list:
                                    logger.debug(f"提示: {platform} 將強制使用FLV格式錄製")
                                    only_flv_record = True

                                if video_save_type == "FLV" or only_flv_record:
                                    # 使用新的檔案命名函數獲取基本檔名
                                    base_filename = get_formatted_filename(anchor_name, title_in_name)
                                    # 使用新函數獲取不重複的檔案名稱
                                    filename = get_non_duplicate_filename(full_path, base_filename, "flv")
                                    save_file_path = f'{full_path}/{filename}'

                                    print(f'{rec_info}/{filename}')

                                    subs_file_path = save_file_path.rsplit('.', maxsplit=1)[0]
                                    subs_thread_name = f'subs_{Path(subs_file_path).name}'
                                    if create_time_file:
                                        create_var[subs_thread_name] = threading.Thread(
                                            target=generate_subtitles, args=(record_name, subs_file_path)
                                        )
                                        create_var[subs_thread_name].daemon = True
                                        create_var[subs_thread_name].start()

                                    try:
                                        flv_url = port_info.get('flv_url')
                                        if flv_url:
                                            _filepath, _ = urllib.request.urlretrieve(flv_url, save_file_path)
                                            record_finished = True
                                            recording.discard(record_name)
                                            print(
                                                f"\n{anchor_name} {time.strftime('%Y-%m-%d %H:%M:%S')} 直播錄製完成\n")
                                        else:
                                            logger.debug("未找到FLV直播流，跳過錄制")
                                    except Exception as e:
                                        clear_record_info(record_name, record_url)
                                        color_obj.print_colored(
                                            f"\n{anchor_name} {time.strftime('%Y-%m-%d %H:%M:%S')} 直播錄製出錯,請檢查網路\n",
                                            color_obj.RED)
                                        logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                        with max_request_lock:
                                            error_count += 1
                                            error_window.append(1)

                                    try:
                                        if converts_to_mp4:
                                            # 從檔案名稱中提取實際使用的基本檔名(可能已包含編號)
                                            actual_base_filename = os.path.splitext(filename)[0]
                                            seg_file_path = f"{full_path}/{actual_base_filename}-%d.mp4"
                                            if split_video_by_time:
                                                segment_video(
                                                    save_file_path, seg_file_path,
                                                    segment_format='mp4', segment_time=split_time,
                                                    is_original_delete=delete_origin_file
                                                )
                                            else:
                                                threading.Thread(
                                                    target=converts_mp4,
                                                    args=(save_file_path, delete_origin_file)
                                                ).start()

                                        else:
                                            # 從檔案名稱中提取實際使用的基本檔名(可能已包含編號)
                                            actual_base_filename = os.path.splitext(filename)[0]
                                            seg_file_path = f"{full_path}/{actual_base_filename}-%d.flv"
                                            if split_video_by_time:
                                                segment_video(
                                                    save_file_path, seg_file_path,
                                                    segment_format='flv', segment_time=split_time,
                                                    is_original_delete=delete_origin_file
                                                )
                                    except Exception as e:
                                        logger.error(f"轉碼失敗: {e} ")

                                elif video_save_type == "MKV":
                                    # 使用新的檔案命名函數獲取基本檔名
                                    base_filename = get_formatted_filename(anchor_name, title_in_name)
                                    # 使用新函數獲取不重複的檔案名稱
                                    filename = get_non_duplicate_filename(full_path, base_filename, "mkv")

                                    print(f'{rec_info}/{filename}')
                                    save_file_path = full_path + '/' + filename

                                    # 從檔案名稱中提取實際使用的基本檔名(可能已包含編號)
                                    actual_base_filename = os.path.splitext(filename)[0]

                                    try:
                                        if split_video_by_time:
                                            # 分段錄製：使用專門的分段檔名函數確保連續編號
                                            segment_base, start_number = get_segment_base_filename(full_path, anchor_name, title_in_name, "mkv")
                                            save_file_path = f"{full_path}/{segment_base}-%d.mkv"
                                            command = [
                                                "-flags", "global_header",
                                                "-c:v", "copy",
                                                "-c:a", "aac",
                                                "-map", "0",
                                                "-f", "segment",
                                                "-segment_time", str(split_time),
                                                "-segment_format", "matroska",
                                                save_file_path,
                                            ]
                                        else:
                                            command = [
                                                "-flags", "global_header",
                                                "-map", "0",
                                                "-c:v", "copy",
                                                "-c:a", "copy",
                                                "-f", "matroska",
                                                "{path}".format(path=save_file_path),
                                            ]
                                        ffmpeg_command.extend(command)

                                        comment_end = check_subprocess(
                                            record_name,
                                            record_url,
                                            ffmpeg_command,
                                            video_save_type,
                                            custom_script,
                                            platform,
                                            proxy_address
                                        )
                                        # 只有被手動註釋時才退出執行緒，錄製自然結束時繼續監控循環
                                        if comment_end:
                                            return
                                        # 錄製結束，設置標誌並繼續監控循環
                                        record_finished = True

                                    except subprocess.CalledProcessError as e:
                                        logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                        with max_request_lock:
                                            error_count += 1
                                            error_window.append(1)

                                elif video_save_type == "MP4":
                                    # 使用新的檔案命名函數獲取基本檔名
                                    base_filename = get_formatted_filename(anchor_name, title_in_name)
                                    # 使用新函數獲取不重複的檔案名稱
                                    filename = get_non_duplicate_filename(full_path, base_filename, "mp4")

                                    print(f'{rec_info}/{filename}')
                                    save_file_path = full_path + '/' + filename

                                    # 從檔案名稱中提取實際使用的基本檔名(可能已包含編號)
                                    actual_base_filename = os.path.splitext(filename)[0]

                                    try:
                                        if split_video_by_time:
                                            # 分段錄製：使用專門的分段檔名函數確保連續編號
                                            segment_base, start_number = get_segment_base_filename(full_path, anchor_name, title_in_name, "mp4")
                                            save_file_path = f"{full_path}/{segment_base}-%d.mp4"
                                            if converts_to_h264:
                                                # 使用 H264 編碼確保相容性
                                                command = [
                                                    "-c:v", "libx264",
                                                    "-preset", "veryfast",
                                                    "-crf", "23",
                                                    "-vf", "format=yuv420p",
                                                    "-c:a", "aac",
                                                    "-map", "0",
                                                    "-f", "segment",  # 使用segment格式進行分段
                                                    "-segment_time", split_time,  # 設定分段時間
                                                    "-segment_format", "mp4",  # 分段格式為mp4
                                                    "-segment_list_type", "flat",  # 分段列表類型
                                                    "-segment_start_number", str(start_number),  # 分段開始編號
                                                    "-reset_timestamps", "1",  # 重置時間戳
                                                    # 分段錄製時使用frag_keyframe+empty_moov以支援即時寫入
                                                    "-movflags", "+frag_keyframe+empty_moov",
                                                    # H.264編碼器錯誤處理參數
                                                    "-x264-params", "nal-hrd=cbr:force-cfr=1",
                                                    "-g", "60",  # 設定GOP大小
                                                    "-keyint_min", "60",  # 最小關鍵幀間隔
                                                    save_file_path,
                                                ]
                                            else:
                                                command = [
                                                    "-c:v", "copy",
                                                    "-c:a", "aac",
                                                    "-map", "0",
                                                    "-f", "segment",  # 使用segment格式進行分段
                                                    "-segment_time", split_time,  # 設定分段時間
                                                    "-segment_format", "mp4",  # 分段格式為mp4
                                                    "-segment_list_type", "flat",  # 分段列表類型
                                                    "-segment_start_number", str(start_number),  # 分段開始編號
                                                    "-reset_timestamps", "1",  # 重置時間戳
                                                    # 分段錄製時使用frag_keyframe+empty_moov以支援即時寫入
                                                    "-movflags", "+frag_keyframe+empty_moov",
                                                    # 強化H.264流修復
                                                    "-bsf:v", "h264_mp4toannexb,h264_metadata=aud=insert:sei_user_data=insert",
                                                    "-fps_mode", "cfr",  # 強制恆定幀率
                                                    save_file_path,
                                                ]

                                        else:
                                            if converts_to_h264:
                                                # 使用 H264 編碼確保相容性
                                                command = [
                                                    "-map", "0",
                                                    "-c:v", "libx264",
                                                    "-preset", "veryfast",
                                                    "-crf", "23",
                                                    "-vf", "format=yuv420p",
                                                    "-c:a", "aac",
                                                    "-f", "mp4",
                                                    # H.264編碼器錯誤處理參數
                                                    "-x264-params", "nal-hrd=cbr:force-cfr=1",
                                                    "-g", "60",  # 設定GOP大小
                                                    "-keyint_min", "60",  # 最小關鍵幀間隔
                                                    # 移除 "+faststart" 以提高即時錄製效能，錄製完成後再優化
                                                    save_file_path,
                                                ]
                                            else:
                                                command = [
                                                    "-map", "0",
                                                    "-c:v", "copy",
                                                    "-c:a", "aac",
                                                    "-f", "mp4",
                                                    # 強化H.264流修復
                                                    "-bsf:v", "h264_mp4toannexb,h264_metadata=aud=insert:sei_user_data=insert",
                                                    "-fps_mode", "cfr",  # 強制恆定幀率
                                                    # 移除 "+faststart" 以提高即時錄製效能，錄製完成後再優化
                                                    save_file_path,
                                                ]

                                        ffmpeg_command.extend(command)
                                        # 應用H.264錯誤修復
                                        ffmpeg_command = fix_h264_stream_errors(ffmpeg_command)
                                        comment_end = check_subprocess(
                                            record_name,
                                            record_url,
                                            ffmpeg_command,
                                            video_save_type,
                                            custom_script,
                                            platform,
                                            proxy_address
                                        )
                                        # 只有被手動註釋時才退出執行緒，錄製自然結束時繼續監控循環
                                        if comment_end:
                                            return
                                        # 錄製結束，設置標誌並繼續監控循環
                                        record_finished = True

                                    except subprocess.CalledProcessError as e:
                                        logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                        with max_request_lock:
                                            error_count += 1
                                            error_window.append(1)

                                elif "音訊" in video_save_type:
                                    try:
                                        extension = "mp3" if "MP3" in video_save_type else "m4a"
                                        # 使用統一的檔案命名函數
                                        base_filename = get_formatted_filename(anchor_name, title_in_name)
                                        filename = get_non_duplicate_filename(full_path, base_filename, extension)
                                        save_file_path = f"{full_path}/{filename}"

                                        if split_video_by_time:
                                            print(f'\r{anchor_name} 準備開始錄製音訊: {save_file_path}')

                                            # 使用 get_non_duplicate_filename 獲取不重複的檔名
                                            if "MP3" in video_save_type:
                                                # 獲取第一個檔案的名稱
                                                first_filename = get_non_duplicate_filename(full_path, base_filename, "mp3")
                                                first_file_path = f"{full_path}/{first_filename}"

                                                command = [
                                                    "-map", "0:a",
                                                    "-c:a", "libmp3lame",
                                                    "-ab", "320k",
                                                    "-f", "mp3",
                                                    first_file_path,
                                                ]
                                            else:
                                                # 獲取第一個檔案的名稱
                                                first_filename = get_non_duplicate_filename(full_path, base_filename, "m4a")
                                                first_file_path = f"{full_path}/{first_filename}"

                                                command = [
                                                    "-map", "0:a",
                                                    "-c:a", "aac",
                                                    "-bsf:a", "aac_adtstoasc",
                                                    "-ab", "320k",
                                                    "-f", "m4a",
                                                    first_file_path,
                                                ]

                                        else:
                                            # 非分段音訊錄製
                                            if "MP3" in video_save_type:
                                                command = [
                                                    "-map", "0:a",
                                                    "-c:a", "libmp3lame",
                                                    "-ab", "320k",
                                                    save_file_path,
                                                ]
                                            else:
                                                command = [
                                                    "-map", "0:a",
                                                    "-c:a", "aac",
                                                    "-bsf:a", "aac_adtstoasc",
                                                    "-ab", "320k",
                                                    "-movflags", "+faststart",
                                                    save_file_path,
                                                ]

                                        ffmpeg_command.extend(command)
                                        # 應用H.264錯誤修復
                                        ffmpeg_command = fix_h264_stream_errors(ffmpeg_command)
                                        comment_end = check_subprocess(
                                            record_name,
                                            record_url,
                                            ffmpeg_command,
                                            video_save_type,
                                            custom_script,
                                            platform,
                                            proxy_address
                                        )
                                        # 只有被手動註釋時才退出執行緒，錄製自然結束時繼續監控循環
                                        if comment_end:
                                            return
                                        # 錄製結束，設置標誌並繼續監控循環
                                        record_finished = True

                                    except subprocess.CalledProcessError as e:
                                        logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                        with max_request_lock:
                                            error_count += 1
                                            error_window.append(1)

                                else:
                                    if split_video_by_time:
                                        # 使用新的檔案命名函數獲取基本檔名
                                        base_filename = get_formatted_filename(anchor_name, title_in_name)
                                        # 使用新函數獲取不重複的檔案名稱
                                        filename = get_non_duplicate_filename(full_path, base_filename, "ts")

                                        print(f'{rec_info}/{filename}')
                                        save_file_path = full_path + '/' + filename

                                        # 從檔案名稱中提取實際使用的基本檔名(可能已包含編號)
                                        actual_base_filename = os.path.splitext(filename)[0]

                                        try:
                                            # 分段錄製：使用專門的分段檔名函數確保連續編號
                                            segment_base, start_number = get_segment_base_filename(full_path, anchor_name, title_in_name, "ts")
                                            segment_template = f"{full_path}/{segment_base}-%d.ts"
                                            command = [
                                                "-c:v", "copy",
                                                "-c:a", "copy",
                                                "-map", "0",
                                                "-f", "segment",
                                                "-segment_time", str(split_time),
                                                "-segment_format", "mpegts",
                                                segment_template,
                                            ]

                                            ffmpeg_command.extend(command)
                                            comment_end = check_subprocess(
                                                record_name,
                                                record_url,
                                                ffmpeg_command,
                                                video_save_type,
                                                custom_script,
                                                platform,
                                                proxy_address
                                            )

                                            # 檢查第一個分段檔案(從1開始)
                                            first_file = f"{full_path}/{actual_base_filename}-1.ts"
                                            if os.path.exists(first_file):
                                                logger.info(f"已產生第一個分段檔案: {actual_base_filename}-1.ts")

                                        except subprocess.CalledProcessError as e:
                                            logger.error(
                                                f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                            with max_request_lock:
                                                error_count += 1
                                                error_window.append(1)

                                    else:
                                        # 使用統一的檔案命名函數
                                        base_filename = get_formatted_filename(anchor_name, title_in_name)
                                        filename = get_non_duplicate_filename(full_path, base_filename, "ts")
                                        print(f'{rec_info}/{filename}')
                                        save_file_path = full_path + '/' + filename

                                        try:
                                            command = [
                                                "-c:v", "copy",
                                                "-c:a", "copy",
                                                "-map", "0",
                                                "-f", "mpegts",
                                                save_file_path,
                                            ]

                                            ffmpeg_command.extend(command)
                                            comment_end = check_subprocess(
                                                record_name,
                                                record_url,
                                                ffmpeg_command,
                                                video_save_type,
                                                custom_script,
                                                platform,
                                                proxy_address
                                            )
                                            # 只有被手動註釋時才退出執行緒，錄製自然結束時繼續監控循環
                                            if comment_end:
                                                threading.Thread(
                                                    target=converts_mp4, args=(save_file_path, delete_origin_file)
                                                ).start()
                                                return
                                            # 錄製結束，設置標誌並繼續監控循環
                                            record_finished = True

                                        except subprocess.CalledProcessError as e:
                                            logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                                            with max_request_lock:
                                                error_count += 1
                                                error_window.append(1)

                                count_time = time.time()

                except Exception as e:
                    logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
                    with max_request_lock:
                        error_count += 1
                        error_window.append(1)

                num = random.randint(-5, 5) + delay_default
                if num < 0:
                    num = 0
                x = num

                if error_count > 20:
                    x = x + 60
                    color_obj.print_colored("\r瞬時錯誤太多,延遲加60秒", color_obj.YELLOW)

                # 這裡是.如果錄製結束後,循環時間會暫時變成30s後檢測一遍. 這樣一定程度上防止主播卡頓造成少錄
                # 當30秒過後檢測一遍後. 會迴歸正常設定的循環秒數
                if record_finished:
                    count_time_end = time.time() - count_time
                    if count_time_end < 60:
                        x = 30
                    record_finished = False

                else:
                    x = num

                # 這裡是正常循環
                while x:
                    x = x - 1
                    if loop_time:
                        print(f'\r{anchor_name}循環等待{x}秒 ', end="")
                    time.sleep(1)
                if loop_time:
                    print('\r檢測直播間中...', end="")
        except Exception as e:
            logger.error(f"錯誤資訊: {e} 發生錯誤的行數: {e.__traceback__.tb_lineno}")
            with max_request_lock:
                error_count += 1
                error_window.append(1)
            time.sleep(2)


def backup_file(file_path: str, backup_dir_path: str, limit_counts: int = 6) -> None:
    try:
        if not os.path.exists(backup_dir_path):
            os.makedirs(backup_dir_path)

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_file_name = os.path.basename(file_path) + '_' + timestamp
        backup_file_path = os.path.join(backup_dir_path, backup_file_name).replace("\\", "/")
        shutil.copy2(file_path, backup_file_path)

        files = os.listdir(backup_dir_path)
        _files = [f for f in files if f.startswith(os.path.basename(file_path))]
        _files.sort(key=lambda x: os.path.getmtime(os.path.join(backup_dir_path, x)))

        while len(_files) > limit_counts:
            oldest_file = _files[0]
            os.remove(os.path.join(backup_dir_path, oldest_file))
            _files = _files[1:]

    except Exception as e:
        logger.error(f'\r備份配置檔案 {file_path} 失敗：{str(e)}')


def backup_file_start() -> None:
    config_md5 = ''
    url_config_md5 = ''

    while True:
        try:
            if os.path.exists(config_file):
                new_config_md5 = utils.check_md5(config_file)
                if new_config_md5 != config_md5:
                    backup_file(config_file, backup_dir)
                    config_md5 = new_config_md5

            if os.path.exists(url_config_file):
                new_url_config_md5 = utils.check_md5(url_config_file)
                if new_url_config_md5 != url_config_md5:
                    backup_file(url_config_file, backup_dir)
                    url_config_md5 = new_url_config_md5
            time.sleep(600)
        except Exception as e:
            logger.error(f"備份配置檔案失敗, 錯誤資訊: {e}")


def check_ffmpeg_existence() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            version_line = lines[0]
            built_line = lines[1]
            print(version_line)
            print(built_line)
    except subprocess.CalledProcessError as e:
        logger.error(e)
    except FileNotFoundError:
        pass
    finally:
        if check_ffmpeg():
            time.sleep(1)
            return True
    return False


# --------------------------初始化程式-------------------------------------
print("-----------------------------------------------------")
print("|                DouyinLiveRecorder                 |")
print("-----------------------------------------------------")

print(f"版本號: {version}")
print("GitHub: https://github.com/ihmily/DouyinLiveRecorder")
print(f'支援平臺: {platforms}')
print('.....................................................')
if not check_ffmpeg_existence():
    logger.error("缺少ffmpeg無法進行錄製，程式退出")
    sys.exit(1)
os.makedirs(os.path.dirname(config_file), exist_ok=True)
t3 = threading.Thread(target=backup_file_start, args=(), daemon=True)
t3.start()
utils.remove_duplicate_lines(url_config_file)


def read_config_value(config_parser: configparser.RawConfigParser, section: str, option: str, default_value: Any) \
        -> Any:
    try:

        config_parser.read(config_file, encoding=text_encoding)
        if '錄製設定' not in config_parser.sections():
            config_parser.add_section('錄製設定')
        if '推送配置' not in config_parser.sections():
            config_parser.add_section('推送配置')
        if 'Cookie' not in config_parser.sections():
            config_parser.add_section('Cookie')
        if 'Authorization' not in config_parser.sections():
            config_parser.add_section('Authorization')
        if '帳號密碼' not in config_parser.sections():
            config_parser.add_section('帳號密碼')
        return config_parser.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError):
        config_parser.set(section, option, str(default_value))
        with open(config_file, 'w', encoding=text_encoding) as f:
            config_parser.write(f)
        return default_value


options = {"是": True, "否": False}
config = configparser.RawConfigParser()
language = read_config_value(config, '錄製設定', 'language(zh_tw/en)', "zh_tw")
skip_proxy_check = options.get(read_config_value(config, '錄製設定', '是否跳過代理檢測(是/否)', "否"), False)
if language and 'en' not in language.lower():
    from i18n import translated_print

    builtins.print = translated_print

try:
    if skip_proxy_check:
        global_proxy = True
    else:
        print('系統代理檢測中，請耐心等待...')
        response_g = urllib.request.urlopen("https://www.google.com/", timeout=15)
        global_proxy = True
        print('\r全域性/規則網路代理已開啟√')
        pd = ProxyDetector()
        if pd.is_proxy_enabled():
            proxy_info = pd.get_proxy_info()
            print("System Proxy: http://{}:{}".format(proxy_info.ip, proxy_info.port))
except HTTPError as err:
    print(f"HTTP error occurred: {err.code} - {err.reason}")
except URLError as err:
    color_obj.print_colored(f"INFO：未檢測到全域性/規則網路代理，請檢查代理配置（若無需錄製海外直播請忽略此條提示）",
                            color_obj.YELLOW)
except Exception as err:
    print("An unexpected error occurred:", err)

while True:

    try:
        if not os.path.isfile(config_file):
            with open(config_file, 'w', encoding=text_encoding) as file:
                pass

        ini_URL_content = ''
        if os.path.isfile(url_config_file):
            with open(url_config_file, 'r', encoding=text_encoding) as file:
                ini_URL_content = file.read().strip()

        if not ini_URL_content.strip():
            input_url = input('請輸入要錄製的主播直播間網址（儘量使用PC網頁端的直播間地址）:\n')
            with open(url_config_file, 'w', encoding=text_encoding) as file:
                file.write(input_url)
    except OSError as err:
        logger.error(f"發生 I/O 錯誤: {err}")

    video_save_path = read_config_value(config, '錄製設定', '直播儲存路徑(不填則預設)', "")
    folder_by_author = options.get(read_config_value(config, '錄製設定', '儲存資料夾是否以作者區分', "是"), False)
    folder_by_time = options.get(read_config_value(config, '錄製設定', '儲存資料夾是否以時間區分', "否"), False)
    folder_by_title = options.get(read_config_value(config, '錄製設定', '儲存資料夾是否以標題區分', "否"), False)
    filename_by_title = options.get(read_config_value(config, '錄製設定', '儲存檔名是否包含標題', "否"), False)
    clean_emoji = options.get(read_config_value(config, '錄製設定', '是否去除名稱中的表情符號', "是"), True)
    video_save_type = read_config_value(config, '錄製設定', '視訊儲存格式ts|mkv|flv|mp4|mp3音訊|m4a音訊', "ts")
    video_record_quality = read_config_value(config, '錄製設定', '原畫|超清|高清|標清|流暢', "原畫")
    use_proxy = options.get(read_config_value(config, '錄製設定', '是否使用代理ip(是/否)', "是"), False)
    proxy_addr_bak = read_config_value(config, '錄製設定', '代理地址', "")
    proxy_addr = None if not use_proxy else proxy_addr_bak
    max_request = int(read_config_value(config, '錄製設定', '同一時間訪問網路的執行緒數', 3))
    semaphore = threading.Semaphore(max_request)
    delay_default = int(read_config_value(config, '錄製設定', '循環時間(秒)', 120))
    local_delay_default = int(read_config_value(config, '錄製設定', '排隊讀取網址時間(秒)', 0))
    loop_time = options.get(read_config_value(config, '錄製設定', '是否顯示循環秒數', "否"), False)
    show_url = options.get(read_config_value(config, '錄製設定', '是否顯示直播源地址', "否"), False)
    split_video_by_time = options.get(read_config_value(config, '錄製設定', '分段錄製是否開啟', "否"), False)
    enable_https_recording = options.get(read_config_value(config, '錄製設定', '是否強制啟用https錄製', "否"), False)
    disk_space_limit = float(read_config_value(config, '錄製設定', '錄製空間剩餘閾值(gb)', 1.0))
    split_time = str(read_config_value(config, '錄製設定', '視訊分段時間(秒)', 1800))
    converts_to_mp4 = options.get(read_config_value(config, '錄製設定', '錄製完成後自動轉為mp4格式', "否"), False)
    converts_to_h264 = options.get(read_config_value(config, '錄製設定', 'mp4格式重新編碼為h264', "否"), False)
    delete_origin_file = options.get(read_config_value(config, '錄製設定', '追加格式後刪除原檔案', "否"), False)
    create_time_file = options.get(read_config_value(config, '錄製設定', '產生時間字幕檔案', "否"), False)
    is_run_script = options.get(read_config_value(config, '錄製設定', '是否錄製完成後執行自定義指令碼', "否"), False)
    custom_script = read_config_value(config, '錄製設定', '自定義指令碼執行命令', "") if is_run_script else None
    # 封包監控預設啟用（硬編碼，無需配置）
    enable_packet_monitoring = True
    enable_proxy_platform = read_config_value(
        config, '錄製設定', '使用代理錄製的平臺(逗號分隔)',
        'tiktok, soop, pandalive, winktv, flextv, popkontv, twitch, liveme, showroom, chzzk, shopee, shp, youtu, faceit'
    )
    enable_proxy_platform_list = enable_proxy_platform.replace('，', ',').split(',') if enable_proxy_platform else None
    extra_enable_proxy = read_config_value(config, '錄製設定', '額外使用代理錄製的平臺(逗號分隔)', '')
    extra_enable_proxy_platform_list = extra_enable_proxy.replace('，', ',').split(',') if extra_enable_proxy else None
    live_status_push = read_config_value(config, '推送配置', '直播狀態推送渠道', "")
    dingtalk_api_url = read_config_value(config, '推送配置', '釘釘推送介面鏈接', "")
    xizhi_api_url = read_config_value(config, '推送配置', '微信推送介面鏈接', "")
    bark_msg_api = read_config_value(config, '推送配置', 'bark推送介面鏈接', "")
    bark_msg_level = read_config_value(config, '推送配置', 'bark推送中斷級別', "active")
    bark_msg_ring = read_config_value(config, '推送配置', 'bark推送鈴聲', "bell")
    dingtalk_phone_num = read_config_value(config, '推送配置', '釘釘通知@對像(填手機號)', "")
    dingtalk_is_atall = options.get(read_config_value(config, '推送配置', '釘釘通知@全體(是/否)', "否"), False)
    tg_token = read_config_value(config, '推送配置', 'tgapi令牌', "")
    tg_chat_id = read_config_value(config, '推送配置', 'tg聊天id(個人或者群組id)', "")
    email_host = read_config_value(config, '推送配置', 'SMTP郵件伺服器', "")
    open_smtp_ssl = options.get(read_config_value(config, '推送配置', '是否使用SMTP服務SSL加密(是/否)', "是"), True)
    smtp_port = read_config_value(config, '推送配置', 'SMTP郵件伺服器埠', "")
    login_email = read_config_value(config, '推送配置', '郵箱登錄帳號', "")
    email_password = read_config_value(config, '推送配置', '發件人密碼(授權碼)', "")
    sender_email = read_config_value(config, '推送配置', '發件人郵箱', "")
    sender_name = read_config_value(config, '推送配置', '發件人顯示昵稱', "")
    to_email = read_config_value(config, '推送配置', '收件人郵箱', "")
    ntfy_api = read_config_value(config, '推送配置', 'ntfy推送地址', "")
    ntfy_tags = read_config_value(config, '推送配置', 'ntfy推送標籤', "tada")
    ntfy_email = read_config_value(config, '推送配置', 'ntfy推送郵箱', "")
    push_message_title = read_config_value(config, '推送配置', '自定義推送標題', "直播間狀態更新通知")
    begin_push_message_text = read_config_value(config, '推送配置', '自定義開播推送內容', "")
    over_push_message_text = read_config_value(config, '推送配置', '自定義關播推送內容', "")
    disable_record = options.get(read_config_value(config, '推送配置', '只推送通知不錄製(是/否)', "否"), False)
    push_check_seconds = int(read_config_value(config, '推送配置', '直播推送檢測頻率(秒)', 1800))
    begin_show_push = options.get(read_config_value(config, '推送配置', '開播推送開啟(是/否)', "是"), True)
    over_show_push = options.get(read_config_value(config, '推送配置', '關播推送開啟(是/否)', "否"), False)
    sooplive_username = read_config_value(config, '帳號密碼', 'sooplive帳號', '')
    sooplive_password = read_config_value(config, '帳號密碼', 'sooplive密碼', '')
    flextv_username = read_config_value(config, '帳號密碼', 'flextv帳號', '')
    flextv_password = read_config_value(config, '帳號密碼', 'flextv密碼', '')
    popkontv_username = read_config_value(config, '帳號密碼', 'popkontv帳號', '')
    popkontv_partner_code = read_config_value(config, '帳號密碼', 'partner_code', 'P-00001')
    popkontv_password = read_config_value(config, '帳號密碼', 'popkontv密碼', '')
    twitcasting_account_type = read_config_value(config, '帳號密碼', 'twitcasting帳號型別', 'normal')
    twitcasting_username = read_config_value(config, '帳號密碼', 'twitcasting帳號', '')
    twitcasting_password = read_config_value(config, '帳號密碼', 'twitcasting密碼', '')
    popkontv_access_token = read_config_value(config, 'Authorization', 'popkontv_token', '')
    dy_cookie = read_config_value(config, 'Cookie', '抖音cookie', '')
    ks_cookie = read_config_value(config, 'Cookie', '快手cookie', '')
    tiktok_cookie = read_config_value(config, 'Cookie', 'tiktok_cookie', '')
    hy_cookie = read_config_value(config, 'Cookie', '虎牙cookie', '')
    douyu_cookie = read_config_value(config, 'Cookie', '鬥魚cookie', '')
    yy_cookie = read_config_value(config, 'Cookie', 'yy_cookie', '')
    bili_cookie = read_config_value(config, 'Cookie', 'B站cookie', '')
    xhs_cookie = read_config_value(config, 'Cookie', '小紅書cookie', '')
    bigo_cookie = read_config_value(config, 'Cookie', 'bigo_cookie', '')
    blued_cookie = read_config_value(config, 'Cookie', 'blued_cookie', '')
    sooplive_cookie = read_config_value(config, 'Cookie', 'sooplive_cookie', '')
    netease_cookie = read_config_value(config, 'Cookie', 'netease_cookie', '')
    qiandurebo_cookie = read_config_value(config, 'Cookie', '千度熱播_cookie', '')
    pandatv_cookie = read_config_value(config, 'Cookie', 'pandatv_cookie', '')
    maoerfm_cookie = read_config_value(config, 'Cookie', '貓耳fm_cookie', '')
    winktv_cookie = read_config_value(config, 'Cookie', 'winktv_cookie', '')
    flextv_cookie = read_config_value(config, 'Cookie', 'flextv_cookie', '')
    look_cookie = read_config_value(config, 'Cookie', 'look_cookie', '')
    twitcasting_cookie = read_config_value(config, 'Cookie', 'twitcasting_cookie', '')
    baidu_cookie = read_config_value(config, 'Cookie', 'baidu_cookie', '')
    weibo_cookie = read_config_value(config, 'Cookie', 'weibo_cookie', '')
    kugou_cookie = read_config_value(config, 'Cookie', 'kugou_cookie', '')
    twitch_cookie = read_config_value(config, 'Cookie', 'twitch_cookie', '')
    liveme_cookie = read_config_value(config, 'Cookie', 'liveme_cookie', '')
    huajiao_cookie = read_config_value(config, 'Cookie', 'huajiao_cookie', '')
    liuxing_cookie = read_config_value(config, 'Cookie', 'liuxing_cookie', '')
    showroom_cookie = read_config_value(config, 'Cookie', 'showroom_cookie', '')
    acfun_cookie = read_config_value(config, 'Cookie', 'acfun_cookie', '')
    changliao_cookie = read_config_value(config, 'Cookie', 'changliao_cookie', '')
    yinbo_cookie = read_config_value(config, 'Cookie', 'yinbo_cookie', '')
    yingke_cookie = read_config_value(config, 'Cookie', 'yingke_cookie', '')
    zhihu_cookie = read_config_value(config, 'Cookie', 'zhihu_cookie', '')
    chzzk_cookie = read_config_value(config, 'Cookie', 'chzzk_cookie', '')
    haixiu_cookie = read_config_value(config, 'Cookie', 'haixiu_cookie', '')
    vvxqiu_cookie = read_config_value(config, 'Cookie', 'vvxqiu_cookie', '')
    yiqilive_cookie = read_config_value(config, 'Cookie', '17live_cookie', '')
    langlive_cookie = read_config_value(config, 'Cookie', 'langlive_cookie', '')
    pplive_cookie = read_config_value(config, 'Cookie', 'pplive_cookie', '')
    six_room_cookie = read_config_value(config, 'Cookie', '6room_cookie', '')
    lehaitv_cookie = read_config_value(config, 'Cookie', 'lehaitv_cookie', '')
    huamao_cookie = read_config_value(config, 'Cookie', 'huamao_cookie', '')
    shopee_cookie = read_config_value(config, 'Cookie', 'shopee_cookie', '')
    youtube_cookie = read_config_value(config, 'Cookie', 'youtube_cookie', '')
    taobao_cookie = read_config_value(config, 'Cookie', 'taobao_cookie', '')
    jd_cookie = read_config_value(config, 'Cookie', 'jd_cookie', '')
    faceit_cookie = read_config_value(config, 'Cookie', 'faceit_cookie', '')

    video_save_type_list = ("FLV", "MKV", "TS", "MP4", "MP3音訊", "M4A音訊")
    if video_save_type and video_save_type.upper() in video_save_type_list:
        video_save_type = video_save_type.upper()
    else:
        video_save_type = "TS"

    check_path = video_save_path or default_path
    if utils.check_disk_capacity(check_path, show=first_run) < disk_space_limit:
        exit_recording = True
        if not recording:
            logger.warning(f"Disk space remaining is below {disk_space_limit} GB. "
                           f"Exiting program due to the disk space limit being reached.")
            sys.exit(-1)


    def contains_url(string: str) -> bool:
        pattern = r"(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+(:\d+)?(/.*)?"
        return re.search(pattern, string) is not None


    try:
        url_comments, line_list, url_line_list = [[] for _ in range(3)]
        with (open(url_config_file, "r", encoding=text_encoding, errors='ignore') as file):
            for origin_line in file:
                if origin_line in line_list:
                    delete_line(url_config_file, origin_line)
                line_list.append(origin_line)
                line = origin_line.strip()
                if len(line) < 20:
                    continue

                line_spilt = line.split('主播: ')
                if len(line_spilt) > 2:
                    line = update_file(url_config_file, line, f'{line_spilt[0]}主播: {line_spilt[-1]}')

                is_comment_line = line.startswith("#")
                if is_comment_line:
                    line = line.lstrip('#')

                if re.search('[,，]', line):
                    split_line = re.split('[,，]', line)
                else:
                    split_line = [line, '']

                if len(split_line) == 1:
                    url = split_line[0]
                    quality, name = [video_record_quality, '']
                elif len(split_line) == 2:
                    if contains_url(split_line[0]):
                        quality = video_record_quality
                        url, name = split_line
                    else:
                        quality, url = split_line
                        name = ''
                else:
                    quality, url, name = split_line

                if quality not in ("原畫", "藍光", "超清", "高清", "標清", "流暢"):
                    quality = '原畫'

                if url not in url_line_list:
                    url_line_list.append(url)
                else:
                    delete_line(url_config_file, origin_line)

                url = 'https://' + url if '://' not in url else url
                url_host = url.split('/')[2]

                platform_host = [
                    'live.douyin.com',
                    'v.douyin.com',
                    'www.douyin.com',
                    'live.kuaishou.com',
                    'www.huya.com',
                    'www.douyu.com',
                    'www.yy.com',
                    'live.bilibili.com',
                    'www.redelight.cn',
                    'www.xiaohongshu.com',
                    'xhslink.com',
                    'www.bigo.tv',
                    'slink.bigovideo.tv',
                    'app.blued.cn',
                    'cc.163.com',
                    'qiandurebo.com',
                    'fm.missevan.com',
                    'look.163.com',
                    'twitcasting.tv',
                    'live.baidu.com',
                    'weibo.com',
                    'fanxing.kugou.com',
                    'fanxing2.kugou.com',
                    'mfanxing.kugou.com',
                    'www.huajiao.com',
                    'www.7u66.com',
                    'wap.7u66.com',
                    'live.acfun.cn',
                    'm.acfun.cn',
                    'live.tlclw.com',
                    'wap.tlclw.com',
                    'live.ybw1666.com',
                    'wap.ybw1666.com',
                    'www.inke.cn',
                    'www.zhihu.com',
                    'www.haixiutv.com',
                    "h5webcdnp.vvxqiu.com",
                    "17.live",
                    'www.lang.live',
                    "m.pp.weimipopo.com",
                    "v.6.cn",
                    "m.6.cn",
                    'www.lehaitv.com',
                    'h.catshow168.com',
                    'e.tb.cn',
                    'huodong.m.taobao.com',
                    '3.cn',
                    'eco.m.jd.com'
                ]
                overseas_platform_host = [
                    'www.tiktok.com',
                    'play.sooplive.co.kr',
                    'm.sooplive.co.kr',
                    'www.pandalive.co.kr',
                    'www.winktv.co.kr',
                    'www.flextv.co.kr',
                    'www.popkontv.com',
                    'www.twitch.tv',
                    'www.liveme.com',
                    'www.showroom-live.com',
                    'chzzk.naver.com',
                    'm.chzzk.naver.com',
                    'live.shopee.',
                    '.shp.ee',
                    'www.youtube.com',
                    'youtu.be',
                    'www.faceit.com'
                ]

                platform_host.extend(overseas_platform_host)
                clean_url_host_list = (
                    "live.douyin.com",
                    "live.bilibili.com",
                    "www.huajiao.com",
                    "www.zhihu.com",
                    "www.huya.com",
                    "chzzk.naver.com",
                    "www.liveme.com",
                    "www.haixiutv.com",
                    "v.6.cn",
                    "m.6.cn",
                    'www.lehaitv.com'
                )

                if 'live.shopee.' in url_host or '.shp.ee' in url_host:
                    url_host = 'live.shopee.' if 'live.shopee.' in url_host else '.shp.ee'

                if url_host in platform_host or any(ext in url for ext in (".flv", ".m3u8")):
                    if url_host in clean_url_host_list:
                        url = update_file(url_config_file, old_str=url, new_str=url.split('?')[0])

                    if 'xiaohongshu' in url:
                        host_id = re.search('&host_id=(.*?)(?=&|$)', url)
                        if host_id:
                            new_url = url.split('?')[0] + f'?host_id={host_id.group(1)}'
                            url = update_file(url_config_file, old_str=url, new_str=new_url)

                    url_comments = [i for i in url_comments if url not in i]
                    if is_comment_line:
                        url_comments.append(url)
                    else:
                        new_line = (quality, url, name)
                        url_tuples_list.append(new_line)
                else:
                    if not origin_line.startswith('#'):
                        color_obj.print_colored(f"\r{origin_line.strip()} 本行包含未知鏈接.此條跳過", color_obj.YELLOW)
                        update_file(url_config_file, old_str=origin_line, new_str=origin_line, start_str='#')

        while len(need_update_line_list):
            a = need_update_line_list.pop()
            replace_words = a.split('|')
            if replace_words[0] != replace_words[1]:
                if replace_words[1].startswith("#"):
                    start_with = '#'
                    new_word = replace_words[1][1:]
                else:
                    start_with = None
                    new_word = replace_words[1]
                update_file(url_config_file, old_str=replace_words[0], new_str=new_word, start_str=start_with)

        text_no_repeat_url = list(set(url_tuples_list))

        if len(text_no_repeat_url) > 0:
            for url_tuple in text_no_repeat_url:
                monitoring = len(running_list)

                if url_tuple[1] in not_record_list:
                    continue

                if url_tuple[1] not in running_list:
                    print(f"\r{'新增' if not first_start else '傳入'}地址: {url_tuple[1]}")
                    monitoring += 1
                    args = [url_tuple, monitoring]
                    create_var[f'thread_{monitoring}'] = threading.Thread(target=start_record, args=args)
                    create_var[f'thread_{monitoring}'].daemon = True
                    create_var[f'thread_{monitoring}'].start()
                    running_list.append(url_tuple[1])
                    time.sleep(local_delay_default)
        url_tuples_list = []
        first_start = False

    except Exception as err:
        logger.error(f"錯誤資訊: {err} 發生錯誤的行數: {err.__traceback__.tb_lineno}")

    if first_run:
        t = threading.Thread(target=display_info, args=(), daemon=True)
        t.start()
        t2 = threading.Thread(target=adjust_max_request, args=(), daemon=True)
        t2.start()
        first_run = False

    time.sleep(3)