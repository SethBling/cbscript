@rem To make double clicking cbscript files work, modify:
@rem \HKEY_CLASSES_ROOT\cbscript_auto_file\shell\open\com
@rem Set the string value to the file location of this file followed by "%1"
@rem For example: "D:\Dropbox\Projects\Python\CBScript 1.16\run.cmd" "%1"
@ECHO CBScript 1.16
@title %~nx1
@cd "D:\Dropbox\Projects\Python\CBScript 1.16\"
@c:\python27\python compile.py %1
@pause