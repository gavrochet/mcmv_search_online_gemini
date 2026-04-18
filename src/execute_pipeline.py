import json
from pathlib import Path
from googlesearch import search
import pdfplumber

from src import config
from src.main import plan_city
from src.downloader import download, DownloadResult
from src.reverse_search import count_matches_in_text

def analyze_pdf(pdf_path: Path, sample_data: dict) -> int:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return 0

    hits = count_matches_in_text(
        text,
        cpfs_masked=sample_data["cpfs_masked"],
        cpfs_unmasked=sample_data["cpfs_unmasked"],
        nis_values=sample_data["nis_values"],
        nomes=sample_data["nomes"],
    )
    return hits

def run():
    print("Gerando plano para Sorocaba, SP...")
    plan = plan_city("Sorocaba", "SP", sample_size=50)
    
    cpf_queries = plan["cpf_grouped_queries"]
    sample_data = plan["sample"]
    
    print(f"Total de queries de CPF agrupadas (5 em 5): {len(cpf_queries)}")
    
    target_dir = Path("downloads/SP_sorocaba")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_urls = set()
    results_found = []

    # Executar apenas as primeiras 5 queries para ter mais chance de achar algo
    for i, query in enumerate(cpf_queries[:5]):
        print(f"\n--- Executando Query {i+1} ---")
        print(f"Q: {query}")
        
        try:
            urls = list(search(query, num_results=5, lang="pt"))
            for url in urls:
                print(f"Encontrado: {url}")
                if url in downloaded_urls:
                    continue
                
                # Vamos baixar se parecer um documento de interesse ou PDF
                if ".pdf" in url.lower() or "sorocaba.sp.gov.br" in url.lower():
                    print(f"  -> Baixando {url} ...")
                    try:
                        result: DownloadResult = download(url, target_dir=target_dir, base_filename="sorocaba_mcmv")
                        downloaded_urls.add(url)
                        
                        if result.local_path.suffix.lower() == ".pdf":
                            print(f"  -> Analisando PDF {result.local_path.name} ...")
                            hits = analyze_pdf(result.local_path, sample_data)
                            print(f"  -> MATCHES ENCONTRADOS: {hits}")
                            if hits > 0:
                                results_found.append({"url": url, "hits": hits, "file": str(result.local_path)})
                        else:
                            print(f"  -> Arquivo {result.local_path.name} salvo, mas não é PDF.")
                    except Exception as e:
                        print(f"  -> Falha no download: {e}")
        except Exception as e:
            print(f"Erro na busca do Google: {e}")

    print("\n=== RESUMO DA ANÁLISE ===")
    if not results_found:
        print("Nenhum documento com matches foi encontrado nesta rodada rápida.")
    for r in results_found:
        print(f"URL: {r['url']}")
        print(f"Arquivo: {r['file']}")
        print(f"Identificadores Casados: {r['hits']}\n")

if __name__ == "__main__":
    run()
