# Changelog

## Não lançado

- **Layout corrigido:** o conteúdo saiu da subpasta `TCC-ABNT2/` para a raiz do
  repositório. Antes, `/plugin marketplace add` não achava o `.claude-plugin/` e o
  GitHub não executava o CI.
- `.gitattributes` com LF em tudo (CRLF só no `.bat`). O `dist/tcc-abnt.zip` deixa de
  ser versionado: o CI o gera e a release o anexa (o link do README aponta para a
  última release).
- `compile-check.sh` agora sai com código 3 quando restam erros, citações ou
  referências indefinidas. `--lenient` mantém o comportamento antigo. O PDF velho é
  apagado antes do build, e o script passa a funcionar no bash 3.2 (macOS).
- O CI falha com citações ou referências indefinidas e testa um caso negativo.
- `check.py`: a lista de dados pessoais agora detecta caminhos reais de perfil do Windows e
  varre o repositório inteiro.

## 2.0.0 — 2026-09-15

Primeira versão pública. Reescrita do skill pessoal `tcc-abnt` (v1, jun. 2026) para
uso por qualquer estudante, com qualquer template abnTeX2.

- **Normas atualizadas** para as edições vigentes: NBR 14724:2024, NBR 10520:2023,
  NBR 6023:2018 (+Errata 2:2020), NBR 6028:2021 — com tabela do que mudou e do que o
  abnTeX2 1.9.7 ainda produz (`references/normas-e-versoes.md`).
- **Correções testadas** sem editar o `.bst`: citações `(Autor, ano)` da NBR
  10520:2023 via `@ABNT-options` + `\citeoption`; URLs sem `< >` via
  `\def\UrlLeft{}\def\UrlRight{}`.
- **Perfil UniforTeX2 (UNIFOR)** completo: todas as macros do `main.tex`, comandos de
  conteúdo, cadeia de compilação com `makeglossaries`, uma dúzia de armadilhas com
  correção sancionada em `main.tex` (o `.sty` nunca é editado) — incluindo a causa
  real do "erro benigno" `Missing \begin{document}` (setters com `\ifthenelse` sem o
  ramo *else*, que engolem o comando seguinte e imprimem `nao` na capa; correção:
  `{}` após cada um) e a opção fantasma `tccgraduacaoPDF`.
- **Perfil do modelo canônico abnTeX2** e procedimento para perfilar qualquer outro
  template (`references/templates/`).
- **Scripts** independentes de plataforma: `setup-sandbox-latex.sh` (instala abnTeX2,
  babel-portuges, Latin Modern e extras a partir do CTAN em `$TEXMFHOME`),
  `compile-check.sh` (build + triagem filtrada do log), `audit-tex.py` (placeholders,
  citações × `.bib`, rótulos, floats sem fonte/chamada, siglas não usadas,
  resumo/abstract, contagem de palavras, triagem do log), `init-workflow.py`
  (scaffold de `.tcc-workflow/`), `compilar.bat` para Windows.
- **Workflow de sessões** revisado com as lições de 36 sessões reais: invariantes
  medidos no log, reconciliação de trackers, escrita atômica de arquivos, verificação
  adversarial de achados de revisores.
- **Checklist de auditoria pré-depósito** e padrão de revisão multiagente
  (`references/revisao-final.md`).
- Lições de `.bib` verificadas no `abntex2-alf.bst`: sobrenomes compostos com
  `{\relax ...}`, partículas (`de Freitas`), acentos como escapes TeX em campos de
  autor, autores-entidade, forma documentada de anais e legislação; e de floats
  (fila bloqueada, `Float too large`).
- Empacotamento como plugin do Claude Code (marketplace neste repositório) e ZIP para
  upload no claude.ai; CI com validação e release automática.
