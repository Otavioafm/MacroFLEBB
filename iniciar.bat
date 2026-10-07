@echo off
chcp 65001 > nul
title AutoMacro Studio Pro

:: 1. Se existir o executavel compilado, abre direto (nao precisa de Python)
if exist "%~dp0AutoMacroStudio.exe" (
    start "" "%~dp0AutoMacroStudio.exe"
    exit /b
)

:: 2. Se existir ambiente virtual local
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0app_ui.py"
    goto fim
)

:: 3. Verifica se o Python esta instalado no sistema
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Iniciando via Python do sistema...
    python "%~dp0app_ui.py"
    if %errorlevel% neq 0 (
        echo.
        echo [AVISO] Houve uma falha ao iniciar. Instalando dependencias necessarias...
        pip install -r "%~dp0requirements.txt"
        echo [INFO] Tentando abrir novamente...
        python "%~dp0app_ui.py"
    )
    goto fim
)

echo.
echo =======================================================================
echo [ERRO] Python ou AutoMacroStudio.exe nao foram encontrados!
echo.
echo Para executar pelo codigo-fonte:
echo 1. Instale o Python 3.10 ou superior pelo site https://www.python.org/
echo 2. Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao.
echo =======================================================================
echo.
pause

:fim
