@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM ============================================================================
REM  compilar.bat — compila o trabalho inteiro (abnTeX2 + BibTeX + glossaries).
REM  Coloque este arquivo na raiz do projeto (ao lado do main.tex) e dê dois cliques.
REM
REM  POR QUE ELE EXISTE
REM  Uma passagem de pdflatex NAO basta. O documento precisa de:
REM     pdflatex        -> descobre rotulos, escreve .aux .toc .lof .acn
REM     bibtex          -> le o .aux e gera o main.bbl (AS REFERENCIAS)
REM     makeglossaries  -> gera o main.acr (A LISTA DE SIGLAS), se o modelo usar glossaries
REM     pdflatex x2     -> preenche numeros, citacoes e as listas
REM
REM  Sem o bibtex, o capitulo de Referencias sai VAZIO e toda citacao vira (????).
REM  Sem o makeglossaries, a lista de siglas sai VAZIA. O PDF encolhe e parece
REM  quebrado -- mas o defeito e a compilacao, nao o texto.
REM
REM  Requisitos: MiKTeX ou TeX Live instalados (pdflatex no PATH). latexmk e opcional.
REM ============================================================================

set MAIN=main
if not "%~1"=="" set MAIN=%~1
cd /d "%~dp0"

if not exist "%MAIN%.tex" (
    echo   [ERRO] %MAIN%.tex nao encontrado nesta pasta. Uso: compilar.bat [nome-sem-extensao]
    goto fim
)

echo.
echo  Compilando %MAIN%.tex. Documentos longos com muitas figuras levam alguns minutos.
echo  Nao feche esta janela.
echo.

REM -- o modelo usa glossaries? (lista de siglas / glossario) --------------------
set USAGLOSS=0
findstr /s /m /c:"\makeglossaries" *.tex lib\*.tex >nul 2>&1 && set USAGLOSS=1

where latexmk >nul 2>&1
if %errorlevel%==0 goto usar_latexmk

REM ---------------------------------------------------------------- fallback
echo  [latexmk nao encontrado -- usando as passagens manuais]
echo.
echo  == 1/5  pdflatex ==
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %MAIN%.tex >nul
echo  == 2/5  bibtex (referencias) ==
bibtex %MAIN%
if "!USAGLOSS!"=="1" (
    echo  == 3/5  makeglossaries (siglas) ==
    makeglossaries %MAIN%
) else (
    echo  == 3/5  makeglossaries: nao necessario neste modelo ==
)
echo  == 4/5  pdflatex ==
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %MAIN%.tex >nul
echo  == 5/5  pdflatex ==
pdflatex -synctex=1 -interaction=nonstopmode -file-line-error %MAIN%.tex >nul
goto verificar

:usar_latexmk
echo  == latexmk: roda todas as passagens na ordem certa ==
if "!USAGLOSS!"=="1" if not exist ".latexmkrc" if not exist "latexmkrc" (
    echo  [AVISO] o modelo usa glossaries mas nao ha .latexmkrc: a lista de siglas pode sair vazia.
    echo          Copie o latexmkrc do skill tcc-abnt para a raiz do projeto como ".latexmkrc".
)
latexmk -pdf -synctex=1 -interaction=nonstopmode -file-line-error %MAIN%.tex

:verificar
echo.
echo  ============================ VERIFICACAO ============================

if not exist "%MAIN%.pdf" (
    echo   [ERRO] %MAIN%.pdf nao foi gerado. Veja %MAIN%.log ^(procure linhas comecando com "!"^).
    goto fim
)

if not exist "%MAIN%.bbl" (
    echo   [FALHA] %MAIN%.bbl ausente -- o bibtex nao rodou.
    echo           As Referencias vao sair VAZIAS e as citacoes como ^(????^).
) else (
    for /f %%i in ('findstr /c:"\bibitem" %MAIN%.bbl ^| find /c /v ""') do set NREF=%%i
    echo   [ok] %MAIN%.bbl presente -- !NREF! referencias resolvidas.
)

if "!USAGLOSS!"=="1" (
    if not exist "%MAIN%.acr" (
        echo   [FALHA] %MAIN%.acr ausente -- o makeglossaries nao rodou. A lista de siglas vai sair VAZIA.
    ) else (
        echo   [ok] %MAIN%.acr presente -- lista de siglas gerada.
    )
)

findstr /c:"There were undefined references" %MAIN%.log >nul 2>&1
if %errorlevel%==0 (
    echo   [ATENCAO] ainda ha referencias/citacoes indefinidas -- rode este arquivo de novo;
    echo             se persistir, procure "undefined" no %MAIN%.log ^(chave ou rotulo errado^).
) else (
    echo   [ok] nenhuma referencia indefinida.
)

for /f %%i in ('findstr /r /c:"^!" %MAIN%.log ^| find /c /v ""') do set NERR=%%i
echo   [i]  !NERR! linha^(s^) de erro LaTeX no log ^(avisos benignos do modelo contam aqui^).

for /f %%i in ('findstr /c:"Overfull \hbox" %MAIN%.log ^| find /c /v ""') do set NOVER=%%i
echo   [i]  !NOVER! caixas overfull ^(texto/tabela invadindo a margem^).

REM -- invariante: toda figura/tabela tem legenda E fonte (\Caption/\caption vs \Fonte/\fonte/\legend)
set /a NCAP=0
set /a NFON=0
for /f %%i in ('findstr /s /r /c:"\\[Cc]aption{" *.tex ^| find /c /v ""') do set /a NCAP=%%i
for /f %%i in ('findstr /s /r /c:"\\[Ff]onte{" /c:"\\legend{" *.tex ^| find /c /v ""') do set /a NFON=%%i
if "!NCAP!"=="!NFON!" (
    echo   [ok] floats equilibrados -- !NCAP! legendas = !NFON! fontes.
) else (
    echo   [ATENCAO] !NCAP! legendas contra !NFON! fontes -- alguma figura/tabela pode estar sem Fonte.
)

echo   ---------------------------------------------------------------
findstr /c:"Output written on" %MAIN%.log
echo   ---------------------------------------------------------------

:fim
echo.
pause
