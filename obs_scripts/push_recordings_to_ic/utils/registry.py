import winreg

# Note, please enable the reg switch
# [HKEY_CURRENT_USER\SOFTWARE\Overwolf\CEF]
# "enable-features"="enable-dev-tools"

CEF_KEY = r"SOFTWARE\Overwolf\CEF"
ENABLE_DEV_MODE_KEY = "enable-features"
ENABLE_DEV_MODE_VALUE = "enable-dev-tools"


def isInDevMode():
    # winreg.CreateKey(winreg.HKEY_CURRENT_USER, CEF_KEY)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CEF_KEY, 0, winreg.KEY_READ) as key: 
            value, _ = winreg.QueryValueEx(key, ENABLE_DEV_MODE_KEY)

            if value == ENABLE_DEV_MODE_VALUE:
                winreg.CloseKey(key)
                return True

            winreg.CloseKey(key)
            return True


    # Fires when the code doesn't exist
    except FileNotFoundError as e:
        return False



def enableDevMode():
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, CEF_KEY)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, CEF_KEY, 0, winreg.KEY_WRITE)

        winreg.SetValueEx(key, ENABLE_DEV_MODE_KEY, 0, winreg.REG_SZ, ENABLE_DEV_MODE_VALUE)
        winreg.CloseKey(key)

    except OSError as e:
        print("Had trouble setting overwolf's cef to its dev mode") 
        print(e)
