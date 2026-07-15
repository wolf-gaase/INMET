import os
import re
import zipfile
import polars as pl
from concurrent.futures import ThreadPoolExecutor, as_completed

def _processar_zip_worker(caminho_zip, codigo_estacao):
    """
    Worker que abre o ZIP uma única vez e processa todos os seus CSVs internos.
    Retorna uma lista de DataFrames.
    """
    dfs_do_zip = []
    
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as z:
            lista_arquivos = z.namelist()
            
            # Filtra os CSVs desejados dentro DESTE zip específico
            if codigo_estacao:
                padrao_busca = rf'(?:^|[_/\-\s]){codigo_estacao}(?:$|[_.\-\s])'
                arquivos_encontrados = [
                    f for f in lista_arquivos 
                    if re.search(padrao_busca, f, re.IGNORECASE) and f.lower().endswith('.csv')
                ]
            else:
                arquivos_encontrados = [
                    f for f in lista_arquivos if f.lower().endswith('.csv')
                ]
            
            # Se não achou nada, encerra mais cedo
            if not arquivos_encontrados:
                return []

            # Loop sequencial APENAS nos arquivos internos deste ZIP aberto
            for nome_csv in arquivos_encontrados:
                try:
                    with z.open(nome_csv) as f:
                        conteudo_bruto = f.read()

                    # Metadados
                    metadata_df = pl.read_csv(
                        conteudo_bruto, separator=';', n_rows=7, has_header=False, encoding='latin-1'
                    )

                    metadados = {}
                    for row in metadata_df.iter_rows():
                        if row[0] is not None:
                            chave = str(row[0]).strip().replace(':', '').lower()
                            valor = str(row[1]).strip() if row[1] is not None else ""
                            metadados[chave] = valor
                    
                    def buscar_chave(termo, padrao=""):
                        for k, v in metadados.items():
                            if termo in k:
                                return v
                        return padrao

                    nome_estacao = buscar_chave('estacao', buscar_chave('regiao', 'Desconhecida')) 
                    codigo_wmo = buscar_chave('codigo', 'Desconhecido')
                    uf = buscar_chave('uf', '')
                    latitude = buscar_chave('latitude', '')
                    longitude = buscar_chave('longitude', '')
                    altitude = buscar_chave('altitude', '')

                    # Dados
                    df_ano = pl.read_csv(
                        conteudo_bruto, separator=";", encoding="latin-1", skip_rows=8,
                        has_header=True, infer_schema_length=0, truncate_ragged_lines=True
                    )
                    
                    if df_ano.width == 0:
                        continue
                    
                    colunas_arquivo = df_ano.columns
                    mapeamento_colunas = {}
                    
                    indices_desejados = {
                        'precipitacao' : 2, 'pressao_atmosferica' : 3, 'pressao_atmosferica_maxima' : 4,
                        'pressao_atmosferica_minima' : 5, 'radiacao' : 6, 'temperatura_ar' : 7,
                        'temperatura_orvalho' : 8, 'temperatura_maxima' : 9, 'temperatura_minima' : 10,
                        'temperatura_orvalho_maxima' : 11, 'temperatura_orvalho_minima' : 12,
                        'umidade_relativa_maxima' : 13, 'umidade_relativa_minima' : 14, 'umidade_relativa' : 15,
                        'vento_direcao' : 16, 'vento_rajada' : 17, 'vento_velocidade' : 18
                    }
                    
                    if len(colunas_arquivo) > 0: mapeamento_colunas[colunas_arquivo[0]] = 'data'
                    if len(colunas_arquivo) > 1: mapeamento_colunas[colunas_arquivo[1]] = 'hora_utc'

                    for nome_alvo, idx in indices_desejados.items():
                        if len(colunas_arquivo) > idx:
                            mapeamento_colunas[colunas_arquivo[idx]] = nome_alvo

                    df_ano = df_ano.select(list(mapeamento_colunas.keys())).rename(mapeamento_colunas)
                    
                    df_ano = df_ano.with_columns([
                        pl.lit(nome_estacao).alias('nome_estacao'),
                        pl.lit(codigo_wmo).alias('codigo_wmo'),
                        pl.lit(uf).alias('uf'),
                        pl.lit(latitude).alias('latitude'),
                        pl.lit(longitude).alias('longitude'),
                        pl.lit(altitude).alias('altitude')
                    ])

                    colunas_numericas = [
                        'precipitacao', 'pressao_atmosferica', 'pressao_atmosferica_maxima', 
                        'pressao_atmosferica_minima', 'radiacao', 'temperatura_ar', 
                        'temperatura_orvalho', 'temperatura_maxima', 'temperatura_minima', 
                        'temperatura_orvalho_maxima', 'temperatura_orvalho_minima', 
                        'umidade_relativa_maxima', 'umidade_relativa_minima', 'umidade_relativa', 
                        'vento_direcao', 'vento_rajada', 'vento_velocidade'
                    ]

                    for col in colunas_numericas:
                        if col in df_ano.columns:
                            # Expressão que limpa a vírgula e converte para número
                            expressao_numerica = (
                                pl.col(col)
                                .str.replace(",", ".", literal=True)
                                .cast(pl.Float64, strict=False)
                            )
                            
                            # Se o resultado for -9999.0, troca por None, senão mantem o número
                            df_ano = df_ano.with_columns(
                                pl.when(expressao_numerica == -9999.0)
                                .then(None)
                                .otherwise(expressao_numerica)
                                .alias(col)
                            )

                    dfs_do_zip.append(df_ano)


                    
                except Exception:
                    continue # Ignora erros em arquivos corrompidos isolados
                    
        return dfs_do_zip
    except Exception:
        return []

def extrair_e_consolidar_inmet(pasta_zips="../data", codigo_estacao=None, arquivo_saida="../data/dados_consolidados_inmet.parquet"):
    dados_consolidados = []
    
    pasta_zips_abs = os.path.abspath(pasta_zips)
    arquivo_saida_abs = os.path.abspath(arquivo_saida)
    caminho_estacoes = os.path.abspath("../data/estacoes_meteorologicas.csv") #Arquivo com nome e código das estações

    # Evita que ao informar apenas a região Sul ou Norte traga também SE ou NE
    if codigo_estacao in {"N","NE","CO","SE","S"}:
        codigo_estacao = f"INMET_{codigo_estacao}"

    
    if not os.path.exists(pasta_zips_abs):
        print(f"Erro: A pasta '{pasta_zips_abs}' não existe.")
        return

    arquivos_zip = [f for f in os.listdir(pasta_zips_abs) if f.endswith('.zip')]
    if not arquivos_zip:
        print(f"Nenhum arquivo .zip encontrado em '{pasta_zips_abs}'.")
        return

    msg_busca = f"da estação {codigo_estacao}" if codigo_estacao else "de TODAS as estações"
    print(f"Iniciando processamento paralelo por arquivo ZIP {msg_busca}...")

    # Dispara uma thread para CADA arquivo ZIP (Ano) externo
    with ThreadPoolExecutor(max_workers=None) as executor:
        futuros = {
            executor.submit(_processar_zip_worker, os.path.join(pasta_zips_abs, nome_zip), codigo_estacao): nome_zip 
            for nome_zip in arquivos_zip
        }
        
        for futuro in as_completed(futuros):
            nome_zip = futuros[futuro]
            lista_dfs = futuro.result()
            if lista_dfs:
                dados_consolidados.extend(lista_dfs)
                print(f" -> ZIP {nome_zip} processado com sucesso em paralelo.")

    if not dados_consolidados:
        print("Nenhum dado válido pôde ser extraído.")
        return

    print("\nConcatenando todos os dados limpos...")
    df_final = pl.concat(dados_consolidados)
    
    # Cruzamento de dados com o CSV de referência
    if os.path.exists(caminho_estacoes):
        print("Corrigindo nomes de estações 'Desconhecida' usando o arquivo de referência...")
        
        # Lê o CSV de referência e renomeia a coluna para evitar conflito no join
        df_ref = pl.read_csv(caminho_estacoes, separator=";").select(["codigo_wmo", "nome_estacao"])
        df_ref = df_ref.rename({"nome_estacao": "nome_estacao_correto"})
        
        # Faz o cruzamento (Left Join) baseado no código WMO
        df_final = df_final.join(df_ref, on="codigo_wmo", how="left")
        
        # Substitui os valores apenas onde for "Desconhecida" ou Nulo
        df_final = df_final.with_columns(
            pl.when(
                (pl.col("nome_estacao") == "Desconhecida") | 
                (pl.col("nome_estacao").is_null())
            )
            .then(pl.col("nome_estacao_correto"))
            .otherwise(pl.col("nome_estacao"))
            .alias("nome_estacao")
        ).drop("nome_estacao_correto") # Remove a coluna auxiliar do join
    else:
        print(f"Aviso: Arquivo de referência '{caminho_estacoes}' não encontrado. Pulando correção.")

    # 3. Salvamento direto no Parquet (Rápido e limpo)
    df_final.write_parquet(arquivo_saida_abs)
    print(f"\nSucesso absoluto! Arquivo salvo em: '{arquivo_saida_abs}'")
    #print(f"Total de horas processadas: {df_final.shape[0]:,}")

if __name__ == "__main__":
    extrair_e_consolidar_inmet(codigo_estacao="S", arquivo_saida="../data/regiao_sul_consolidada.parquet")