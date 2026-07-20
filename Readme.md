# Análise de Dados Meteorológicos das Estações Automáticas do INMET (Em Desenvolvimento)

## Objetivo

Efetuar a análise dos dados meteorológicos das estações automáticas do INMET entre 2015 e 2025, realizando limpeza, transformação, análise exploratória e geração de visualizações interativas para identificação de padrões climáticos.

## Introdução

Os [dados históricos](https://portal.inmet.gov.br/dadoshistoricos) e o catálogo das [estações automáticas](https://portal.inmet.gov.br/paginas/catalogoaut) foram obtidos do Portal do Instituto Nacional de Meteorologia (INMET).

- REGIÃO: Regiões do Brasil (N,NE,CO, SE, S).
- UF: Unidades da Federação.
- ESTAÇÃO: Nome da estação.
- CODIGO (WMO): identificador numérico internacional fornecido pela Organização Meteorológica Mundial (WMO). Códigos iniciados por letras são - utilizados para identificar as estações automáticas (ex: A001).
- LATITUDE:Latitude da localização da estação.
- LONGITUDE:Longitude da localização da estação.
- ALTITUDE:altitude da estação em relação ao nível do mar.
- DATA DE FUNDAÇÃO (YYYY-MM-DD): Data de fundação da estação.

# Dicionário de Dados
**Cabeçalho**


| Coluna                         | Descrição                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| REGIÃO:                        | Região do Brasil (N,NE,CO, SE, S).                                                           |
| UF:                            | Unidades da Federação.                                                                       |
| ESTAÇÃO:                       | Nome da estação.                                                                             |
| CODIGO (WMO):                  | identificador numérico internacional fornecido pela Organização Meteorológica Mundial (WMO). |
| LATITUDE:                      | Latitude da localização da estação.                                                          |
| LONGITUDE:                     | Longitude da localização da estação.                                                         |
| ALTITUDE:                      | Altitude da estação em relação ao nível do mar.                                              |
| DATA DE FUNDAÇÃO (YYYY-MM-DD): | Data de fundação da estação.                                                                 |


**Dados**

| Coluna                                                | Descrição                                                           |
| ----------------------------------------------------- | ------------------------------------------------------------------- |
| DATA (YYYY-MM-DD)                                     | Data da medição                                                     |
| HORA (UTC)                                            | Hora da medição (horário UTC)                                       |
| PRECIPITAÇÃO TOTAL, HORÁRIO (mm)                      | Precipitação total no horário (mm)                                  |
| PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB) | Pressao atmosférica ao nível da estação no horário (em milibares)   |
| PRESSÃO ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)       | Pressão atmosférica máxima na hora ant. (aut) (em milibares)        |
| PRESSÃO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)      | Pressão atmosférica min. Na hora ant. (aut) (em milibares)          |
| RADIACAO GLOBAL (KJ/m²)                               | Radiação global (kj/m²)                                             |
| TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)          | Temperatura do ar - bulbo seco, horaria (°c)                        |
| TEMPERATURA DO PONTO DE ORVALHO (°C)                  | Temperatura do ponto de orvalho (°c)                                |
| TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)            | Temperatura máxima na hora ant. (aut) (°c)                          |
| TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)            | Temperatura mínima na hora ant. (aut) (°c)                          |
| TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)      | Temperatura orvalho máxima. Na hora ant. (aut) (°c)                 |
| TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)      | Temperatura orvalho mínima. Na hora ant. (aut) (°c)                 |
| UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)              | Umidade relativa máxima. Na hora ant. (aut) (%)                     |
| UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)              | Umidade relativa mínima Na hora ant. (aut) (%)                      |
| UMIDADE RELATIVA DO AR, HORARIA (%)                   | Umidade relativa do ar, horaria (%)                                 |
| VENTO, DIREÇÃO HORARIA (gr) (° (gr))                  | Direção horaria do vento (gr) (° (gr))                              |
| VENTO, RAJADA MAXIMA (m/s)                            | Velocidade máxima da rajada de vento (m/s)                          |
| VENTO, VELOCIDADE HORARIA (m/s)                       | Velocidade horaria do vento (m/s)                                   |