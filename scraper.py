import csv
import requests
from bs4 import BeautifulSoup

# 1. URL direcionada para busca de smartphones no Buscapé (não bloqueia requisições)
url = 'https://www.buscape.com.br/search?q=smartphone'

# Simula um navegador real para evitar bloqueios
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Iniciando a busca de produtos no Buscapé...")
try:
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Cria e abre o arquivo CSV
        with open('analise_precos.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            escritor.writerow(['Produto', 'Preço (R$)'])
            
            # 3. Encontra os containers dos produtos (os cards do Buscapé)
            produtos = soup.find_all(class_=lambda x: x and 'Hits_ProductCard' in x)
            
            contador = 0
            for produto in produtos:
                try:
                    # 4. Extrai o nome e o preço usando os identificadores estáveis
                    nome_elemento = produto.find(attrs={"data-testid": "product-card::name"}) or produto.find('h2')
                    preco_elemento = produto.find(attrs={"data-testid": "product-card::price"}) or produto.find('strong')
                    
                    if nome_elemento and preco_elemento:
                        nome = nome_elemento.text.strip()
                        # Remove o "R$" e espaços para deixar o preço limpo
                        preco = preco_elemento.text.replace('R$', '').strip()
                        
                        escritor.writerow([nome, preco])
                        print(f'Produto: {nome} | Preço: R$ {preco}')
                        contador += 1
                        
                except Exception:
                    continue

        if contador > 0:
            print(f'\nRaspagem concluída! {contador} dados salvos com sucesso em "analise_precos.csv".')
        else:
            print('\nNenhum produto foi encontrado. As classes do site podem ter mudado.')
    else:
        print(f'Falha na requisição. Status Code: {response.status_code}')
except Exception as e:
    print(f'Erro de conexão ao tentar acessar o site: {e}')