import pandas as pd
import requests
import json
import unicodedata

# Função para normalizar texto e corrigir caracteres bugados
def normalize_text(text):
    if isinstance(text, str):
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text

# Carregar os arquivos XLS
# folha_pagamento = pd.read_excel('rafaelBB.xlsx', sheet_name=4)  # Substitua o sheet_name pelo nome correto
# base = pd.read_excel('ARENA 61.xlsx', sheet_name=1)
base = pd.read_excel('rafaelBB.xlsx', sheet_name=1)

# Formatar a DATA para o formato YYYY-MM-DD
if 'DATA' in base.columns:
    base['DATA'] = pd.to_datetime(base['DATA'], errors='coerce').dt.strftime('%Y-%m-%d')

# Adicionar os campos faltantes no DataFrame
base['FORMA DE PAGAMENTO'] = base['FORMA DE PAGAMENTO'].fillna('Pix')  # Preenchendo forma de pagamento com Pix por padrão
base['C/D'] = base['C/D'].fillna('Saída')  # Supondo "Débito" como padrão
base['FIXO/VARIAVEL'] = base['FIXO/VARIAVEL'].fillna('VARIAVEL')  # Assumindo "VARIAVEL" como padrão

# Adicionar dados fictícios para pagamentos
base['STATUS'] = 'pendente'  # Status padrão
base['PARCELAS'] = base['PARCELAS']  # Número de parcelas padrão (alterar se necessário)
base['VALOR_PARCELA'] = base['VALOR'].apply(lambda x: round(x / 1, 2))  # Calculando valor da parcela para 1 parcela

# Construir o JSON no formato esperado
data = {
    "account_name": "rafaelBB",
    "data": []
}

for _, row in base.iterrows():
    # Criar a estrutura do pagamento
    payment = {
        "status": normalize_text(row['STATUS']),
        "installments": row['PARCELAS'],
        "installment_value": row['VALOR_PARCELA'],
    }

    # Adicionar o item formatado
    item = {
        "nomeEmpresa": normalize_text(row['NOME/EMPRESA']),
        "natureza": normalize_text(row['NATUREZA']),
        "tipo_natureza": normalize_text(row['TIPO NATUREZA']),
        "valor": float(row['VALOR']),
        "moviment_type": normalize_text(row['C/D']),
        "formaDePagamento": normalize_text(row['FORMA DE PAGAMENTO']),
        "centroDeCusto": normalize_text(row['CENTRO DE CUSTO']),
        "fixoVariavel": normalize_text(row['FIXO/VARIAVEL']),
        "data": row['DATA'],
        "mes": pd.to_datetime(row['DATA'], errors='coerce').month if 'DATA' in row else None,
        "payment": payment
    }
    data['data'].append(item)

# Converter para JSON
data_json = json.dumps(data, indent=4, ensure_ascii=False)

# Configurar o URL do endpoint Laravel e os headers
url = "http://localhost:9090/api/event"  # Substitua pelo URL correto do seu endpoint
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# Enviar a requisição POST com o JSON
try:
    response = requests.post(url, headers=headers, data=data_json)

    # Verificar a resposta
    if response.status_code == 200:
        print("Dados enviados com sucesso!")
    else:
        print(f"Erro ao enviar dados: {response.status_code}")
        print("Detalhes do erro:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro ao enviar a requisição: {e}")
