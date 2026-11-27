# Contribuindo

Este repositório é um *skill* para o Claude: instruções em Markdown lidas pelo
modelo, mais alguns scripts. Contribuições úteis, em ordem de valor:

1. **Perfil de template da sua universidade** (`skills/tcc-abnt/references/templates/<nome>.md`).
   Use o esqueleto `skills/tcc-abnt/assets/TEMPLATE-profile.md` e o procedimento em
   `references/templates/README.md`. Tudo verificado por `grep` no `.sty`/`.cls` e por
   uma compilação limpa — nada de memória. Adicione a pista de identificação na tabela
   de `templates/README.md` e no "Step 0" do `SKILL.md`.
2. **Correções de norma** com fonte (manual de biblioteca universitária, texto da
   norma, changelog do abnTeX2). Indique a edição (`NBR 10520:2023`) e o que muda na
   prática para um projeto LaTeX.
3. **Armadilhas de compilação** reproduzíveis (mensagem exata, causa, correção que não
   toca o `.sty` do template).
4. Melhorias nos scripts (`skills/tcc-abnt/scripts/`): só biblioteca-padrão do Python
   (3.8+) e bash POSIX-ish; nunca reescrever um arquivo do projeto do usuário; escrita
   atômica (arquivo temporário + `os.replace`).

## Antes de abrir o PR

```bash
python3 scripts/check.py           # frontmatter, links, manifests, scripts, dados pessoais
bash scripts/package.sh            # gera dist/tcc-abnt.zip localmente (não commite: a release o anexa)
```

Testes manuais úteis: compilar o modelo canônico (`abntex2-modelo-trabalho-academico`)
com `scripts/compile-check.sh` e rodar `scripts/audit-tex.py` sobre ele; se tiver um
projeto UniforTeX2, repetir com ele.

## Regras editoriais

- `SKILL.md` fica abaixo de 500 linhas; detalhe vai para `references/`.
- Instruções em inglês (é o que o modelo lê), terminologia ABNT em português,
  exemplos de texto em pt-BR.
- Explique o *porquê* das regras em vez de acumular "NUNCA/SEMPRE".
- Nada de dados pessoais, nomes de orientadores, títulos de TCC reais ou caminhos de
  máquina — o `check.py` recusa alguns padrões, mas a revisão humana é o filtro real.
- Não redistribua templates institucionais (`.sty`, logos) aqui; aponte para a
  distribuição oficial (Overleaf/GitHub da instituição).

## Versionamento

Semver em `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` e no
`metadata.version` do `SKILL.md`; anote em `CHANGELOG.md`. Uma tag `vX.Y.Z` gera a
release com o ZIP anexado (workflow `validate.yml`).
