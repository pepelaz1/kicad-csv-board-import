@echo off
setlocal
cd /d "%~dp0"
set "KICAD_CONFIG_HOME=%CD%\tools\kicad-config"
set "KICAD_DOCUMENTS_HOME=%CD%\tools\kicad-documents"
if not defined KICAD_BIN set "KICAD_BIN=%CD%\tools\kicad-10.0.8\bin"
if not exist "%KICAD_BIN%\python.exe" set "KICAD_BIN=%ProgramFiles%\KiCad\10.0\bin"

if not exist "%KICAD_BIN%\python.exe" (
  echo KiCad 10.0.8 was not found. Install KiCad or set KICAD_BIN to its bin folder.
  exit /b 1
)

"%KICAD_BIN%\python.exe" import_board.py sample.csv output\demo.kicad_pcb || exit /b 1
"%KICAD_BIN%\kicad-cli.exe" pcb export gerbers --layers F.Cu,B.Cu --output output\gerbers\ output\demo.kicad_pcb || exit /b 1
"%KICAD_BIN%\kicad-cli.exe" pcb export drill --output output\drill\ output\demo.kicad_pcb || exit /b 1
echo Done. Board: output\demo.kicad_pcb
echo Gerbers: output\gerbers
echo Drill: output\drill
