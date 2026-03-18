#!/usr/bin/env python3
import os
import time
from openpilot.common.swaglog import cloudlog

DRM_STATUS_PATH = "/sys/class/drm/card0-DP-1/status"

def main():
  last_status = None

  cloudlog.info("displayd: started")

  while True:
    try:
      if os.path.exists(DRM_STATUS_PATH):
        with open(DRM_STATUS_PATH, "r") as f:
          status = f.read().strip()
      else:
        status = "disconnected"

      if last_status is None:
        last_status = status
        
      if status != last_status:
        cloudlog.warning(f"displayd: display status changed to {status}")
        if status == "connected":
          # 1. Restart Weston to ensure it picks up the new output and creates a fresh socket
          cloudlog.info("displayd: restarting weston")
          os.system("sudo systemctl restart weston")
          
          # 2. Wait for the Wayland socket to appear
          socket_path = "/var/tmp/weston/wayland-0"
          for _ in range(20):
            if os.path.exists(socket_path):
              cloudlog.info("displayd: wayland socket is ready")
              break
            time.sleep(0.5)
          
          # 3. Force kill UI process to ensure it connects to the fresh Weston instance
          os.system("pkill -SIGKILL ui")
        
      last_status = status
    except Exception:
      cloudlog.exception("displayd: error")

    time.sleep(1.0)

if __name__ == "__main__":
  main()
