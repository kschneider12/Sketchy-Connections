@echo off
setlocal

set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%"

set "PYTHON_CMD="
set "USE_PYINSTALLER_EXE=0"
set "ICON_PATH=%~1"

where pyinstaller >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "USE_PYINSTALLER_EXE=1"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=py -3"
    ) else (
        where python >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_CMD=python"
        )
    )

    if "%PYTHON_CMD%"=="" (
        echo Could not find pyinstaller, py, or python.
        echo Install Python and PyInstaller, then retry.
        set "EXIT_CODE=1"
        goto :end
    )

    call %PYTHON_CMD% -c "import PyInstaller" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo PyInstaller is not installed for %PYTHON_CMD%.
        echo Install with: %PYTHON_CMD% -m pip install pyinstaller
        set "EXIT_CODE=1"
        goto :end
    )
)

if "%USE_PYINSTALLER_EXE%"=="1" (
    if "%ICON_PATH%"=="" (
        pyinstaller ^
          --noconfirm ^
          --clean ^
          --windowed ^
          --name SketchyConnections ^
          --paths client ^
          --paths shared ^
          --add-data "client/assets;assets" ^
          client/sketchy_client/main.py
    ) else (
        pyinstaller ^
          --noconfirm ^
          --clean ^
          --windowed ^
          --name SketchyConnections ^
          --paths client ^
          --paths shared ^
          --add-data "client/assets;assets" ^
          --icon "%ICON_PATH%" ^
          client/sketchy_client/main.py
    )
) else (
    if "%ICON_PATH%"=="" (
        call %PYTHON_CMD% -m PyInstaller ^
          --noconfirm ^
          --clean ^
          --windowed ^
          --name SketchyConnections ^
          --paths client ^
          --paths shared ^
          --add-data "client/assets;assets" ^
          client/sketchy_client/main.py
    ) else (
        call %PYTHON_CMD% -m PyInstaller ^
          --noconfirm ^
          --clean ^
          --windowed ^
          --name SketchyConnections ^
          --paths client ^
          --paths shared ^
          --add-data "client/assets;assets" ^
          --icon "%ICON_PATH%" ^
          client/sketchy_client/main.py
    )
)

if %ERRORLEVEL% NEQ 0 (
    set "EXIT_CODE=%ERRORLEVEL%"
    goto :end
)

echo Build complete: dist\SketchyConnections
set "EXIT_CODE=0"

:end
popd
exit /b %EXIT_CODE%
