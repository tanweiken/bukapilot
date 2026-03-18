#!/usr/bin/env python3
import os
import time
from openpilot.common.swaglog import cloudlog
from openpilot.common.params import Params

DRM_STATUS_PATH = "/sys/class/drm/card0-DP-1/status"

DISPLAY_STATE_PATH = "/var/tmp/display_connected"

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

      if last_status is None or status != last_status:
        cloudlog.warning(f"displayd: display status changed to {status}")
        if status == "connected":
          with open(DISPLAY_STATE_PATH, "w") as f:
            f.write("1")
          # Ensure Weston is running. If it failed at boot due to no output, we restart it.
          os.system("sudo systemctl restart weston")
          # Force kill any hanging UI process to ensure a clean start on the new display
          os.system("pkill -SIGKILL ui")
        else:
          if os.path.exists(DISPLAY_STATE_PATH):
            os.remove(DISPLAY_STATE_PATH)
        
      last_status = status
    except Exception:
      cloudlog.exception("displayd: error")
      if os.path.exists(DISPLAY_STATE_PATH):
        os.remove(DISPLAY_STATE_PATH)
      
    time.sleep(1.0)

if __name__ == "__main__":
  main()
