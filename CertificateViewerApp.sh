#!/bin/bash
############################################################################################################
##                                 Certificate Viewer Tool                                                ##
##                                                                                                        ##
## This Script is developed by Shankar N G                                                                ##
## It is to trigger the Certificate Viewer Tool application                                               ##
## The application reads the backend system list and makes a live call to fetch SSL certificate details   ##
## It fetches and sorts certificates into Red, Yellow, and Green bins based on expiry date                ##
## This Script is for Linux Terminal                                                                      ##
## Please edit the APP_DIR path to point to where the application is installed                            ##
## Make sure the virtual environment and requirements are set up before running                            ##
############################################################################################################

APP_DIR=~/PythonProjects/CertificateViewerTool
LOG_DIR=$APP_DIR/logs
LOG_FILE=$LOG_DIR/certificate_viewer_$(date +%Y%m%d_%H%M%S).log

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "=============================================="
echo "  Starting Certificate Viewer Tool"
echo "  Started at: $(date)"
echo "  Logs: $LOG_FILE"
echo "=============================================="

# Navigate to application directory
cd "$APP_DIR" || { echo "ERROR: Application directory not found: $APP_DIR"; exit 1; }

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "Virtual environment activated."
else
    echo "WARNING: Virtual environment not found. Running with system Python."
fi

# Run the application with nohup so it keeps running after terminal closes
nohup python -m app.main >> "$LOG_FILE" 2>&1 &

APP_PID=$!
echo "Certificate Viewer Tool started with PID: $APP_PID"
echo "To stop the application, run: kill $APP_PID"
echo "To view logs, run: tail -f $LOG_FILE"

# Save PID to file for easy reference later
echo $APP_PID > "$APP_DIR/certificate_viewer.pid"
echo "PID saved to: $APP_DIR/certificate_viewer.pid"

# Deactivate virtual environment in current shell
deactivate 2>/dev/null

echo "=============================================="
echo "  Application is running in the background"
echo "=============================================="
