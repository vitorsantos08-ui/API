# 🤝 Validador de Integração entre APIs (v5.0)

**Autor:** Vitor Santos | **Linguagem:** Python 3.x  

Aplicação demonstrativa que integra duas **APIs públicas** — [JSONPlaceholder](https://jsonplaceholder.typicode.com/users) (usuários) e [FakeStoreAPI](https://fakestoreapi.com/products) (produtos) — aplicando **validações de consistência** e uma **camada antifraude simulada** com pontuação de risco de 0 a 100.

> ⚠️ Projeto **acadêmico e fictício**, sem uso de dados reais.  
> Criado para fins de **demonstração e aprendizado sobre integração entre APIs REST.**

---

### 🧠 Lógica antifraude
- E-mail suspeito  
- Categoria e preço do produto  
- CPF fake gerado dinamicamente  
- Heurísticas simples (nome e e-mail)  

🔴 **Risco ≥ 70** → integração bloqueada  
🟢 **Risco < 70** → integração aprovada  

---

### 🚀 Como executar
```bash
pip install requests
python validador_api_v5.py
