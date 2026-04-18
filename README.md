# mcmv_search_online

Agente de busca e coleta de editais públicos do programa **Minha Casa Minha Vida (MCMV) — Faixa 1** (2009–2020).

Alimenta um pipeline de pesquisa acadêmica que explora a aleatorização via sorteio público para inferência causal sobre efeitos do programa.

## Escopo

- **Apenas Faixa 1** (sorteio público juridicamente obrigatório — única faixa com listas nominais publicadas).
- Período **2009–2020** (MCMV original, antes da transição para Casa Verde e Amarela).
- Fontes: Diários Oficiais municipais/estaduais, portais de prefeituras e COHABs, Wayback Machine, Ministério Público, TCEs, etc.
- Saída: documentos catalogados (inscritos, sorteados, suplentes, cadastro reserva, atas) em `catalog/catalog.jsonl`.

## Especificação completa

Ver **[CLAUDE.md](CLAUDE.md)** — o documento de especificação que orienta o agente.

## Estrutura

```
mcmv_search_online/
├── CLAUDE.md                  # especificação do agente
├── README.md
├── requirements.txt
├── src/                       # código do agente
│   ├── config.py              # caminhos e constantes
│   ├── ref_data.py            # carrega dados de referência
│   ├── queries.py             # gera queries de busca
│   ├── search_engine.py       # wrapper para motores de busca
│   ├── downloader.py          # download + hashing SHA-256
│   ├── reverse_search.py      # busca reversa por CPF/NIS/nome
│   ├── catalog.py             # escrita do catálogo JSONL
│   └── main.py                # orquestrador (Rodada 1 e 2)
├── scripts/
│   └── analyze_data_train.py  # benchmark contra arquivos já coletados
├── reference_data/            # (gitignored) dados fornecidos pelo pesquisador
├── data_train/                # (gitignored) set de validação — editais já coletados
├── downloads/                 # (gitignored) arquivos baixados
├── catalog/                   # (gitignored) catálogo, logs
└── tmp/                       # (gitignored) área temporária
```

## Execução

```bash
pip install -r requirements.txt
python -m src.main --rodada 1         # varredura em cidades do takeup
python -m src.main --rodada 2         # cidades com empreendimentos mas sem contratos
python scripts/analyze_data_train.py  # benchmark contra data_train/
```

## Dados de referência (não versionados)

- `reference_data/dados_abertos_filtrado.csv` — empreendimentos MCMV Faixa 1 por cidade.
- `reference_data/takeup_far_dec17.xlsx` — contratos assinados até dez/2017 (Nome, NIS, CPF, Cidade, Empreendimento).

## Notas de ética e segurança

- Os documentos coletados já são **públicos** (publicados em diários oficiais e portais governamentais).
- Identificadores pessoais usados na busca reversa **nunca** são persistidos em logs em texto claro (somente hashes ou referências por índice).
- Respeito a `robots.txt` e rate limits por domínio.
