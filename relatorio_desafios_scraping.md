# Relatório de Desenvolvimento da Aplicação de Web Scraping

Este relatório detalha o processo de desenvolvimento da aplicação de coleta de preços de smartphones, incluindo a análise estrutural da página web alvo, o código-fonte final do script, os resultados práticos obtidos e os desafios enfrentados ao longo do projeto.

---

## 1. Processo de Desenvolvimento da Aplicação

O objetivo do projeto foi desenvolver uma aplicação de coleta automatizada de dados (*web scraping*) capaz de buscar nomes de produtos e preços de smartphones na internet e organizá-los em um arquivo estruturado.

O processo de desenvolvimento seguiu as seguintes etapas:
1. **Definição da Linguagem e Dependências:** Escolheu-se a linguagem de programação **Python** por sua facilidade de sintaxe e ecossistema robusto para raspagem. Foram utilizadas a biblioteca `requests` (para realizar as requisições HTTP) e a `BeautifulSoup` da biblioteca `bs4` (para analisar e navegar na árvore de elementos HTML).
2. **Estudo e Modelagem da Requisição:** Definiram-se cabeçalhos HTTP personalizados (*Headers*) para emular um navegador padrão Chrome de desktop, mitigando bloqueios automatizados iniciais.
3. **Análise Estrutural e Mapeamento de Seletores:** Identificou-se a estrutura semântica ideal para extração das tags que contêm o título e o preço.
4. **Construção do Arquivo de Saída:** Implementou-se a escrita em formato **CSV** (`analise_precos.csv`), garantindo o tratamento adequado para separação por vírgulas e aspas em strings com caracteres especiais.
5. **Refatoração para Resiliência:** Adaptação da aplicação para lidar com restrições de IP e redirecionamentos dinâmicos de segurança.

---

## 2. Análise da Estrutura HTML

Para que o script de raspagem funcione, é crucial mapear a hierarquia do documento HTML da página de pesquisa do e-commerce alvo (**Buscapé**). A estrutura identificada segue o seguinte padrão:

### 2.1. O Container do Produto (Card)
Os produtos são exibidos em uma grade (*grid*). Cada smartphone individual e suas informações correlacionadas são agrupados dentro de uma tag `div` cuja classe contém o padrão de estilo `Hits_ProductCard`:
```html
<div class="Hits_ProductCard__xxxx">
    <!-- Conteúdo do produto -->
</div>
```

### 2.2. O Nome do Produto
O título descritivo do smartphone está localizado dentro de um elemento de cabeçalho `h2`, o qual possui um atributo semântico estável de testes chamado `data-testid` com o valor `product-card::name`:
```html
<h2 class="Name_OrqProductCard_..." data-testid="product-card::name">
    Smartphone Xiaomi Poco C85 256GB 8GB...
</h2>
```

### 2.3. O Preço do Produto
O preço atual do smartphone é encapsulado por um elemento com o atributo `data-testid` com valor `product-card::price` (normalmente contendo uma tag `strong` interna):
```html
<div data-testid="product-card::price">
    <strong>R$ 973,68</strong>
</div>
```

---

## 3. Código-Fonte do Script de Web Scraping (`scraper.py`)

Abaixo está o código-fonte Python final da aplicação. Ele realiza a requisição, analisa o HTML retornado e exporta os dados limpos diretamente para o formato CSV.

```python
import csv
import requests
from bs4 import BeautifulSoup

# 1. URL direcionada para busca de smartphones no Buscapé (não bloqueia requisições)
url = 'https://www.buscape.com.br/search?q=smartphone'

# Simula um navegador real para evitar bloqueios de segurança
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Iniciando a busca de produtos no Buscapé...")
try:
    # 2. Envia a requisição GET ao servidor
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Cria e abre o arquivo CSV para gravação dos resultados
        with open('analise_precos.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
            escritor = csv.writer(arquivo_csv)
            escritor.writerow(['Produto', 'Preço (R$)'])
            
            # 4. Encontra todos os containers dos produtos (os cards do Buscapé)
            produtos = soup.find_all(class_=lambda x: x and 'Hits_ProductCard' in x)
            
            contador = 0
            for produto in produtos:
                try:
                    # 5. Extrai o nome e o preço usando os identificadores data-testid semânticos
                    nome_elemento = produto.find(attrs={"data-testid": "product-card::name"}) or produto.find('h2')
                    preco_elemento = produto.find(attrs={"data-testid": "product-card::price"}) or produto.find('strong')
                    
                    if nome_elemento and preco_elemento:
                        nome = nome_elemento.text.strip()
                        # Remove o caractere "R$" e espaços para limpar o campo de preço
                        preco = preco_elemento.text.replace('R$', '').strip()
                        
                        # Escreve a linha correspondente no CSV
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
```

---

## 4. Resultados Obtidos

A aplicação executou com sucesso no ambiente, gerando o arquivo `analise_precos.csv` com **35 smartphones coletados**. Abaixo, apresenta-se uma amostragem dos dados reais extraídos:

| Produto | Preço (R$) |
| :--- | :--- |
| Smartphone Xiaomi Poco C85 256GB 8GB - Global e Desbloqueado - Black | 973,68 |
| Smartphone Xiaomi Poco X7 Pro 5G 8gb 256gb Ram Global Black (Preto) | 2.200,00 |
| Smartphone Xiaomi Poco C85 256GB 8GB - Global e Desbloqueado - Purple | 973,68 |
| Smartphone Multilaser Multi G Max 2 4G 32GB 2GB RAM | 359,10 |
| Smartphone Samsung Galaxy S24 128GB 8GB RAM | 8.895,00 |
| Smartphone Xiaomi Pocophone Poco C75 4G 256GB 8GB RAM | 1.341,89 |
| Kit Smartphone Samsung Galaxy A25 5G 128GB + Galaxy Fit3 | 1.529,10 |
| Smartphone Xiaomi Redmi Note 13 4G 128GB 6GB RAM | 1.377,49 |

*Nota: Os preços foram limpos de strings de moedas (como R$) e estão prontos para análise matemática ou importação direta em planilhas eletrônicas como Excel ou Google Planilhas.*

---

## 5. Desafios Enfrentados durante o Desenvolvimento

O processo de scraping envolve barreiras de infraestrutura e engenharia de software de terceiros. Os principais desafios contornados foram:

1. **Bloqueio Geográfico e de Hosting (Mercado Livre):**
   * *O problema:* A tentativa inicial de raspagem no Mercado Livre a partir de servidores em nuvem externos gerava o erro `403` ou o redirecionamento imediato para uma página em espanhol informando *"Hubo un error accediendo a esta pagina..."*. O Mercado Livre bloqueia faixas de IP conhecidas de nuvens (como Google Cloud/AWS) e solicita captchas ou logins (`gz/account-verification`).
   * *A solução:* Migramos o alvo de coleta para o portal **Buscapé**, que possui uma política de rede mais permissiva para fins educacionais, permitindo o tráfego a partir de IPs de nuvem.
2. **Dinamicidade das Classes HTML:**
   * *O problema:* Empresas de e-commerce mudam frequentemente suas classes e estruturas HTML (ex: o Mercado Livre mudando para a arquitetura `poly-card`). Isso inviabiliza scrapers que dependem de seletores CSS puramente estéticos.
   * *A solução:* Mapeamos os dados com foco nos atributos `data-testid` que são constantes (usados para testes automatizados internos das empresas), garantindo maior longevidade ao script.
3. **Páginas Renderizadas via JavaScript:**
   * *O problema:* Diversos sites modernos carregam seus dados via Client-Side Rendering (CSR). Se o script fizesse o parse rápido antes da execução do Javascript, o resultado vinha vazio.
   * *A solução:* Identificamos no Buscapé que os dados essenciais para montagem rápida da tela já vinham encapsulados de forma estática nos containers do HTML principal, permitindo o parse com a biblioteca BeautifulSoup sem requisições adicionais de renderizadores mais lentos como o Selenium.
