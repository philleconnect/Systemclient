rmdir /s /Q dist
rmdir /s /Q build
pyinstaller --onefile --path=C:\Users\Johannes\Documents\GitHub\systemclient-v2\modules --icon=icon.ico -w systemclient.py
pyinstaller --onefile --path=C:\Users\Johannes\Documents\GitHub\systemclient-v2\modules --icon=icon.ico -w dkmp.py
