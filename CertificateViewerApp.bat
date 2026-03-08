@echo off
REM ############################################################################################################
REM ##                                 Certificate Viewer Tool                                                ##
REM ##                                                                                                        ##
REM ## This Script is developed by Shankar N G                                                                ##
REM ## It is to trigger the Certificate Viewer Tool application                                               ##
REM ## The application reads the backend system list and makes a live call to fetch SSL certificate details   ##
REM ## It fetches and sorts certificates into Red, Yellow and Green bins based on expiry date                 ##
REM ## This Script is for Windows Command Prompt / Task Scheduler                                             ##
REM ## Please edit the APP_DIR path to point to where the application is installed                            ##
REM ## Make sure the virtual environment and requirements are set up before running                            ##
REM ############################################################################################################

SET APP_DIR=%USERPROFILE%\PythonProjects\CertificateViewerTool
SET LOG_DIR=%APP_DIR%\logs

REM Create log directory if it does not exist
IF NOT EXIST "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Generate timestamped log filename
FOR /F "tokens=1-6 delims=/:. " %%A IN ("%DATE% %TIME%") DO (
    SET LOG_FILE=%LOG_DIR%\certificate_viewer_%%C%%B%%A_%%D%%E%%F.log
)

echo ==============================================
echo   Starting Certificate Viewer Tool
echo   Started at: %DATE% %TIME%
echo   Logs: %LOG_FILE%
echo ==============================================

REM Navigate to application directory
IF NOT EXIST "%APP_DIR%" (
    echo ERROR: Application directory not found: %APP_DIR%
    pause
    exit /b 1
)
cd /d "%APP_DIR%"

REM Activate virtual environment if it exists
IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated.
) ELSE (
    echo WARNING: Virtual environment not found. Running with system Python.
)

REM Run the application in the background using START so terminal can be closed
echo Starting Certificate Viewer Tool in background...
START "CertificateViewerTool" /B python -m app.main >> "%LOG_FILE%" 2>&1

echo ==============================================
echo   Application is running in the background
echo   To view logs, open: %LOG_FILE%
echo   To stop the application, close the process
echo   from Task Manager ^(python.exe^)
echo ==============================================

REM Deactivate virtual environment
IF EXIST ".venv\Scripts\deactivate.bat" (
    call .venv\Scripts\deactivate.bat
)

pause
