# Training Findings - MCMV Search Online

Este documento registra os padrões de busca e descobertas acumuladas durante a fase de treinamento em `data_train/`.

## Termos de Busca que Funcionaram (Generalistas)
- `"beneficiários habilitados"`
- `"famílias sorteadas"`
- `"beneficiários titulares"`
- `"cadastro de interessados em moradia"`
- `"sorteio público" "Minha Casa Minha Vida"`
- `"lista de inscritos" "MCMV"`

## Padrões por Cidade

### Campinas - SP
- **Fonte Principal:** Diário Oficial e site da COHAB Campinas.
- **Frase de efeito:** "A Prefeitura Municipal de Campinas convoca" ou "divulga a relação".
- **Termos específicos:** "beneficiários habilitados", "famílias sorteadas".

### Sorocaba - SP
- **Fonte Principal:** Diário Oficial do Município (Jornal Município de Sorocaba).
- **Padrão de busca:** "Jornal Município de Sorocaba" + [número da edição].
- **Edições Críticas ( ground-truth):**
  - 1572: Inscritos Parque das Árvores
  - 1634: Inscritos Parque da Mata e Bem Viver
  - 1646: Inscritos Jardim Carandá
  - 1649: Sorteados Jardim Carandá
  - 1720: Deferimento sorteio Jardim Carandá e takeup Altos do Ipanema II

### Bauru - SP
- **Fonte Principal:** Site da prefeitura (Sistema MCMV).
- **URL Padrão:** `www2.bauru.sp.gov.br/arquivos/sist_mcmv/pmcmv/...`
- **Gotcha:** Empreendimentos de 2012 (Monte Verde, Mirante da Colina, Três Américas, Moradas do Buriti) estão em arquivos separados.

### Registro - SP
- **Fonte Principal:** Site da prefeitura.
- **Empreendimento:** Jardim Virgínia (2016).

## Dicas Gerais
- **Take-up incompleto:** Procurar por listas de "ausentes e reconvocados" ou "deferimento/indeferimento de sorteados". Isso ajuda a casar os dados com o arquivo `takeup_far_dec17.xlsx`.
- **Identificadores:** Alguns editais publicam apenas os últimos 4 dígitos do CPF ou CPFs truncados. Registrar isso na catalogação.
- **Wayback Machine:** Essencial para cidades que mudaram o portal ou removeram seções antigas de habitação.
