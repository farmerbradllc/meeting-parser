@echo off
REM Wayne County Meeting Minutes Bulk Downloader (Windows)
REM This script helps download multiple meeting minutes PDFs

echo Wayne County Meeting Minutes Downloader
echo ========================================
echo.

REM Base URL for PDFs
set BASE_URL=https://www.co.wayne.in.us/minutes/archive/cw

REM Create output directory
set OUTPUT_DIR=wayne_county_minutes
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
cd "%OUTPUT_DIR%"

echo Output directory: %OUTPUT_DIR%
echo.

REM Check if curl is available (Windows 10+ has curl built-in)
where curl >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: curl is not available. Please install curl or download PDFs manually.
    pause
    exit /b 1
)

echo Downloading 2025 meetings...
echo.

curl -f -s -o workshop1-15-25.pdf %BASE_URL%/2025/workshop1-15-25.pdf && echo Downloaded: workshop1-15-25.pdf || echo Failed: workshop1-15-25.pdf
curl -f -s -o workshop2-19-25.pdf %BASE_URL%/2025/workshop2-19-25.pdf && echo Downloaded: workshop2-19-25.pdf || echo Failed: workshop2-19-25.pdf
curl -f -s -o workshop3-19-25.pdf %BASE_URL%/2025/workshop3-19-25.pdf && echo Downloaded: workshop3-19-25.pdf || echo Failed: workshop3-19-25.pdf
curl -f -s -o workshop4-16-25.pdf %BASE_URL%/2025/workshop4-16-25.pdf && echo Downloaded: workshop4-16-25.pdf || echo Failed: workshop4-16-25.pdf
curl -f -s -o workshop5-21-25.pdf %BASE_URL%/2025/workshop5-21-25.pdf && echo Downloaded: workshop5-21-25.pdf || echo Failed: workshop5-21-25.pdf
curl -f -s -o workshop6-18-25.pdf %BASE_URL%/2025/workshop6-18-25.pdf && echo Downloaded: workshop6-18-25.pdf || echo Failed: workshop6-18-25.pdf
curl -f -s -o workshop7-16-25.pdf %BASE_URL%/2025/workshop7-16-25.pdf && echo Downloaded: workshop7-16-25.pdf || echo Failed: workshop7-16-25.pdf
curl -f -s -o workshop8-20-25.pdf %BASE_URL%/2025/workshop8-20-25.pdf && echo Downloaded: workshop8-20-25.pdf || echo Failed: workshop8-20-25.pdf
curl -f -s -o workshop9-17-25.pdf %BASE_URL%/2025/workshop9-17-25.pdf && echo Downloaded: workshop9-17-25.pdf || echo Failed: workshop9-17-25.pdf
curl -f -s -o workshop10-16-25.pdf %BASE_URL%/2025/workshop10-16-25.pdf && echo Downloaded: workshop10-16-25.pdf || echo Failed: workshop10-16-25.pdf
curl -f -s -o workshop11-19-25.pdf %BASE_URL%/2025/workshop11-19-25.pdf && echo Downloaded: workshop11-19-25.pdf || echo Failed: workshop11-19-25.pdf
curl -f -s -o workshop12-17-25.pdf %BASE_URL%/2025/workshop12-17-25.pdf && echo Downloaded: workshop12-17-25.pdf || echo Failed: workshop12-17-25.pdf

echo.
echo Downloading 2024 meetings...
echo.

curl -f -s -o workshop1-17-24.pdf %BASE_URL%/2024/workshop1-17-24.pdf && echo Downloaded: workshop1-17-24.pdf || echo Failed: workshop1-17-24.pdf
curl -f -s -o workshop2-21-24.pdf %BASE_URL%/2024/workshop2-21-24.pdf && echo Downloaded: workshop2-21-24.pdf || echo Failed: workshop2-21-24.pdf
curl -f -s -o workshop3-20-24.pdf %BASE_URL%/2024/workshop3-20-24.pdf && echo Downloaded: workshop3-20-24.pdf || echo Failed: workshop3-20-24.pdf
curl -f -s -o workshop4-17-24.pdf %BASE_URL%/2024/workshop4-17-24.pdf && echo Downloaded: workshop4-17-24.pdf || echo Failed: workshop4-17-24.pdf
curl -f -s -o workshop5-15-24.pdf %BASE_URL%/2024/workshop5-15-24.pdf && echo Downloaded: workshop5-15-24.pdf || echo Failed: workshop5-15-24.pdf
curl -f -s -o workshop7-17-24.pdf %BASE_URL%/2024/workshop7-17-24.pdf && echo Downloaded: workshop7-17-24.pdf || echo Failed: workshop7-17-24.pdf
curl -f -s -o workshop8-21-24.pdf %BASE_URL%/2024/workshop8-21-24.pdf && echo Downloaded: workshop8-21-24.pdf || echo Failed: workshop8-21-24.pdf
curl -f -s -o workshop9-18-24.pdf %BASE_URL%/2024/workshop9-18-24.pdf && echo Downloaded: workshop9-18-24.pdf || echo Failed: workshop9-18-24.pdf
curl -f -s -o workshop10-16-24.pdf %BASE_URL%/2024/workshop10-16-24.pdf && echo Downloaded: workshop10-16-24.pdf || echo Failed: workshop10-16-24.pdf
curl -f -s -o workshop11-20-24.pdf %BASE_URL%/2024/workshop11-20-24.pdf && echo Downloaded: workshop11-20-24.pdf || echo Failed: workshop11-20-24.pdf
curl -f -s -o workshop12-18-24.pdf %BASE_URL%/2024/workshop12-18-24.pdf && echo Downloaded: workshop12-18-24.pdf || echo Failed: workshop12-18-24.pdf

echo.
echo ========================================
echo Download complete!
echo.
echo Files downloaded to: %OUTPUT_DIR%
dir /b *.pdf 2>nul | find /c ".pdf"
echo.
echo To parse all meetings, run:
echo   python ..\voting_parser.py *.pdf --format all --output wayne_county_analysis
echo.
pause
