@echo off
REM ====================================================
REM Clinical Trial Protocol Generator - Start Services
REM ====================================================

echo.
echo ========================================
echo Clinical Trial Protocol Generator
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please create virtual environment first:
    echo    python -m venv .venv
    echo    .venv\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo Please edit .env and add your OPENAI_API_KEY if you want LLM features.
    echo.
)

echo Starting services...
echo.

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
echo.
echo [2/4] Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo FastAPI not found. Installing dependencies...
    echo This may take a few minutes...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please run manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
) else (
    echo Dependencies already installed.
)

REM Check if ChromaDB is initialized
if not exist "vector_db" (
    echo.
    echo [3/4] ChromaDB not initialized. Seeding RAG database...
    echo This may take a few minutes...
    python examples/seed_rag_direct.py
    if errorlevel 1 (
        echo.
        echo WARNING: RAG seeding failed. Continuing anyway...
        echo You can seed the database later with: python examples/seed_rag_direct.py
        echo.
    ) else (
        echo.
        echo RAG database seeded successfully!
        echo.
    )
) else (
    echo [3/4] RAG database already initialized (vector_db folder exists)
    echo.
)

REM Start FastAPI server
echo [4/4] Starting FastAPI server...
echo.
echo ========================================
echo Server will start on: http://localhost:8000
echo Web UI available at: http://localhost:8000/
echo API Docs available at: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

REM Keep window open if server exits with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Server stopped with errors!
    echo ========================================
    echo.
    pause
)
