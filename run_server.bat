@echo off
setlocal

set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%"

set "PYTHONPATH=%ROOT_DIR%server;%ROOT_DIR%shared"

if "%SKETCHY_SERVER_HOST%"=="" set "SKETCHY_SERVER_HOST=0.0.0.0"
if "%SKETCHY_SERVER_PORT%"=="" set "SKETCHY_SERVER_PORT=8000"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -m uvicorn sketchy_server.app.main:app --host %SKETCHY_SERVER_HOST% --port %SKETCHY_SERVER_PORT%
) else (
    python -m uvicorn sketchy_server.app.main:app --host %SKETCHY_SERVER_HOST% --port %SKETCHY_SERVER_PORT%
)

set "EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %EXIT_CODE%
