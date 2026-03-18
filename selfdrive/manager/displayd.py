#!/usr/bin/env python3
import os
import time
from openpilot.common.swaglog import cloudlog
from openpilot.common.params import Params

DRM_STATUS_PATH = "/sys/class/drm/card0-DP-1/status"

def main():
  params = Params()
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
        params.put_bool("DisplayConnected", status == "connected")
        
      if status != last_status:
        cloudlog.warning(f"displayd: display status changed to {status}")
        params.put_bool("DisplayConnected", status == "connected")
        if status == "connected":
          # Ensure Weston is running. If it failed at boot due to no output, we restart it.
          os.system("sudo systemctl restart weston")
          # Force kill any hanging UI process to ensure a clean start on the new display
          os.system("pkill -SIGKILL ui")
        
      last_status = status
    except Exception:
      cloudlog.exception("displayd: error")
      
    time.sleep(1.0)

if __name__ == "__main__":
  main()
