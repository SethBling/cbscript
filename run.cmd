@rem To make double clicking cbscript files work, modify:
@rem \HKEY_CLASSES_ROOT\cbscript_auto_file\shell\open\com
@ECHO CBScript 1.15
@title %~nx1
@cd "D:\Dropbox\Projects\Python\CBScript 1.15\"
@c:\python27\python compile.py %1
@pause