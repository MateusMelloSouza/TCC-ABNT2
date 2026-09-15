# TCC-ABNT2 — skill do Claude para TCC, dissertação e tese em LaTeX (abnTeX2 + ABNT)

Um *skill* para o Claude (claude.ai, app desktop/Cowork e Claude Code) que faz dele um
coautor e diagramador competente de trabalhos acadêmicos brasileiros **escritos em
LaTeX com a classe abnTeX2**: TCC, monografia, dissertação, tese, artigo científico e
projeto de pesquisa. Ele conhece as normas ABNT nas edições vigentes, sabe o que o
abnTeX2 ainda faz do jeito antigo e como corrigir, respeita o template da sua
universidade (perfil completo do **UniforTeX2/UNIFOR** incluído) e traz um fluxo de
sessões de escrita para chegar ao depósito com o PDF compilando e sem dívidas
escondidas.

Nasceu do skill pessoal usado em 36 sessões de escrita e auditoria de um TCC de
Engenharia de Computação na UNIFOR; a versão pública remove tudo o que era específico
daquele trabalho e incorpora o que as sessões ensinaram.

> Foco deliberado em **LaTeX**. Se o seu trabalho está em Word, este skill não é para
> ele — mas as referências de norma (`references/*.md`) ainda servem de consulta.

## O que ele faz

- **Escreve e revisa** em português acadêmico formal: resumo/abstract (NBR 6028:2021),
  introdução com objetivos, fundamentação, metodologia, resultados, conclusão — sem
  inventar fontes nem resultados (lacunas viram `% TODO` visíveis).
- **Cita e referencia** (NBR 10520:2023, NBR 6023:2018): comandos do `abntex2cite` e do
  `biblatex-abnt`, entradas `.bib` corretas (sobrenomes compostos, autores-entidade,
  anais, legislação), lista de referências sem órfãos.
- **Formata** (NBR 14724:2024, 6024, 6027): estrutura e ordem dos elementos, figuras e
  tabelas com fonte e chamada no texto, **tabela × quadro**, listas de siglas e
  símbolos, equações, alíneas — sempre pelos comandos do template, nunca "na mão".
- **Compila e diagnostica** em qualquer lugar: Overleaf, VS Code + LaTeX Workshop,
  TeXstudio/MiKTeX, linha de comando, Windows (`compilar.bat`) e sandboxes sem abnTeX2
  (scripts que instalam o que falta a partir do CTAN). Tabela de erros: `(????)`,
  `??`, lista de siglas vazia, `File 'lib/xxx.sty' not found`, `Float too large`…
- **Sessões de escrita** repetíveis (5 fases) com estado no projeto
  (`.tcc-workflow/STATUS.md`, `TODO.md`, logs de sessão) e **auditoria pré-depósito**
  (checklist ABNT + padrão de revisão multiagente com verificação adversarial).

## Normas cobertas — e o que o abnTeX2 ainda faz diferente

| Norma | Edição vigente | Mudança que importa | abnTeX2 1.9.7 (2018) | Correção testada |
|---|---|---|---|---|
| NBR 10520 (citações) | **2023** | `(Silva, 2020)` — só a inicial maiúscula; *et al.* opcional a partir de 4 autores; latinismos em itálico | imprime `(SILVA, 2020)` | entrada `@ABNT-options` + `\citeoption` — 2 linhas, sem editar o `.bst` |
| NBR 6023 (referências) | **2018** + Errata 2 (2020) | `Disponível em: URL.` sem `< >`; `[S. l.]` | imprime `<URL>` | `\def\UrlLeft{}\def\UrlRight{}` |
| NBR 6028 (resumo) | **2021** | palavras-chave separadas por **ponto e vírgula** | imprime o que você digitar | — |
| NBR 14724 (estrutura) | **2024** | fontes de figuras conforme 10520:2023; "seções", não "capítulos"; anexos com referências próprias | implementa 2011 | — |
| NBR 6024 / 6027 / 6022 / 15287 | 2012 / 2012 / 2018 / 2011 | — | ok | — |

A regra de decisão do skill: **o manual da sua biblioteca e o seu orientador mandam**.
Ele explica a diferença uma vez, recomenda perguntar à biblioteca e registra a decisão
no `STATUS.md`. Detalhes em
[`skills/tcc-abnt/references/normas-e-versoes.md`](skills/tcc-abnt/references/normas-e-versoes.md).

## Instalação

### Claude.ai e app desktop (Cowork)

1. Baixe [`dist/tcc-abnt.zip`](https://github.com/MateusMelloSouza/TCC-ABNT2/raw/main/dist/tcc-abnt.zip)
   (a pasta `tcc-abnt/` é a raiz do ZIP, como o claude.ai exige).
2. No claude.ai: **Customize → Skills → "+" → Create skill → Upload a skill** e envie o ZIP.
   O skill aparece na lista e pode ser ligado/desligado; skills da conta também ficam
   disponíveis no app desktop (Cowork).
3. Peça algo como *"Comece uma sessão de escrita do meu TCC"* com a pasta do projeto
   conectada (Cowork) ou os arquivos anexados.

### Claude Code

Como plugin (recomendado — atualizações pelo menu `/plugin`):

```
/plugin marketplace add MateusMelloSouza/TCC-ABNT2
/plugin install tcc-abnt2@tcc-abnt2
```

Ou como skill pessoal/de projeto (cópia da pasta):

```bash
git clone https://github.com/MateusMelloSouza/TCC-ABNT2.git
cp -r TCC-ABNT2/skills/tcc-abnt ~/.claude/skills/        # todos os projetos
# ou, dentro do projeto do TCC:  cp -r TCC-ABNT2/skills/tcc-abnt .claude/skills/
```

## Como usar

Fale normalmente; o skill dispara quando percebe TCC/ABNT/abnTeX2. Pedidos típicos:

- *"Comece uma sessão de escrita do meu TCC"* → lê `.tcc-workflow/STATUS.md`, mede de novo o
  projeto (`audit-tex.py`, `compile-check.sh`), reconcilia as dívidas e pergunta o alvo
  da sessão. Sem `.tcc-workflow/`, ele cria com `scripts/init-workflow.py`.
- *"Escreva a seção de Trabalhos Relacionados com estes três artigos"* → pede o que
  falta, propõe o plano, escreve nos arquivos do capítulo com os comandos do template.
- *"Minhas citações saem como (????)"* / *"a lista de siglas está vazia"* → diagnóstico
  pela tabela de erros (faltou `bibtex`/`makeglossaries`, chave errada, root file errado…).
- *"Converta as citações para a NBR 10520:2023"* → aplica a correção de duas linhas e
  recompila.
- *"Essa tabela deveria ser um quadro?"* → classifica (dados numéricos × conteúdo
  textual), converte com o comando do template e ajusta as listas.
- *"Faça a auditoria ABNT antes do depósito"* → checklist de
  [`revisao-final.md`](skills/tcc-abnt/references/revisao-final.md), com scripts primeiro
  e olhos depois; achados verificados contra o `.tex` e o `main.log` antes de editar.

### Para quem usa o UniforTeX2 (UNIFOR)

O skill reconhece o template (`lib/unifortex2.sty`, `\trabalhoacademico`,
`\UNIFORfig`) e carrega o perfil
[`references/templates/unifortex2.md`](skills/tcc-abnt/references/templates/unifortex2.md):
todas as macros do `main.tex` (tipo de trabalho, IES, curso, orientador, banca, datas),
os blocos de figura/tabela/quadro/algoritmo, a lista de siglas via `glossaries`
(exige `makeglossaries`), e uma dúzia de armadilhas conhecidas com a correção
sancionada em `main.tex` — o `unifortex2.sty` **nunca** é editado, para o projeto
continuar compilando no Overleaf. Entre elas: o erro `Missing \begin{document}` que
todo mundo chama de "benigno" e que na verdade imprime a palavra `nao` na capa (os
comandos `\removerbordasdohyperlink`, `\cordohyperlink`, `\ehqualificacao` e
`\orientadorfeminino` do template engolem o comando seguinte; a correção é um `{}`
depois de cada um), o `\glossarystyle` removido pelo `glossaries` ≥ 4.50, o marcador
de PDF dos apêndices, a opção `tccgraduacaoPDF` que na verdade seleciona
`dissertacao`, e o `\glsaddall` que imprime siglas não usadas. O template está na
galeria do Overleaf ("UNIFOR - Template Latex", Bruno Lopes) — é um projeto
extraoficial, e este repositório não o redistribui.

### Para outras universidades

Cada instituição tem seu fork do abnTeX2. Na primeira sessão o skill **perfila o
template** ([procedimento](skills/tcc-abnt/references/templates/README.md)) e grava o
resultado em `.tcc-workflow/TEMPLATE.md`; nas seguintes, aplica as normas *através* do
template. Perfis verificados são bem-vindos como contribuição (veja
[CONTRIBUTING.md](CONTRIBUTING.md)).

## Scripts (funcionam sem o Claude também)

| Script | O que faz |
|---|---|
| `skills/tcc-abnt/scripts/setup-sandbox-latex.sh` | Instala abnTeX2, babel-portuges, Latin Modern e pacotes extras a partir do CTAN em `~/texmf`, sem root — para sandboxes/CI com TeX Live enxuto. |
| `skills/tcc-abnt/scripts/compile-check.sh [main.tex]` | `latexmk` completo (com `makeglossaries` quando preciso) + resumo: páginas, citações/referências indefinidas, erros reais (avisos benignos filtrados), overfull, placeholders. |
| `skills/tcc-abnt/scripts/audit-tex.py [pasta]` | Mede o projeto de novo: placeholders, `\cite` × `.bib` (faltantes, órfãs, duplicadas), rótulos, floats sem fonte/chamada, siglas não usadas, resumo/abstract (palavras, separador), contagem de palavras, triagem do log. Só biblioteca-padrão; Windows ok. |
| `skills/tcc-abnt/scripts/init-workflow.py [pasta] [--build-helpers]` | Cria `.tcc-workflow/` (STATUS, TODO, TEMPLATE, log de sessão, cópias das ferramentas) e, opcionalmente, `.latexmkrc`, `.gitignore`, `compilar.bat` e `.vscode/settings.json`. |
| `skills/tcc-abnt/assets/compilar.bat` | Windows: dois cliques compilam tudo na ordem certa e verificam `.bbl`, `.acr`, referências indefinidas e legendas × fontes. |

## Estrutura do repositório

```
skills/tcc-abnt/
├── SKILL.md                      # instruções principais (o que o Claude lê primeiro)
├── references/
│   ├── normas-e-versoes.md       # edições vigentes × abnTeX2, correções testadas
│   ├── estrutura-nbr14724.md     # elementos e ordem, comandos abnTeX2
│   ├── citacoes-nbr10520.md      # citações (2023) e comandos abntex2cite/biblatex
│   ├── referencias-nbr6023.md    # referências e higiene do .bib
│   ├── formatacao.md             # página, seções, figuras, tabela × quadro, listas
│   ├── escrita-academica.md      # registro, resumo, seções, armadilhas
│   ├── workflow-sessao.md        # as 5 fases da sessão de escrita
│   ├── compilacao-e-erros.md     # compilar em qualquer lugar; tabela de erros
│   ├── revisao-final.md          # auditoria pré-depósito; revisão multiagente
│   └── templates/                # perfis: unifortex2.md, abntex2-modelo.md, README.md
├── scripts/                      # setup-sandbox-latex.sh, compile-check.sh, audit-tex.py, init-workflow.py
└── assets/                       # modelos de STATUS/TODO/log, latexmkrc, gitignore, vscode, compilar.bat
.claude-plugin/                   # plugin.json + marketplace.json (Claude Code)
dist/tcc-abnt.zip                 # pacote para upload no claude.ai
```

## Fontes consultadas

Edições e mudanças das normas: [UFMG — principais mudanças da NBR 14724:2024](https://sites.arq.ufmg.br/biblioteca/wp-content/uploads/2025/03/NBR-14724-2024_principais-mudan%C3%A7as-1.pdf),
[PUCPR — NBR 14724 atualizada](https://www.pucpr.br/noticias/abnt-nbr-14-724-atualizada-descubra-o-que-mudou/),
[UFV — normalização 2025](https://www.bbt.ufv.br/wp-content/uploads/2025/02/Normalizacao-de-trabalhos-academicos-2025-UFV.pdf),
[UFPA — NBR 10520:2023](https://bc.ufpa.br/atualizacao-da-norma-de-citacoes-da-abnt-nbr-10520/),
[Mundo Bibliotecário — 7 atualizações da NBR 10520:2023](https://mundobibliotecario.com.br/index.php/2023/07/25/a-caixa-alta-morreu-conheca-essa-e-mais-6-outras-atualizacoes-da-norma-abnt-nbr-105202023-que-vao-te-surpreender/),
[Seu Melhor TCC — NBR 10520:2023](https://seumelhortcc.com/norma-de-citacoes-2023-atualizacao-abnt-nbr-10520/),
[Biblioteca Unifor — NBR 6028:2021](https://unifor.br/web/bibliotecaunifor/confira-a-atualizacao-da-norma-de-resumo-abnt-nbr-6028-2021),
[UNESP — NBR 6028:2021](https://www.foa.unesp.br/Home/instituicao/biblioteca108/informativo-gnt---nbr-6028-2021_final.pdf).
abnTeX2: [CTAN](https://ctan.org/pkg/abntex2), [GitHub](https://github.com/abntex/abntex2),
issues [#233](https://github.com/abntex/abntex2/issues/233) e [#264](https://github.com/abntex/abntex2/issues/264) (URL com `< >`),
[lista abntex2 — NBR 10520:2023](https://groups.google.com/g/abntex2/c/yQ-AgdE9338);
[biblatex-abnt #123](https://github.com/abntex/biblatex-abnt/issues/123).
UniforTeX2: [Overleaf — UNIFOR Template Latex](https://www.overleaf.com/latex/templates/unifor-template-latex/znrhfnkcwycq);
alternativa [unifor-abnTeX2](https://www.overleaf.com/latex/templates/unifor-abntex2/hmjpngwqqmmf).
As correções para o `abntex2cite` foram testadas no modelo canônico e num projeto
UniforTeX2 (TeX Live 2023).

## Licença e créditos

MIT (veja [LICENSE](LICENSE)). abnTeX2 é da equipe abnTeX2 (LPPL); UniforTeX2 é de
Bruno Lopes (LPPL/CC BY 4.0) — nenhum dos dois é redistribuído aqui. As normas ABNT
são documentos pagos: este skill descreve o que elas exigem na prática, não as
reproduz.

---

## English summary

**TCC-ABNT2** is a Claude skill (claude.ai, desktop/Cowork, Claude Code) for
Brazilian academic documents written in **LaTeX with abnTeX2** — TCC, monografia,
dissertação, tese, article, research project. It knows the current ABNT editions
(NBR 14724:2024, 10520:2023, 6023:2018, 6028:2021), what abnTeX2 1.9.7 still does the
old way and the tested two-line fixes, respects institutional templates (full
**UniforTeX2/UNIFOR** profile, plus a procedure to profile any other), runs a 5-phase
writing-session workflow with in-project state (`.tcc-workflow/`), and ships
dependency-free scripts to install the toolchain in sandboxes, compile with a filtered
log summary, and audit a project (placeholders, citations vs `.bib`, labels, floats
without source, unused acronyms, resumo/abstract). Install: upload
`dist/tcc-abnt.zip` in claude.ai (Customize → Skills), or in Claude Code
`/plugin marketplace add MateusMelloSouza/TCC-ABNT2` then
`/plugin install tcc-abnt2@tcc-abnt2`. Skill instructions are in English; the
documents it writes are in Brazilian Portuguese. MIT.
