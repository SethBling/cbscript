@echo off
rem To make double clicking cbscript files work, either:
rem 1. Run file_assoc.cmd
rem 2. Modify
rem     \HKEY_CLASSES_ROOT\cbscript_auto_file\shell\open\command
rem     Set the string value to the file location of this file followed by "%1"
rem     For example: "D:\Dropbox\Projects\Python\CBScript 1.16\run.cmd" "%1"
rem
rem To generate blocks.json, via command prompt at the minecraft server:
rem java -DbundlerMainClass=net.minecraft.data.Main -jar {jar_path} --server --reports

echo CBScript 1.20
title %~nx1

if "%1" == "" (
    echo You must specify a file path.
    exit /b
)

if not exist "%1" (
    echo The specified file does not exist.
    exit /b
)

cd "%~dp0"

if not defined PYTHON27 set PYTHON27=c:\python27\python
if exist "%PYTHON27%" (
    py -2.7 compile.py %1
) else (
    py compile.py %1
)

pause