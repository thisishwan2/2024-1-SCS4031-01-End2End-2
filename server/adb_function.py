import subprocess

from com.dtmilano.android.viewclient import ViewClient

def find_by_id_touch(key):
    print("id_touch")
    vc = ViewClient(*ViewClient.connectToDeviceOrExit())
    vc.findViewById('id/no_id/'+key).touch()

def find_by_id_touch_type(key, text):
    print("typing")
    # vc = ViewClient(*ViewClient.connectToDeviceOrExit())
    # vc.traverse(transform=vc.traverseShowClassIdTextAndUniqueId)
    # edit_text_view = vc.findViewById('id/no_id/'+key)
    # if edit_text_view and isinstance(edit_text_view, EditText):
    #     edit_text_view.setText(text)

    # vc = ViewClient(*ViewClient.connectToDeviceOrExit(), useuiautomatorhelper=True)
    #
    # oid = vc.uiAutomatorHelper.ui_device.find_object(clazz='android.widget.EditText').oid
    # vc.uiAutomatorHelper.ui_object2.set_text(oid, text)
    try:
        # adb에는 한글 지원 이슈가 존재함. 따라서 adb 키보드를 다운받아서 사용한다.
        subprocess.run("adb shell ime set com.android.adbkeyboard/.AdbIME", shell=True)

        # 공백은 다음과 같이 처리해야한다. "안녕하세\ 요"
        split_text = text.split()
        if len(split_text) >= 2:
            parse_text = ""
            for i in split_text:
                parse_text += i + "\ "
            text = parse_text

        cmd = "adb shell am broadcast -a ADB_INPUT_TEXT --es msg "+text
        subprocess.run(cmd, shell=True)

        # 삼성 키패드로 변경
        subprocess.run("adb shell ime set com.sec.android.inputmethod/.SamsungKeypad", shell=True)
    except Exception as e:
        print(e)
        subprocess.run("adb shell ime set com.sec.android.inputmethod/.SamsungKeypad", shell=True)




def back(key):
    print("back")
    cmd = "adb shell input keyevent 4"
    subprocess.run(cmd, shell=True)

def home(key):
    print("home")
    cmd = "adb shell input keyevent 3"
    subprocess.run(cmd, shell=True)

def swipe_left_to_right(key):
    print("swipe")
    cmd = "adb shell input swipe 1000 500 100 500 100"
    subprocess.run(cmd, shell=True)

def swipe_right_to_left(key):
    print("swipe")
    cmd = "adb shell input swipe 100 500 1000 500 100"
    subprocess.run(cmd, shell=True)

def swipe_up_to_down(key):
    print("swipe down")
    cmd = "adb shell input swipe 500 1000 500 500 100"
    subprocess.run(cmd, shell=True)

def swife_down_to_up(key):
    print("swipe up")
    cmd = "adb shell input swipe 500 500 500 1000 100"
    subprocess.run(cmd, shell=True)