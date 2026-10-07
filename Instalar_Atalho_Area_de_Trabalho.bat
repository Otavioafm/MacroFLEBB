@echo off
chcp 65001 > nul
title Instalador do AutoMacro Studio Pro
color 0A

echo ========================================================
echo        INSTALADOR - AUTOMACRO STUDIO PRO
echo ========================================================
echo.
echo Criando atalho na sua Área de Trabalho...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$desktop = [Environment]::GetFolderPath('Desktop'); $wsh = New-Object -ComObject WScript.Shell; $sc = $wsh.CreateShortcut(\"$desktop\AutoMacro Studio Pro.lnk\"); $sc.TargetPath = '%~dp0AutoMacroStudio.exe'; $sc.WorkingDirectory = '%~dp0'; $sc.Description = 'Gravador e Repetidor de Teclado e Mouse Profissional'; $sc.Save()"

if %errorlevel% equ 0 (
    echo [SUCESSO] Atalho criado com sucesso na sua Área de Trabalho!
    echo.
    echo Você já pode abrir o 'AutoMacro Studio Pro' diretamente
    echo pelo ícone na sua Área de Trabalho ou executando AutoMacroStudio.exe!
) else (
    echo [AVISO] Houve uma falha ao criar o atalho automático.
    echo Mas você pode executar o programa diretamente pelo arquivo AutoMacroStudio.exe nesta pasta.
)

echo.
echo ========================================================
pause
