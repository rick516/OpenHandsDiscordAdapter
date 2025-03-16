@echo off
echo Starting OpenHandsDiscordAdapter Bot...
cd /d %~dp0
python -m src.__main__
if %ERRORLEVEL% NEQ 0 (
    echo Bot crashed with error code %ERRORLEVEL%
    echo Check the logs for more information
    timeout /t 10
)
pause 