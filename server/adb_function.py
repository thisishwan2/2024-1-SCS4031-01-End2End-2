import subprocess

from service import vc

def find_by_id_touch(key):
    print("id_touch")
    vc.findViewById('id/no_id/'+key).touch()

def find_by_text_touch(key):
    print("text_touch")
    vc.findViewWithText(key).touch()

def find_by_id_touch_type(key, text):
    vc.findViewById('id/no_id/' + key).type(text)

def find_by_text_touch_type(key, text):
    vc.findViewWithText(key).type(text)

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


