@echo off
setlocal

set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%"

set "PYTHONPATH=%ROOT_DIR%client;%ROOT_DIR%shared"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -m sketchy_client.main
) else (
    python -m sketchy_client.main
)

set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
