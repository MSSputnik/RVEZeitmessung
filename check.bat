@echo off
REM Local check script: run ruff lint, ruff format check, ty, then pytest,
REM one after another. Stops at the first failing step so files can be
REM lint/format/type/test checked without a pre-commit hook. Each step prints
REM which check is starting.

echo.
echo ============================================================
echo [1/4] ruff check
echo ============================================================
uv run ruff check .
if errorlevel 1 (
    echo.
    echo ruff check failed. Stopping.
    exit /b 1
)

echo.
echo ============================================================
echo [2/4] ruff format --check
echo ============================================================
uv run ruff format --check .
if errorlevel 1 (
    echo.
    echo ruff format check failed ^(run "uv run ruff format ." to fix^). Stopping.
    exit /b 1
)

echo.
echo ============================================================
echo [3/4] ty check
echo ============================================================
uv run ty check .
if errorlevel 1 (
    echo.
    echo ty check failed. Stopping.
    exit /b 1
)

echo.
echo ============================================================
echo [4/4] pytest
echo ============================================================
uv run python -m pytest
set "PYTEST_RC=%errorlevel%"
REM Exit code 5 means "no tests collected" - treat that as OK, not a failure.
if %PYTEST_RC% equ 5 (
    echo No tests collected ^(exit 5^) - treating as pass.
) else if %PYTEST_RC% neq 0 (
    echo.
    echo pytest failed. Stopping.
    exit /b 1
)

echo.
echo All checks passed.
exit /b 0
