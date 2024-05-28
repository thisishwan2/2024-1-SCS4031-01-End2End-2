import subprocess
import time

from com.dtmilano.android.viewclient import ViewClient

def find_by_id_touch(key,serial_no):
    print("id_touch")
    vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
    vc.findViewById('id/no_id/'+key).touch()

# def find_by_text_touch(key, serial_no):
#     print("id_touch")
#     vc = ViewClient(*ViewClient.connectToDeviceOrExit(serialno=serial_no))
#     vc.findViewById('id/no_id/' + key).touch()

def find_by_id_touch_type(key, text, serial_no):
    print("typing")

    vc = ViewClient(*ViewClient.connectToDeviceOrExit())
    vc.findViewById('id/no_id/' + key).touch()
    # cmd = f"adb su -c shell input text \"{text}\""
    # subprocess.run(cmd, shell=True)
    cmd = f"adb -s {serial_no} shell input text \"{text}\""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

def back():
    print("back")
    cmd = "adb shell input keyevent 4"
    subprocess.run(cmd, shell=True)

def home():
    print("home")
    cmd = "adb shell input keyevent 3"
    subprocess.run(cmd, shell=True)

def swipe_left_to_right():
    print("swipe")
    cmd = "adb shell input swipe 1000 500 100 500 100"
    subprocess.run(cmd, shell=True)

def swipe_right_to_left():
    print("swipe")
    cmd = "adb shell input swipe 100 500 1000 500 100"
    subprocess.run(cmd, shell=True)

def swipe_up_to_down():
    print("swipe down")
    cmd = "adb shell input swipe 500 1000 500 500 100"
    subprocess.run(cmd, shell=True)

def swife_down_to_up():
    print("swipe up")
    cmd = "adb shell input swipe 500 500 500 1000 100"
    subprocess.run(cmd, shell=True)