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
