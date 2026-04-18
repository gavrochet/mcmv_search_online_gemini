# MCMV Search Online Gemini

Agente especializado na busca, coleta e catalogação de documentos públicos do programa **Minha Casa Minha Vida (MCMV) - Faixa 1** (2009-2020).

## Objetivo
Localizar editais, listas de inscritos, sorteados, suplentes e atas de sorteio para alimentar pipelines de pesquisa acadêmica sobre os efeitos do programa.

## Estrutura do Repositório
- `src/`: Código fonte do agente.
- `scripts/`: Scripts auxiliares para análise de dados e processamento de PDFs.
- `GEMINI.md`: Guia mestre de operação do agente (instruções críticas).
- `catalog/`: Documentação de descobertas e dicas de treinamento.

## Funcionalidades Principais
- Busca automatizada em portais governamentais e Wayback Machine.
- Busca reversa baseada em CPFs/NIS (take-up data).
- Catalogação estruturada com extração de metadados.

## Setup
1. Clone o repositório: `git clone https://github.com/seu-usuario/mcmv_search_online_gemini.git`
2. Instale as dependências: `pip install -r requirements.txt`
3. Coloque os dados de referência (não inclusos no repo) em `reference_data/`.

## Licença
Documentos coletados são públicos. O código está sob licença MIT.
