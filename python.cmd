@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "WRAPPER=%~f0"
set "ROOT=%~dp0"

call :resolve_python
if errorlevel 1 exit /b %ERRORLEVEL%

set "PREV_SKIP=%ALEXANDRIA_GUARD_SKIP%"
if not "%ALEXANDRIA_GUARD_SKIP%"=="1" if /I not "%ALEXANDRIA_GUARD_MODE%"=="developer" (
    call :run_guard
    set "guard_rc=%ERRORLEVEL%"
    if not "%guard_rc%"=="0" exit /b %guard_rc%
)

set "ALEXANDRIA_GUARD_SKIP=1"
if /I "%REAL_PYTHON%"=="py" (
    py %*
    set "RC=%ERRORLEVEL%"
) else (
    "%REAL_PYTHON%" %*
    set "RC=%ERRORLEVEL%"
)

if defined PREV_SKIP (
    set "ALEXANDRIA_GUARD_SKIP=%PREV_SKIP%"
) else (
    set ALEXANDRIA_GUARD_SKIP=
)

endlocal & exit /b %RC%

:resolve_python
if defined REAL_PYTHON exit /b 0

if defined ALEXANDRIA_PYTHON_PATH (
    set "REAL_PYTHON=%ALEXANDRIA_PYTHON_PATH%"
    goto :resolve_done
)

for /f "usebackq delims=" %%P in (`where py 2^>nul`) do (
    set "REAL_PYTHON=py"
    goto :resolve_done
)

for /f "usebackq delims=" %%P in (`where python 2^>nul`) do (
    set "CANDIDATE=%%~fP"
    if /I not "!CANDIDATE!"=="%WRAPPER%" (
        set "REAL_PYTHON=!CANDIDATE!"
        goto :resolve_done
    )
)

echo [guard] Unable to locate Python interpreter. >&2
exit /b 1

:resolve_done
if not defined REAL_PYTHON (
    echo [guard] Unable to locate Python interpreter. >&2
    exit /b 1
)
exit /b 0

:run_guard
if /I "%REAL_PYTHON%"=="py" (
    py "%ROOT%scripts\guard\verify_progress.py"
) else (
    "%REAL_PYTHON%" "%ROOT%scripts\guard\verify_progress.py"
)
exit /b %ERRORLEVEL%
