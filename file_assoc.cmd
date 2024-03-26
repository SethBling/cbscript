@echo off
rem This script associates the .cbscript file extension with
rem the corresponding commmand to compile it, located in run.cmd

:admincheck
    rem Checks if the file is running with administrator privileges
    if "%PROCESSOR_ARCHITECTURE%" equ "amd64" (
        >nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
    ) else (
        >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
    )

    if "%errorlevel%" equ "0" goto main

:noadmin
    echo Not running as administrator.
    echo Requesting administrative privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0'"
    exit /b

:main
    assoc .cbscript=CBScript
    ftype CBScript=%~dp0run.cmd "%%1" %%*

    echo.
    echo Successfully associated CBScript (.cbscript) files

    pause