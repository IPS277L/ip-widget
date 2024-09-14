import ctypes
import os
import socket
import sys
import threading

import winshell
from PIL import Image
from pystray import Icon, Menu, MenuItem
from win32com.client import Dispatch

from constants import IPServices


class Application:

    DEFAULT_IP_SERVICE = IPServices.FreeIPAPI

    def __init__(self):
        self._stop_thread = threading.Event()
        self._images_path = os.path.join(os.path.abspath('.'), 'assets/images')

        self._ip_services = {
            ip_service.name: {
                'class': ip_service.value,
                'state': False
            }
            for ip_service in IPServices
        }
        self._startup_status = self._check_startup_status()

        self._icon = Icon('ip-widget')
        self._icon.menu = Menu(
            MenuItem('Refresh', action=self._refresh_ip_manual),
            MenuItem(
                'IP Service',
                Menu(
                    *[
                        MenuItem(
                            ip_service.name,
                            action=self._select_ip_service,
                            checked=lambda _, ip_service_name=ip_service.name: self._ip_service_state(ip_service_name)
                        )
                        for ip_service in IPServices 
                    ]
                )
            ),
            MenuItem('Startup', action=self._toggle_startup, checked=lambda _: self._startup_status),
            MenuItem('Exit', action=self._stop),
        )

        self._ip_service = self.DEFAULT_IP_SERVICE.value()
        self._ip_services[self.DEFAULT_IP_SERVICE.name]['state'] = True

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

    def _set_default_icon(self):
        flag_image = Image.open(f"{self._images_path}/aq.png")
        self._icon.icon = self._prepare_tray_icon(flag_image)

    def _refresh_ip(self):
        country_code = self._ip_service.get_country_code()

        if country_code:
            flag_image = Image.open(f"{self._images_path}/{country_code.lower()}.png")
            self._icon.icon = self._prepare_tray_icon(flag_image)
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

    def _ip_service_state(self, ip_service: str) -> bool:
        return self._ip_services[ip_service]['state']

    def _select_ip_service(self, icon: Menu, item: MenuItem):
        self._ip_services = {key: {**value, 'state': False} for key, value in self._ip_services.items()}
        self._ip_services[item.text]['state'] = True

        self._ip_service = self._ip_services[item.text]['class']()

        self._set_default_icon()
        self._refresh_ip()

    def _refresh_ip_manual(self, icon: Menu, item: MenuItem):
        self._set_default_icon()
        self._refresh_ip()

    def _stop(self, icon: Menu, item: MenuItem):
        self._stop_thread.set()
        icon.stop()

    def run(self):
        threading.Thread(target=self._monitor_network_change, daemon=True).start()
        self._icon.run()


if __name__ == '__main__':
    app = Application()
    app.run()
