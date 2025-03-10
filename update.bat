@echo off
setlocal enabledelayedexpansion

set "URL=http://plana.ink/update_app/lastest_data"
set "ZIPFILE=lastest_data.zip"
set "DESTINATION=."  

echo ���������ļ�...
curl -o "%ZIPFILE%" "%URL%" --silent --fail
if %ERRORLEVEL% neq 0 (
    echo ����ʧ�ܣ������������ӻ� URL �Ƿ���ȷ��
    exit /b 1
)

if not exist "%ZIPFILE%" (
    echo ����ʧ�ܣ��ļ�δ�ҵ���
    exit /b 1
)

echo ���ڽ�ѹ�ļ�...
tar -xf "%ZIPFILE%" -C "%DESTINATION%"
if %ERRORLEVEL% neq 0 (
    echo ��ѹʧ�ܣ���ȷ�����Ѿ���װ 7z �� tar��
    exit /b 1
)

del "%ZIPFILE%"

echo ��ɣ�
pause

