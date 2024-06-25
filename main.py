import ctypes
import os
import socket
import sys
import threading
from http import HTTPStatus
from typing import Union

import requests
import winshell
from PIL import Image
from pystray import Icon, Menu, MenuItem
from win32com.client import Dispatch


class Application:

    def __init__(self):
        self._stop_thread = threading.Event()
        self._images_path = os.path.join(os.path.abspath('.'), 'assets/images')

        self._startup_status = self._check_startup_status()

        self._icon = Icon('ip-widget')
        self._icon.menu = Menu(
            MenuItem('Startup', action=self._toggle_startup, checked=lambda _: self._startup_status),
            MenuItem('Exit', action=self._stop),
        )

        self._set_default_icon()
        self._refresh_ip()

    @property
    def _shortcut_path(self) -> str:
        startup_folder = winshell.startup()
        return os.path.join(startup_folder, 'ip-widget.lnk')

    @staticmethod
    def _prepare_tray_icon(flag: Image) -> Image:
        flag_w, flag_h = flag.size
        image_w, image_h = flag_w, flag_w

        offset = ((image_w - flag_w) // 2, (image_h - flag_h) // 2)

        background = Image.new('RGBA', (image_w, image_h), (0, 0, 0, 0))
        background.paste(flag, offset)

        return background

    @staticmethod
    def _get_ip_info() -> Union[dict, bool]:
        service_url = 'http://ip-api.com/json/'

        try:
            response = requests.get(service_url)
        except Exception:
            return False

        if response.status_code == HTTPStatus.OK:
            ip_data = response.json()
            return ip_data

        return False

    def _set_default_icon(self):
        flag_image = Image.open(f"{self._images_path}/aq.png")

        self._icon.icon = self._prepare_tray_icon(flag_image)
        self._icon.title = ''

    def _refresh_ip(self):
        ip_info = self._get_ip_info()

        if ip_info:
            flag_image = Image.open(f"{self._images_path}/{ip_info['countryCode'].lower()}.png")

            self._icon.icon = self._prepare_tray_icon(flag_image)
            self._icon.title = ip_info['query']
        else:
            self._set_default_icon()

    def _is_network_change_completed(self) -> bool:
        try:
            socket.create_connection(('8.8.8.8', 53), timeout=15)
            return True
        except Exception:
            return False

    def _monitor_network_change(self):
        iphlpapi = ctypes.WinDLL('iphlpapi.dll')

        NotifyAddrChange = iphlpapi.NotifyAddrChange
        NotifyAddrChange.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]
        NotifyAddrChange.restype = ctypes.wintypes.DWORD

        notify_handle = ctypes.c_void_p()

        while not self._stop_thread.is_set():
            result = NotifyAddrChange(ctypes.byref(notify_handle), None)

            if result == 0:
                self._set_default_icon()

                if self._is_network_change_completed():
                    self._refresh_ip()

    def _check_startup_status(self) -> bool:
        return os.path.exists(self._shortcut_path)

    def _add_to_startup(self):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(self._shortcut_path)

        python_executable = sys.executable
        script_path = os.path.abspath(sys.argv[0])

        shortcut.TargetPath = python_executable
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()

    def _remove_from_startup(self):
        if os.path.exists(self._shortcut_path):
            os.remove(self._shortcut_path)

    def _toggle_startup(self, icon: Menu, item: MenuItem):
        if self._startup_status:
            self._remove_from_startup()
            self._startup_status = False
        else:
            self._add_to_startup()
            self._startup_status = True

    def _stop(self, icon: Menu, item: MenuItem):
        self._stop_thread.set()
        icon.stop()

    def run(self):
        threading.Thread(target=self._monitor_network_change, daemon=True).start()
        self._icon.run()


if __name__ == '__main__':
    app = Application()
    app.run()
