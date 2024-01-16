@rem To make double clicking cbscript files work, modify:
@rem \HKEY_CLASSES_ROOT\cbscript_auto_file\shell\open\command
@rem Set the string value to the file location of this file followed by "%1"
@rem For example: "D:\Dropbox\Projects\Python\CBScript 1.16\run.cmd" "%1"
@rem
@rem To generate blocks.json, via command prompt at the minecraft server:
@rem java -DbundlerMainClass=net.minecraft.data.Main -jar {jar_path} --server --reports
@ECHO CBScript 1.20
@title %~nx1
@cd "D:\Dropbox\Projects\Python\CBScript 1.20\"
@c:\python27\python compile.py %1
@pause