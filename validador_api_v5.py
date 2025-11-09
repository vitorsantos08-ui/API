

"""
Projeto: Integração e Validação entre APIs
Autor: Vitor Santos
Versão: 5.0 (com camada antifraude simulada)
"""

import requests
import time
import json
import logging
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime
from random import Random

# ============================
# CONFIGURAÇÕES E CONSTANTES
# ============================

USERS_API = "https://jsonplaceholder.typicode.com/users"
PRODUCTS_API = "https://fakestoreapi.com/products"

LOG_DIR = Path("logs")
RESULT_DIR = Path("resultados")
LOG_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "integracao.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Risco acima deste valor => bloqueia integração
RISK_THRESHOLD = 70

# ============================
# CORES PARA O TERMINAL
# ============================

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

# ============================
# UTILITÁRIOS DE REDE
# ============================

def fetch_api(url: str, retries: int = 3, delay: float = 1.0) -> Optional[dict]:
    """Requisição HTTP com timeout e retry."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"{Colors.YELLOW}⏳ Timeout ({attempt}/{retries}), tentando...{Colors.RESET}")
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}❌ Erro de requisição: {e}{Colors.RESET}")
            logging.error(f"Erro ao acessar {url}: {e}")
            break
    return None

def get_user(user_id: int) -> Optional[dict]:
    print(f"{Colors.CYAN}\n🔍 Consultando usuário ID={user_id}...{Colors.RESET}")
    user = fetch_api(f"{USERS_API}/{user_id}")
    if not user:
        print(f"{Colors.RED}⚠️ Usuário não encontrado.{Colors.RESET}")
    return user

def get_product(product_id: int) -> Optional[dict]:
    print(f"{Colors.CYAN}🛒 Buscando produto ID={product_id}...{Colors.RESET}")
    product = fetch_api(f"{PRODUCTS_API}/{product_id}")
    if not product:
        print(f"{Colors.RED}⚠️ Produto não encontrado.{Colors.RESET}")
    return product

# ============================
# VALIDAÇÃO DE E-MAIL E CPF
# ============================

def validar_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def gerar_cpf_fake(user_id: int) -> str:
    """Gera CPF fictício determinístico a partir do user_id (reprodutível)."""
    rng = Random(user_id)  # determinístico conforme user_id
    base = [rng.randint(0, 9) for _ in range(9)]
    soma = sum(base[i] * (10 - i) for i in range(9))
    dig1 = (soma * 10) % 11
    dig1 = 0 if dig1 == 10 else dig1
    soma = sum(base[i] * (11 - i) for i in range(9)) + dig1 * 2
    dig2 = (soma * 10) % 11
    dig2 = 0 if dig2 == 10 else dig2
    cpf = "".join(map(str, base)) + f"{dig1}{dig2}"
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# ============================
# CAMADA ANTIFRAUDE (SIMULADA)
# ============================

def category_risk(category: str) -> int:
    """Risco associado a categorias (mapeamento simples)."""
    cat = (category or "").lower()
    mapping = {
        "electronics": 30,
        "jewelery": 40,
        "men's clothing": 10,
        "women's clothing": 10,
    }
    return mapping.get(cat, 15)  # default 15

def email_risk(email: str) -> Tuple[int, str]:
    """Avalia risco do e-mail; retorna (pontuação, motivo)."""
    suspicious_domains = {"mailinator.com", "tempmail.com", "10minutemail.com", "disposablemail.com"}
    try:
        domain = email.split("@", 1)[1].lower()
    except Exception:
        return 40, "E-mail malformado"

    if domain in suspicious_domains:
        return 50, f"Domínio descartável ({domain})"
    if len(domain) > 30:
        return 10, "Domínio muito longo (suspeito)"
    return 0, "E-mail com domínio comum"

def price_risk(price: float) -> Tuple[int, str]:
    """Influência do preço na pontuação de risco."""
    if price >= 500:
        return 35, "Preço muito alto"
    if price >= 100:
        return 20, "Preço elevado"
    if price >= 50:
        return 10, "Preço moderado"
    return 0, "Preço baixo"

def cpf_risk(cpf: str) -> Tuple[int, str]:
    """Avalia o CPF gerado: regras simples (simulação)."""
    # Exemplo: CPF cujo último dígito é ímpar = um pouco mais arriscado
    last_digit = int(re.sub(r'\D', '', cpf)[-1])
    if last_digit % 2 == 1:
        return 25, "CPF simulado termina em dígito ímpar (simulado)"
    return 0, "CPF simulado com padrão aceitável"

def compute_risk_score(user: dict, product: dict) -> Tuple[int, List[str]]:
    """
    Calcula a pontuação de risco (0-100) aplicando regras:
     - base 10
     - soma: email_risk + cpf_risk + category_risk + price_risk + heurísticos
     - normalize/clamp 0-100
    Retorna (score, motivos)
    """
    motivos: List[str] = []
    score = 10  # base

    # Email
    email = user.get("email", "")
    if not validar_email(email):
        motivos.append("E-mail inválido/formatado incorretamente")
        score += 40
    else:
        erisk, emot = email_risk(email)
        if erisk:
            motivos.append(emot)
        score += erisk

    # CPF (simulado)
    cpf = gerar_cpf_fake(user.get("id", 0))
    crisk, cmot = cpf_risk(cpf)
    if crisk:
        motivos.append(cmot)
    score += crisk

    # Categoria do produto
    category = product.get("category", "")
    cat_r = category_risk(category)
    if cat_r:
        motivos.append(f"Categoria: {category} (risco {cat_r})")
    score += cat_r

    # Preço
    price = float(product.get("price", 0) or 0)
    pr_r, pr_mot = price_risk(price)
    if pr_r:
        motivos.append(pr_mot)
    score += pr_r

    # Heurísticos adicionais (simulados)
    # - Se nome do usuário contém muitos caracteres especiais -> acrescenta risco
    name = user.get("name", "")
    if len(re.findall(r'[^A-Za-zÀ-ÿ \-\.]', name)) > 0:
        motivos.append("Nome do usuário contém caracteres incomuns")
        score += 8

    # - Se e-mail e nome não compartilham domínio/parte reconhecível -> pequeno risco
    if "@" in email:
        local = email.split("@")[0]
        if local.split(".")[0].lower() not in name.replace(".", " ").lower():
            motivos.append("Nome e parte local do e-mail não coincidem (heurística)")
            score += 5

    # Clamp
    final = max(0, min(100, int(score)))
    if final != score:
        motivos.append("Pontuação ajustada para limite 0-100")

    return final, motivos

# ============================
# SALVAMENTO E LOGS
# ============================

def save_result(user: dict, product: dict, risk: int, reasons: List[str], blocked: bool):
    """Salva resultado incluindo pontuação antifraude e motivo(s)."""
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "city": user["address"]["city"]
        },
        "product": {
            "id": product["id"],
            "title": product["title"],
            "price": product["price"],
            "category": product.get("category", "")
        },
        "antifraud": {
            "score": risk,
            "blocked": blocked,
            "reasons": reasons
        }
    }

    filename = RESULT_DIR / f"user{user['id']}_product{product['id']}_result.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logging.info(f"Resultado salvo: {filename} | risk={risk} | blocked={blocked}")

# ============================
# VALIDAÇÃO INTEGRADA
# ============================

def validate_integration(user_id: int, product_id: int):
    """Fluxo principal com antifraude."""
    user = get_user(user_id)
    if not user:
        logging.warning(f"Usuário {user_id} não encontrado.")
        return

    product = get_product(product_id)
    if not product:
        logging.warning(f"Produto {product_id} não encontrado.")
        return

    # Calcula risco
    risk, reasons = compute_risk_score(user, product)
    blocked = risk >= RISK_THRESHOLD

    # Exibe resumo
    print(f"\n{Colors.BOLD}{Colors.GREEN}👤 Usuário:{Colors.RESET} {user['name']} | {user['email']}")
    print(f"{Colors.CYAN}🏙️ Cidade:{Colors.RESET} {user['address']['city']}")
    print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Produto:{Colors.RESET} {product['title']}")
    print(f"{Colors.CYAN}💲 Preço:{Colors.RESET} R${product['price']} | Categoria: {product.get('category','-')}")
    print(f"\n{Colors.YELLOW}🔎 Pontuação de risco: {risk}/100{Colors.RESET}")

    if reasons:
        print(f"{Colors.YELLOW}📋 Motivos: {', '.join(reasons)}{Colors.RESET}")

    if blocked:
        print(f"{Colors.RED}\n⛔ Integração BLOQUEADA — risco acima do limiar ({RISK_THRESHOLD}).{Colors.RESET}")
        logging.warning(f"Integração bloqueada — user={user_id} product={product_id} risk={risk}")
    else:
        print(f"{Colors.GREEN}\n🎉 Integração autorizada — prosseguindo com salvamento.{Colors.RESET}")
        logging.info(f"Integração autorizada — user={user_id} product={product_id} risk={risk}")

    # Salva resultado com detalhe de risco (mesmo quando bloqueado)
    save_result(user, product, risk, reasons, blocked)

# ============================
# UI / MENU
# ============================

def show_header():
    print("=" * 80)
    print(f"{Colors.BOLD}{Colors.CYAN}🤝 SISTEMA DE VALIDAÇÃO ENTRE APIs (v5.0) — +ANTIFRAUDE{Colors.RESET}")
    print("=" * 80)
    print("🔹 Usuários → https://jsonplaceholder.typicode.com/users")
    print("🔹 Produtos → https://fakestoreapi.com/products")
    print(f"🔹 Limiar de bloqueio (RISK_THRESHOLD) = {RISK_THRESHOLD}")
    print("=" * 80)

def main():
    show_header()
    while True:
        try:
            user_id = int(input(f"\nDigite o ID do usuário (1–10): "))
            product_id = int(input("Digite o ID do produto (1–20): "))
            validate_integration(user_id, product_id)
        except ValueError:
            print(f"{Colors.YELLOW}⚠️ Digite apenas números válidos!{Colors.RESET}")
            continue

        again = input(f"\nDeseja validar outro par? (s/n): ").lower().strip()
        if again != "s":
            print(f"{Colors.CYAN}\n👋 Encerrando o programa... até logo!{Colors.RESET}")
            break

if __name__ == "__main__":
    main()
