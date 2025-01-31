@echo off
setlocal enabledelayedexpansion

:: 配置下载链接和文件名
set "URL=http://plana.ink/update_app/lastest_data"
set "ZIPFILE=lastest_data.zip"
set "DESTINATION=."  :: 解压目标目录

:: 使用 curl 下载 ZIP 文件
echo 正在下载文件...
curl -o "%ZIPFILE%" "%URL%" --silent --fail
if %ERRORLEVEL% neq 0 (
    echo 下载失败，请检查网络连接或 URL 是否正确！
    exit /b 1
)

:: 检查是否下载成功
if not exist "%ZIPFILE%" (
    echo 下载失败，文件未找到！
    exit /b 1
)

:: 解压 ZIP 文件（需要 7z 或 tar）
echo 正在解压文件...
:: 如果已经安装 7z
tar -xf "%ZIPFILE%" -C "%DESTINATION%"
if %ERRORLEVEL% neq 0 (
    echo 解压失败，请确保你已经安装 7z 或 tar！
    exit /b 1
)

:: 清理 ZIP 文件
del "%ZIPFILE%"

echo 完成！
pause

