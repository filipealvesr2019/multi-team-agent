
# -*- coding: utf-8 -*-
# SiteCloner v1.0 - Uma ferramenta para clonagem visual de websites para uso offline.
# Criado como parte de um projeto de aprendizado guiado.

import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# --- Funções Auxiliares ---

def sanitize_url_to_foldername(url):
    """Cria um nome de pasta seguro a partir de uma URL."""
    try:
        domain = urlparse(url).netloc
        return re.sub(r'[\\/*?:"<>|]', "", domain)
    except Exception:
        return "cloned_site"

def create_directory(path):
    """Cria um diretório se ele não existir."""
    os.makedirs(path, exist_ok=True)

def download_file(session, url, save_path):
    """Baixa um arquivo, retornando o status HTTP."""
    try:
        response = session.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"  [AVISO] Falha na conexão ao baixar {url}: {e}")
        return None

def get_filename_from_url(url):
    """Extrai um nome de arquivo de uma URL."""
    path = urlparse(url).path
    return os.path.basename(path) if path else "index.html"

def parse_font_family_from_filename(filename):
    """Extrai um nome de família de fonte de um nome de arquivo. Ex: 'UncutSans-Bold.ttf' -> 'Uncut Sans'"""
    try:
        # Remove a extensão e possíveis sufixos de peso
        base_name = os.path.splitext(filename)[0]
        # Remove variações comuns como -Bold, -Regular, etc.
        family_name = re.sub(r'-(Bold|Regular|Medium|Light|Semibold|Italic|Black)$', '', base_name, flags=re.IGNORECASE)
        # Converte CamelCase para espaços. Ex: 'UncutSans' -> 'Uncut Sans'
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', family_name)
    except Exception:
        return None

def parse_css_and_download_assets(session, css_content, css_url, project_folder, failed_font_families):
    """Analisa CSS, baixa ativos e lida com falhas de fontes."""
    modified_css = css_content
    # Regex para encontrar url() com ou sem aspas
    font_urls = re.findall(r'url\((["\']?)(.*?)\1\)', css_content)

    for quote, original_font_path in font_urls:
        if original_font_path.startswith('data:'):
            continue

        absolute_font_url = urljoin(css_url, original_font_path)
        font_filename = get_filename_from_url(absolute_font_url)
        if not font_filename: continue

        font_save_path = os.path.join(project_folder, 'fonts', font_filename)
        
        status_code = download_file(session, absolute_font_url, font_save_path)
        
        if status_code == 200:
            # Sucesso: reescreve o caminho para o arquivo local
            new_local_path = f"../fonts/{font_filename}"
            modified_css = modified_css.replace(original_font_path, new_local_path)
        elif status_code == 404:
            # Falha: Adiciona à lista de fallback do Google Fonts
            print(f"  [FALLBACK] Fonte não encontrada (404): {absolute_font_url}. Tentando Google Fonts.")
            family_name = parse_font_family_from_filename(font_filename)
            if family_name:
                failed_font_families.add(family_name)

    return modified_css

# --- Função Principal ---

def main():
    print("==================================================")
    print("          SiteCloner v1.0 - By MentorTHM          ")
    print("==================================================")
    
    BASE_URL = input("Por favor, insira a URL do site a ser clonado: ")
    project_folder = sanitize_url_to_foldername(BASE_URL)
    
    print(f"\n[+] Iniciando clonagem de '{BASE_URL}'")
    print(f"[+] Arquivos serão salvos em: '{project_folder}/'")
    create_directory(project_folder)

    # --- FASE 1: Scraping com Selenium ---
    print("\n--- [FASE 1/3] Obtendo HTML dinâmico com Selenium ---")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3") # Suprime logs desnecessários
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(BASE_URL)
        time.sleep(2) # Espera inicial
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height
        html_content = driver.page_source
        driver.quit()
        print(" -> HTML obtido com sucesso.")
    except Exception as e:
        print(f"[ERRO FATAL] Falha ao executar o Selenium. Verifique a instalação do Chrome/WebDriver. Erro: {e}")
        return

    # --- FASE 2: Download de Ativos ---
    print("\n--- [FASE 2/3] Baixando e organizando ativos ---")
    soup = BeautifulSoup(html_content, 'lxml')
    asset_folders = ['css', 'js', 'img', 'fonts']
    for folder in asset_folders:
        create_directory(os.path.join(project_folder, folder))

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    failed_font_families = set()

    # Processar CSS
    for link in soup.find_all('link', rel='stylesheet'):
        if link.has_attr('href') and not link['href'].startswith('data:'):
            css_url = urljoin(BASE_URL, link['href'])
            css_filename = get_filename_from_url(css_url)
            if not css_filename: continue
            css_save_path = os.path.join(project_folder, 'css', css_filename)
            
            if download_file(session, css_url, css_save_path) == 200:
                with open(css_save_path, 'r+', encoding='utf-8') as f:
                    css_content = f.read()
                    modified_css = parse_css_and_download_assets(session, css_content, css_url, project_folder, failed_font_families)
                    f.seek(0)
                    f.write(modified_css)
                    f.truncate()
                link['href'] = f"css/{css_filename}"
    print(" -> Arquivos CSS e fontes processados.")

    # Processar Imagens e JS
    for tag in soup.find_all(['img', 'script'], src=True):
        if tag['src'].startswith('data:'):
            continue
        asset_url = urljoin(BASE_URL, tag['src'])
        asset_filename = get_filename_from_url(asset_url)
        if not asset_filename: continue
        
        folder = 'js' if tag.name == 'script' else 'img'
        asset_save_path = os.path.join(project_folder, folder, asset_filename)
        download_file(session, asset_url, asset_save_path)
        tag['src'] = f"{folder}/{asset_filename}"
    print(" -> Arquivos de Imagem e JavaScript processados.")

    # --- FASE 3: Finalização e Correções ---
    print("\n--- [FASE 3/3] Aplicando correções finais e salvando ---")

    # Fallback para Google Fonts
    if failed_font_families:
        print(f" -> Aplicando fallback para {len(failed_font_families)} família(s) de fontes via Google Fonts...")
        for family in failed_font_families:
            google_font_url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}&display=swap"
            new_link_tag = soup.new_tag('link', rel='stylesheet', href=google_font_url)
            soup.head.append(new_link_tag)
    
    # Injetar CSS para forçar rolagem
    scroll_fix_style = soup.new_tag('style')
    scroll_fix_style.string = "html, body { overflow: visible !important; height: auto !important; position: static !important; }"
    soup.head.append(scroll_fix_style)
    print(" -> Injetado CSS para garantir a funcionalidade da barra de rolagem.")
    
    # Remover todos os scripts restantes para evitar problemas de interatividade
    for s in soup.find_all('script'):
        s.decompose()
    print(" -> Scripts remanescentes removidos para garantir estabilidade visual.")

    # Salvar o arquivo final
    final_html_path = os.path.join(project_folder, "CLONE.html")
    with open(final_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("\n==============================================")
    print("   PROCESSO DE CLONAGEM CONCLUÍDO!   ")
    print(f"   Arquivo final: {final_html_path}   ")
    print("==============================================")


if __name__ == "__main__":
    main()