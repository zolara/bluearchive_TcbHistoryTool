@echo off
setlocal enabledelayedexpansion

set "URL=http://plana.ink/update_app/lastest_data"
set "ZIPFILE=lastest_data.zip"
set "DESTINATION=."  

echo 正在下载文件...
curl -o "%ZIPFILE%" "%URL%" --silent --fail
if %ERRORLEVEL% neq 0 (
    echo 下载失败，请检查网络连接或 URL 是否正确！
    exit /b 1
)

if not exist "%ZIPFILE%" (
    echo 下载失败，文件未找到！
    exit /b 1
)

echo 正在解压文件...
tar -xf "%ZIPFILE%" -C "%DESTINATION%"
if %ERRORLEVEL% neq 0 (
    echo 解压失败，请确保你已经安装 7z 或 tar！
    exit /b 1
)

del "%ZIPFILE%"

echo 完成！
pause

