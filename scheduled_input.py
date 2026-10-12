"""예약 시각에 동적 창 제목을 찾아 메시지 또는 TXT 내용을 입력합니다."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pyperclip
import win32api
import win32con
import win32gui
import win32process


# ======================== 사용자 설정 ========================
RUN_AT = "2026-10-12 19:05"  # 예약 시각: YYYY-MM-DD HH:MM 형식. 즉시 실행하려면 ""로 비워 두세요.
TEXT_FILE = r"C:\Users\CNXK\Downloads\리셋할일1.txt"
MESSAGE = ""  # 직접 입력하려면 TEXT_FILE을 비우고 여기에 입력

WINDOW_TITLE_PREFIX = "pipeline-26-2h-"
# 비워 두면 창 제목만으로 찾습니다. 필요할 때만 프로세스 필터를 사용하세요.
PROCESS_NAMES: set[str] = set()
PRESS_ENTER = True
CLIPBOARD_RESTORE = True
SEARCH_TIMEOUT_SECONDS = 30
PASTE_DELAY_SECONDS = 0.15
# =============================================================


def read_content() -> str:
    if TEXT_FILE and MESSAGE:
        raise ValueError("TEXT_FILE과 MESSAGE 중 하나만 사용하세요.")
    if TEXT_FILE:
        return Path(TEXT_FILE).read_text(encoding="utf-8-sig")
    if MESSAGE:
        return MESSAGE
    raise ValueError("TEXT_FILE 또는 MESSAGE를 설정하세요.")


def visible_windows() -> list[tuple[int, str, str]]:
    found: list[tuple[int, str, str]] = []

    def callback(hwnd: int, _extra: object) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        # 제목 앞에 "✳ " 같은 상태 표시가 붙어도 찾을 수 있도록 포함 여부를 사용합니다.
        if WINDOW_TITLE_PREFIX not in title:
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process_name = __import__("psutil").Process(pid).name()
        except Exception:
            process_name = ""
        if PROCESS_NAMES and process_name not in PROCESS_NAMES:
            return
        found.append((hwnd, title, process_name))

    win32gui.EnumWindows(callback, None)
    return found


def wait_for_target(start_hwnd: int) -> tuple[int, str, str]:
    if not WINDOW_TITLE_PREFIX:
        if not start_hwnd or not win32gui.IsWindow(start_hwnd):
            raise TimeoutError("스크립트를 실행한 현재 창을 확인하지 못했습니다.")
        return start_hwnd, win32gui.GetWindowText(start_hwnd), "current window"

    deadline = time.monotonic() + SEARCH_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        matches = visible_windows()
        if matches:
            return matches[0]
        time.sleep(0.5)
    visible = []
    win32gui.EnumWindows(
        lambda hwnd, _: visible.append(win32gui.GetWindowText(hwnd))
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd)
        else None,
        None,
    )
    sample = ", ".join(repr(title) for title in visible[:8])
    raise TimeoutError(
        f"대상 창을 찾지 못했습니다: {WINDOW_TITLE_PREFIX!r}. "
        f"현재 보이는 창 예시: {sample}"
    )


def paste_and_submit(hwnd: int, content: str) -> None:
    old_clipboard = pyperclip.paste() if CLIPBOARD_RESTORE else None
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        pyperclip.copy(content)
        time.sleep(PASTE_DELAY_SECONDS)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord("V"), 0, 0, 0)
        win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        if PRESS_ENTER:
            time.sleep(PASTE_DELAY_SECONDS)
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    finally:
        if CLIPBOARD_RESTORE and old_clipboard is not None:
            time.sleep(PASTE_DELAY_SECONDS)
            pyperclip.copy(old_clipboard)


def main() -> None:
    start_hwnd = win32gui.GetForegroundWindow()
    content = read_content()
    if RUN_AT:
        target_time = datetime.strptime(RUN_AT, "%Y-%m-%d %H:%M")
        seconds = (target_time - datetime.now()).total_seconds()
        if seconds > 0:
            print(f"{target_time:%Y-%m-%d %H:%M}까지 대기합니다.")
            time.sleep(seconds)
    hwnd, title, process_name = wait_for_target(start_hwnd)
    paste_and_submit(hwnd, content)
    print(f"완료: {title} ({process_name}), {len(content)}자 입력")


if __name__ == "__main__":
    main()
