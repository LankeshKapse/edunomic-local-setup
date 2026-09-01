@echo off
echo Stopping all Edunomic services by port...

REM List of ports used by your services
set PORTS=8080 8083 8084 8085 8086 8087 8088 8089 8090 8091 8092 8093 8094

for %%P in (%PORTS%) do (
    echo Checking for service on port %%P...
    for /f "tokens=5" %%A in ('netstat -ano ^| findstr :%%P') do (
        echo Terminating PID %%A running on port %%P
        taskkill /PID %%A /F
    )
)

echo All listed ports have been terminated.
pause
