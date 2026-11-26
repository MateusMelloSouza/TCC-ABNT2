@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM ============================================================================
REM  build.bat - compile the whole LaTeX document (Windows, TeX Live or MiKTeX).
REM  Put this file next to main.tex and double-click it (or run: build.bat other-main).
REM
REM  WHY IT EXISTS
REM  One LaTeX run is never enough. A thesis or paper needs:
REM     latex                -> collects labels and citations (.aux, .toc, .bcf)
REM     biber or bibtex      -> builds the bibliography (.bbl)
REM     makeglossaries       -> builds lists of abbreviations, if \makeglossaries is used
REM     latex x2             -> fills in numbers, citations and lists
REM  Without the bibliography step every citation prints [?] or the key in bold and
REM  the References section is missing. The PDF looks broken, but the text is fine.
REM
REM  latexmk does all of this automatically. On MiKTeX, latexmk needs Perl
REM  (e.g. Strawberry Perl); without it this script falls back to manual passes.
REM ============================================================================

set MAIN=main
if not "%~1"=="" set MAIN=%~1
cd /d "%~dp0"
if not exist "%MAIN%.tex" (
    echo   [ERROR] %MAIN%.tex not found in this folder. Usage: build.bat [main-file-without-.tex]
    goto end
)

REM -- engine: magic comment, else fontspec/unicode-math => LuaLaTeX, else pdfLaTeX
set ENGINE=pdflatex
findstr /i /r /c:"^%% *!TEX *program *= *lualatex" "%MAIN%.tex" >nul 2>&1 && set ENGINE=lualatex
findstr /i /r /c:"^%% *!TEX *program *= *xelatex" "%MAIN%.tex" >nul 2>&1 && set ENGINE=xelatex
if "!ENGINE!"=="pdflatex" (
    findstr /s /m /c:"{fontspec}" /c:"{unicode-math}" /c:"{polyglossia}" *.tex >nul 2>&1 && set ENGINE=lualatex
)
set LMKENG=-pdf
if "!ENGINE!"=="lualatex" set LMKENG=-lualatex
if "!ENGINE!"=="xelatex" set LMKENG=-xelatex

echo.
echo  Building %MAIN%.tex with !ENGINE!. Long documents take a few minutes; keep this window open.
echo.

where latexmk >nul 2>&1
if %errorlevel%==0 (
    latexmk -v >nul 2>&1
    if !errorlevel!==0 goto use_latexmk
    echo  [latexmk is installed but does not run - on MiKTeX install Perl. Using manual passes.]
)

REM ---------------------------------------------------------------- manual passes
echo  == 1/4  !ENGINE! ==
!ENGINE! -synctex=1 -interaction=nonstopmode -file-line-error "%MAIN%.tex" >nul
if exist "%MAIN%.bcf" (
    echo  == 2/4  biber ^(biblatex^) ==
    biber "%MAIN%"
) else (
    findstr /c:"\bibdata" "%MAIN%.aux" >nul 2>&1 && (echo  == 2/4  bibtex ==& bibtex "%MAIN%") || echo  == 2/4  no bibliography ==
)
if exist "%MAIN%.glo" ( echo  == 2b   makeglossaries ==& makeglossaries "%MAIN%" ) else if exist "%MAIN%.acn" ( echo  == 2b   makeglossaries ==& makeglossaries "%MAIN%" )
echo  == 3/4  !ENGINE! ==
!ENGINE! -synctex=1 -interaction=nonstopmode -file-line-error "%MAIN%.tex" >nul
echo  == 4/4  !ENGINE! ==
!ENGINE! -synctex=1 -interaction=nonstopmode -file-line-error "%MAIN%.tex" >nul
goto verify

:use_latexmk
if exist ".latexmkrc" (
    echo  == latexmk ^(settings from .latexmkrc^) ==
    latexmk -synctex=1 -interaction=nonstopmode -file-line-error "%MAIN%.tex"
) else (
    findstr /s /m /c:"\makeglossaries" *.tex >nul 2>&1 && (
        echo  [WARNING] \makeglossaries is used but there is no .latexmkrc: the abbreviation list may be empty.
        echo            Copy the skill's assets\latexmkrc here as ".latexmkrc".
    )
    echo  == latexmk !LMKENG! ==
    latexmk !LMKENG! -synctex=1 -interaction=nonstopmode -file-line-error "%MAIN%.tex"
)

:verify
echo.
echo  ============================== CHECKS ==============================
if not exist "%MAIN%.pdf" (
    echo   [ERROR] %MAIN%.pdf was not produced. Open %MAIN%.log and look for lines starting with "!".
    goto end
)
if exist "%MAIN%.bbl" (
    echo   [ok] bibliography built ^(%MAIN%.bbl^).
) else (
    echo   [i]  no %MAIN%.bbl - fine only if the document has no bibliography.
)
findstr /c:"There were undefined references" /c:"There were undefined citations" "%MAIN%.log" >nul 2>&1
if %errorlevel%==0 (
    echo   [WARNING] undefined references or citations remain - run this file again;
    echo             if they persist, search the log for "undefined" ^(wrong key or label^).
) else (
    echo   [ok] no undefined references or citations.
)
for /f %%i in ('findstr /r /c:"^!" "%MAIN%.log" ^| find /c /v ""') do set NERR=%%i
echo   [i]  !NERR! LaTeX error line^(s^) in %MAIN%.log.
for /f %%i in ('findstr /c:"Overfull \hbox" "%MAIN%.log" ^| find /c /v ""') do set NOVER=%%i
echo   [i]  !NOVER! overfull box^(es^) ^(text or tables running into the margin^).
echo   ---------------------------------------------------------------
findstr /c:"Output written on" "%MAIN%.log"
echo   ---------------------------------------------------------------

:end
echo.
pause
