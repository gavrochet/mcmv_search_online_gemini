from src.execute_pipeline import run

capitais = [
    ("Rio Branco", "AC"),
    ("Maceió", "AL"),
    ("Macapá", "AP"),
    ("Manaus", "AM"),
    ("Salvador", "BA"),
    ("Fortaleza", "CE"),
    ("Brasília", "DF"),
    ("Vitória", "ES"),
    ("Goiânia", "GO"),
    ("São Luís", "MA"),
    ("Cuiabá", "MT"),
    ("Campo Grande", "MS"),
    ("Belo Horizonte", "MG"),
    ("Belém", "PA"),
    ("João Pessoa", "PB"),
    ("Curitiba", "PR"),
    ("Recife", "PE"),
    ("Teresina", "PI"),
    ("Rio de Janeiro", "RJ"),
    ("Natal", "RN"),
    ("Porto Alegre", "RS"),
    ("Porto Velho", "RO"),
    ("Boa Vista", "RR"),
    ("Florianópolis", "SC"),
    ("São Paulo", "SP"),
    ("Aracaju", "SE"),
    ("Palmas", "TO")
]

if __name__ == "__main__":
    print("Iniciando execução para as capitais de cada UF...")
    for municipio, uf in capitais:
        try:
            run(municipio, uf)
        except Exception as e:
            print(f"Erro ao processar {municipio}-{uf}: {e}")
    print("\nExecução para todas as capitais concluída.")
