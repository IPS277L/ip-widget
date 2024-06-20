import os
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

    _refresh_interval = 15

    def __init__(self):
        self._stop_thread = threading.Event()
        self._images_path = os.path.join(os.path.abspath('.'), 'assets/images')

        self._current_ip = None
        self._startup_status = self._check_startup_status()

        self._icon = Icon('ip-widget')
        self._icon.icon = Image.open(f"{self._images_path}/default.png")
        self._icon.menu = Menu(
            MenuItem('Startup', action=self._toggle_startup, checked=lambda _: self._startup_status),
            MenuItem('Exit', action=self._stop),
        )

    @property
    def _shortcut_path(self) -> str:
        startup_folder = winshell.startup()
        return os.path.join(startup_folder, 'ip-widget.lnk')

    @staticmethod
    def _get_ip_info() -> Union[dict, bool]:
        service_url = 'http://ip-api.com/json/'

        try:
            response = requests.get(service_url)
        except ConnectionError:
            return False

        if response.status_code == HTTPStatus.OK:
            ip_data = response.json()
            return ip_data

        return False

    def _refresh_ip(self):
        while True:
            ip_info = self._get_ip_info()

            if ip_info:
                ip_address = ip_info['query']

                if ip_address != self._current_ip:
                    self._current_ip = ip_address
                    self._icon.icon = Image.open(f"{self._images_path}/{ip_info['countryCode']}.png")
                    self._icon.title = ip_address
            else:
                self._current_ip = None
                self._icon.icon = Image.open(f"{self._images_path}/default.png")

            self._stop_thread.wait(self._refresh_interval)

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
        threading.Thread(target=self._refresh_ip, daemon=True).start()
        self._icon.run()


if __name__ == '__main__':
    app = Application()
    app.run()
