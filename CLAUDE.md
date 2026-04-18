# CLAUDE.md — Agente de Busca e Coleta de Editais MCMV Faixa 1

## 1. Objetivo

Localizar, baixar e catalogar, na internet aberta, documentos públicos (editais, listas, atas, resultados, anexos) do programa **Minha Casa Minha Vida (MCMV) — exclusivamente Faixa 1** que contenham **listas nominais de candidatos inscritos, sorteados, suplentes ou em cadastro reserva** em processos de seleção habitacional por sorteio público.

**Período de interesse:** 2009 a 2020 (programa MCMV original, Faixa 1, antes da transição para Casa Verde e Amarela).

**Finalidade:** alimentar um pipeline de pesquisa acadêmica que explora a aleatorização via sorteio para inferência causal sobre efeitos do programa. A **completude da lista** (idealmente com CPF, NIS OU nome completo) é crítica.

**Escopo restrito a Faixa 1** (renda familiar até aproximadamente R$ 1.600 no desenho original do programa, ajustada ao longo dos anos). Faixa 1 é onde o sorteio é juridicamente obrigatório e onde há listas nominais públicas. **Faixas 1.5, 2 e 3 estão fora do escopo** — descartar documentos que sejam exclusivamente dessas faixas.

---

## 2. Estrutura de pastas

O agente deve usar e manter a seguinte estrutura. As pastas de dados de referência já existem com os arquivos colocados pelo pesquisador; as demais devem ser criadas pelo agente conforme necessário.

```
mcmv_editais_search/
├── CLAUDE.md                          # este arquivo
├── reference_data/                    # dados de referência fornecidos pelo pesquisador
│   ├── dados_abertos_filtrados.csv    # empreendimentos MCMV Faixa 1 por cidade + data de aprovação
│   └── takeup_dec2017.xlsx            # contratos assinados até dez/2017 (Nome, NIS, CPF, Cidade, Empreendimento)
├── catalog/
│   ├── catalog.jsonl                  # um registro por documento encontrado (formato na §7)
│   ├── catalog_report.md              # relatório-resumo da varredura
│   ├── coverage_gaps.md               # municípios-alvo onde a busca foi exaustiva mas nada foi encontrado
│   └── search_log.jsonl               # log de queries executadas por cidade (para auditoria e retomada)
├── downloads/                         # arquivos baixados, organizados por cidade
│   └── {UF}_{municipio_slug}/
│       ├── {ano}_{numero_edital_slug}_{tipo}_{hash8}.{ext}
│       └── _metadata/
│           └── {mesmo_nome}.json      # metadados do documento, idêntico ao registro no catalog.jsonl
└── tmp/                               # área de trabalho temporária (downloads parciais, etc.)
```

**Convenções de nomenclatura:**
- `municipio_slug`: nome do município em minúsculas, sem acentos, espaços convertidos em `_` (ex.: `sao_jose_do_rio_preto`).
- `hash8`: primeiros 8 caracteres do SHA-256 do arquivo baixado, para evitar colisões.
- `tipo`: um de `inscritos`, `sorteados`, `suplentes`, `cadastro_reserva`, `ata`, `misto` (mais de um tipo no mesmo arquivo).
- Se o número do edital não estiver disponível, usar `sem_numero` no lugar de `numero_edital_slug`.

---

## 3. Dados de referência fornecidos

### 3.1 `reference_data/dados_abertos_filtrados.csv`

Contém, **por cidade**, o **Nome** e a **data de aprovação** de cada um dos **empreendimentos MCMV Faixa 1** a serem analisados. É o universo de empreendimentos-alvo da pesquisa.

### 3.2 `reference_data/takeup_dec2017.xlsx`

Contém a lista de **todas as pessoas que assinaram contrato junto à Caixa Econômica Federal** para o MCMV Faixa 1 **até dezembro de 2017** — ou seja, pessoas que foram sorteadas e efetivamente formalizaram o contrato. Colunas: **Nome, NIS, CPF, Cidade, Empreendimento**.

Este arquivo serve a dois propósitos:

1. **Definir o universo prioritário de cidades** para a primeira rodada de busca (§5.1).
2. **Fornecer identificadores (CPF, NIS, Nome Completo) para busca reversa** — documentos que contenham múltiplos desses identificadores são quase certamente listas de sorteio MCMV Faixa 1 (§5.3).

---

## 4. Definições e escopo

**Documento de interesse** — qualquer PDF, planilha, página HTML, imagem digitalizada ou arquivo equivalente que satisfaça pelo menos um dos critérios:

1. Lista de **inscritos** (candidatos habilitados, pré-selecionados, classificados) em edital MCMV Faixa 1 com nome e/ou identificador.
2. Lista de **sorteados** (contemplados, selecionados, beneficiários) de edital MCMV Faixa 1 com nome e/ou identificador.
3. Lista de **suplentes**, **cadastro reserva** ou **lista de espera** vinculada a sorteio MCMV Faixa 1.
4. **Atas de sorteio público**, **resultados de audiência pública de seleção** ou **relatórios de comissão de seleção** que nomeiem beneficiários Faixa 1.
5. **Editais de convocação** que publiquem listas anexas de candidatos Faixa 1.

**Fora do escopo:** editais de chamamento de construtoras, editais de licitação de obras, cartilhas do programa, relatórios agregados sem nomes, materiais exclusivamente do MCMV Entidades (modalidade rural/entidades organizadoras), e documentos exclusivamente de Faixas 1.5, 2 ou 3.

**Ambiguidade sobre a Faixa:** se um documento não identifica explicitamente a faixa, mas (a) menciona "sorteio público", "seleção habitacional", "habitação de interesse social", ou (b) contém identificadores que também aparecem no `takeup_dec2017.xlsx`, tratar como candidato Faixa 1 e registrar com confianca `media` ou `alta` conforme o caso.

---

## 5. Estratégia de busca

### 5.1 Ordem de prioridade das cidades

**Rodada 1 — Cidades presentes em `takeup_dec2017.xlsx`:**  
Executar varredura completa e profunda em todas as cidades que aparecem nesse arquivo. Essas cidades têm sorteios conhecidos que produziram contratos, portanto há alta probabilidade de existirem listas públicas.

**Rodada 2 — Cidades em `dados_abertos_filtrados.csv` mas ausentes de `takeup_dec2017.xlsx`:**  
Somente iniciar a Rodada 2 após a conclusão da Rodada 1. Cidades nessa situação tiveram empreendimentos aprovados mas nenhum contrato assinado até dez/2017 — pode significar atraso de obra, atraso de contratação, ou problemas no empreendimento. Ainda vale buscar, porque listas de inscritos/sorteados podem existir mesmo sem contratação subsequente.

Dentro de cada rodada, priorizar cidades em ordem decrescente de **número de linhas no takeup** (Rodada 1) ou **número de empreendimentos** (Rodada 2) — mais volume implica maior probabilidade de documentos públicos bem preservados.

### 5.2 Busca geral por variantes terminológicas

Para cada cidade, gerar combinações com os seguintes termos:

**Programa:** "Minha Casa Minha Vida", "MCMV", "PMCMV", "Programa Minha Casa Minha Vida", "habitação de interesse social" + "sorteio", "Faixa 1", "Faixa I".

**Documento:** edital, edital de convocação, edital de chamamento público, edital de seleção, ata de sorteio, resultado do sorteio, lista de sorteados, lista de contemplados, lista de beneficiários, lista de habilitados, lista de classificados, relação de sorteados, relação de inscritos, homologação do sorteio, cadastro reserva, lista de suplentes, lista de espera.

**Processo:** sorteio, sorteio público, sorteio eletrônico, seleção pública, audiência pública de sorteio, demanda aberta, demanda fechada.

**Ator institucional:** COHAB, SEHAB, SMH, Secretaria de Habitação, Caixa Econômica Federal, CEF, prefeitura municipal de [cidade], fundação habitacional, companhia habitacional.

### 5.3 Busca reversa por identificadores do takeup

**Para TODAS as cidades em varredura** (tanto Rodada 1 quanto Rodada 2), executar também buscas reversas usando identificadores do `takeup_dec2017.xlsx`:

- **CPF completo** (formato `XXX.XXX.XXX-XX` e também `XXXXXXXXXXX` sem máscara).
- **NIS** (11 dígitos) — aparece frequentemente como alternativa ao CPF em editais.
- **Nome Completo** — para casos em que apenas o nome está presente no documento.

**Procedimento:**

1. Filtrar o takeup pela cidade sendo pesquisada.
2. Amostrar (aleatoriamente, para evitar viés) entre 50 e 100 identificadores distintos dessa cidade — misturando CPFs, NIS e Nomes Completos.
3. Executar queries dirigidas, ex.:
   - `"XXX.XXX.XXX-XX" site:gov.br`
   - `"XXX.XXX.XXX-XX" "minha casa minha vida"`
   - `"{nome completo}" "sorteado" OR "contemplado"`
   - `"{NIS}" "MCMV" OR "habitação"`
4. Para cada documento que aparecer nos resultados, fazer download e contar quantos identificadores da amostra dessa cidade aparecem nele.
5. **Critério de retenção:** baixar e catalogar o documento se tiver **mais de 10 matches** com identificadores da cidade pesquisada. Abaixo desse limiar, descartar (provavelmente é coincidência, documento de outra cidade, ou documento agregado sem interesse para o merge).
6. Quando um documento for retido via busca reversa, **expandir a contagem** para o universo completo de identificadores daquela cidade no takeup (não só a amostra), e registrar no catálogo.

**Importante:** não logar ou persistir CPFs/NIS em arquivos de auditoria públicos (`search_log.jsonl` não deve conter identificadores pessoais em texto claro — usar hash ou referência por índice de linha do takeup).

### 5.4 Fontes prioritárias

1. **Diários Oficiais municipais** (DOM) — portais como `dom.{cidade}.{uf}.gov.br`, `diariooficial.{cidade}...`, Imprensa Oficial estadual. Usar operador `site:`.
2. **Diários Oficiais estaduais** (DOE) — alguns municípios publicam no DOE.
3. **Portais de transparência municipais** — seções "Habitação", "Programas Sociais", "Editais".
4. **Sites de COHABs e companhias habitacionais estaduais** (COHAB-SP, COHAB-MG, AGEHAB-GO, COHAPAR-PR, SEHAB-DF, etc.).
5. **Wayback Machine (`web.archive.org`)** — **fonte de primeira classe.** Muitas prefeituras removeram editais antigos; o Wayback frequentemente tem a única cópia sobrevivente. Sempre checar snapshots de portais municipais para os anos 2009-2020.
6. **Cache do Google** — para documentos recém-removidos.
7. **Scribd, Academia.edu, ResearchGate, Issuu** — mirrors informais comuns.
8. **Câmaras Municipais** — requerimentos com listas anexas.
9. **Ministério Público estadual e federal** — inquéritos civis públicos sobre MCMV frequentemente anexam listas.
10. **Repositórios do TCU, CGU, TCEs** — auditorias do MCMV.
11. **Portal da Caixa** (`caixa.gov.br`) — raramente publica listas nominais, mas checar.

### 5.5 Operadores de busca sugeridos

```
site:gov.br "minha casa minha vida" "sorteados" "faixa 1" filetype:pdf
site:{uf}.gov.br "lista de contemplados" "MCMV"
"ata de sorteio" "minha casa minha vida" "faixa 1" filetype:pdf
"relação dos sorteados" "MCMV" site:gov.br
"edital de convocação" "minha casa minha vida" "CPF" filetype:pdf
"empreendimento" "sorteados" "MCMV" inurl:diario
site:web.archive.org "minha casa minha vida" "{cidade}" "sorteio"
"{nome empreendimento}" "sorteados" OR "contemplados"
```

Iterar substituindo termos, combinando com nomes de estados/cidades, e com nomes de empreendimentos específicos obtidos de `dados_abertos_filtrados.csv`.

---

## 6. Heurísticas e armadilhas conhecidas

- **CPFs parciais são comuns** (ex.: `***.123.456-**`, ou apenas os 4 últimos dígitos — caso conhecido: Betim). Registrar em `identificadores_presentes` — ainda é útil para merge, com estratégia específica.
- **Checkbox HTML renderizado em PDF** (casos conhecidos: Londrina, Guarulhos): marcações ☒/☐ que viram caracteres estranhos na extração de texto. Sinalizar em `observacoes`.
- **Editais multi-arquivo**: um mesmo sorteio pode estar em vários PDFs (inscritos em um, sorteados em outro, suplentes em um terceiro). Agrupar por `numero_edital` + `municipio` e referenciar em `documento_relacionado`.
- **Duplicatas exatas**: mesmo edital pode aparecer em DOM, portal da prefeitura e Scribd. Deduplicar por hash SHA-256, mas registrar todos os URLs como fontes alternativas no mesmo registro.
- **Quase-duplicatas**: versões republicadas com pequenas correções. Tratar como documentos distintos e marcar relação.
- **Tabelas escaneadas**: PDFs de 2009-2013 frequentemente são digitalizações de baixa qualidade. Marcar `formato: "pdf_scan"` para OCR posterior.
- **MCMV Entidades** (modalidade associativa) geralmente não tem sorteio público — excluir se for puramente entidade.
- **"Lista de espera" da COHAB** (cadastro genérico pré-MCMV) não é lista de sorteio de edital específico. Distinguir.
- **Bauru (2012)** — caso conhecido de múltiplos empreendimentos (Monte Verde, Mirante da Colina, Três Américas, Moradas do Buriti) com listas em arquivos separados. Ficar atento a padrões similares em outras cidades.
- **Truncamento de CPFs** (caso conhecido: Registro) — alguns editais publicam CPFs truncados a 9 dígitos. Sinalizar.
- **Cidades com nomes ambíguos**: sempre combinar nome do município com UF nas queries (ex.: "São José do Rio Preto SP", não só "São José do Rio Preto").

---

## 7. Formato de catalogação

Para cada documento retido, gravar um registro JSON em `catalog/catalog.jsonl` (um objeto por linha) **e** uma cópia idêntica em `downloads/{UF}_{municipio_slug}/_metadata/{nome_arquivo}.json`:

```json
{
  "doc_id": "uuid-v4",
  "url_primaria": "URL direta do documento",
  "urls_alternativas": ["lista de URLs duplicadas/mirrors"],
  "url_host": "domínio raiz da URL primária",
  "fonte_tipo": "DOM | DOE | portal_prefeitura | cohab | wayback | scribd | mp | tce | cache_google | outro",
  "via_busca_reversa": false,
  "caminho_local": "downloads/SP_sao_paulo/2013_edital_001_sorteados_a3f2b1c4.pdf",
  "hash_sha256": "hash completo do arquivo baixado",
  "tamanho_bytes": 1234567,

  "municipio": "Nome do município",
  "uf": "Sigla do estado",

  "ano_publicacao": "YYYY (do documento)",
  "ano_sorteio": "YYYY (do sorteio propriamente dito, se diferente ou se identificável)",
  "numero_edital": "ex. Edital 001/2013, ou null",
  "empreendimentos_citados": ["Residencial X", "Condomínio Y"],
  "empreendimentos_match_dados_abertos": ["Residencial X"],

  "faixa_renda": "Faixa 1 | Faixa 1 (inferida) | mista_com_faixa_1 | nao_especificado",
  "tipo_lista": ["inscritos", "sorteados", "suplentes", "cadastro_reserva", "ata"],
  "identificadores_presentes": ["nome_completo", "cpf_completo", "cpf_parcial_4dig", "cpf_parcial_mascara", "cpf_truncado_9dig", "nis", "rg", "numero_inscricao"],
  "numero_aproximado_de_linhas": 1234,
  "formato": "pdf_texto | pdf_scan | pdf_html_renderizado | xlsx | xls | csv | html | doc | docx | imagem",

  "takeup_matches": {
    "amostra_usada_tamanho": 50,
    "amostra_matches": 27,
    "universo_cidade_tamanho": 412,
    "universo_matches": 389
  },

  "confianca": "alta | media | baixa",
  "motivo_confianca": "ex. 'Faixa 1 explícita + 389/412 matches com takeup da cidade'",
  "observacoes": "Notas sobre qualidade, particularidades, multi-arquivo, etc.",
  "documentos_relacionados": ["doc_id de arquivos do mesmo edital"],

  "data_acesso": "YYYY-MM-DDTHH:MM:SSZ",
  "data_catalogacao": "YYYY-MM-DDTHH:MM:SSZ"
}
```

**Níveis de `confianca`:**
- **alta:** Faixa 1 explícita OU ≥ 10 matches com takeup da cidade OU ambos.
- **media:** sorteio MCMV evidente mas Faixa não especificada; ou poucos matches mas documento bem identificado.
- **baixa:** documento parece relevante mas há ambiguidade significativa (sem Faixa, sem identificadores compatíveis, contexto incerto).

---

## 8. Download e organização local

Para cada documento retido:

1. Calcular SHA-256. Se o hash já existe em `catalog.jsonl`, **não duplicar o download** — apenas adicionar a URL atual ao campo `urls_alternativas` do registro existente.
2. Salvar em `downloads/{UF}_{municipio_slug}/` com o padrão de nome descrito na §2.
3. Gravar metadata JSON em `_metadata/` com o mesmo nome base.
4. Anexar registro ao `catalog.jsonl`.
5. Registrar a query executada e timestamp em `search_log.jsonl` (sem CPFs/NIS em texto claro).

**Atomicidade:** escrever primeiro em `tmp/`, validar hash e extensão, depois mover para o destino final. Isso evita arquivos parciais em caso de interrupção.

**Retomada:** o agente deve ser capaz de reiniciar a partir do `search_log.jsonl` — não refazer buscas já concluídas para a mesma cidade/query nos últimos 7 dias, a menos que explicitamente instruído.

---

## 9. Critérios de cobertura e sucesso

**Por cidade (Rodada 1 e Rodada 2):**
- Ao menos 5 combinações distintas de query geral executadas.
- Ao menos 3 fontes distintas consultadas (DOM, portal prefeitura, Wayback no mínimo).
- Busca reversa com amostra de 20-50 identificadores do takeup (Rodada 1) ou tentativa equivalente com nomes de empreendimentos (Rodada 2).
- Snapshots do Wayback Machine checados para o portal municipal de habitação em pelo menos 3 pontos no tempo dentro de 2009-2020.

**Sinalização de exaustão sem achado:**  
Cidades onde a busca foi completa mas nada foi encontrado devem ser registradas em `catalog/coverage_gaps.md` com:
- Nome, UF, rodada.
- Queries executadas (resumo).
- Fontes consultadas.
- Número de empreendimentos esperados (do `dados_abertos_filtrados.csv`) e de contratos assinados (do `takeup_dec2017.xlsx`).
- Hipóteses para a ausência (portal removido, documento nunca publicado online, etc.).

Essa lista orienta busca manual posterior pelo pesquisador.

---

## 10. Entregáveis finais

1. **`downloads/`** — todos os arquivos baixados, organizados por `{UF}_{municipio_slug}/`, com metadata JSON individual em `_metadata/`.
2. **`catalog/catalog.jsonl`** — catálogo unificado, um registro por documento.
3. **`catalog/catalog_report.md`** — relatório resumindo:
   - Total de documentos por UF e por ano.
   - Distribuição por `tipo_lista` e `faixa_renda`.
   - Distribuição por `confianca`.
   - Cobertura da Rodada 1 vs Rodada 2.
   - Cidades com maior e menor volume de achados.
   - Estimativa de cobertura do universo do takeup (quantas cidades do takeup têm ao menos um documento catalogado).
4. **`catalog/coverage_gaps.md`** — municípios-alvo onde nada foi encontrado, para busca manual posterior.
5. **`catalog/search_log.jsonl`** — log de auditoria das queries executadas.

---

## 11. Execução — ordem sugerida

1. Carregar `reference_data/takeup_dec2017.xlsx` e extrair lista de cidades únicas (ordenadas por contagem de linhas, decrescente).
2. Carregar `reference_data/dados_abertos_filtrados.csv` e extrair lista de cidades únicas com empreendimentos Faixa 1.
3. Identificar conjunto diferença: cidades em `dados_abertos` mas não em `takeup` (universo da Rodada 2).
4. Criar estrutura de pastas conforme §2.
5. **Executar Rodada 1** cidade por cidade: busca geral (§5.2) + busca reversa com identificadores do takeup (§5.3) + checagem de Wayback Machine.
6. Catalogar e baixar conforme §7 e §8.
7. Após conclusão completa da Rodada 1, **executar Rodada 2** com busca geral + busca por nomes de empreendimentos (já que essas cidades não têm identificadores no takeup).
8. Gerar relatórios finais (§10).

**Ritmo sugerido:** processar cidades em lotes, gravando checkpoints no `search_log.jsonl` a cada cidade completada, para permitir retomada em caso de interrupção.

---

## 12. Notas de segurança e ética

- Os arquivos `reference_data/` contêm dados pessoais identificáveis (CPF, NIS, nomes). Eles são usados **apenas localmente** pelo agente para busca reversa; **nunca** devem ser enviados para serviços externos além das queries estritamente necessárias (e essas queries contêm apenas um identificador por vez, já publicado em contexto público no documento-alvo).
- O `search_log.jsonl` não deve conter CPFs/NIS em texto claro — usar SHA-256 truncado (primeiros 16 caracteres) ou referência por índice de linha do takeup.
- Os documentos baixados já são públicos (publicados em Diários Oficiais e portais governamentais). O agente não está exfiltrando dados privados — está consolidando dados já publicados.
- Respeitar `robots.txt` e rate limits razoáveis (ex.: 1-2 requests/segundo por domínio, backoff exponencial em caso de erro).