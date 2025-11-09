 Validador de Integração entre APIs (v5.0)
 Autor: Vitor Santos
 Linguagem: Python 3.x
 Versão: 5.0 — com camada antifraude simulada
 Descrição

  Aplicação em Python que realiza integração e validação entre duas APIs públicas:

 JSONPlaceholder
  Usuários

 FakeStoreAPI
  Produtos

O sistema cruza os dados, aplica validações de consistência e uma camada antifraude simulada com pontuação de risco (0–100).

 Funcionalidades

Integração entre APIs REST

Validação de dados de usuário e produto

Geração de CPF fake para simulação

Cálculo de risco antifraude baseado em:

E-mail suspeito

Categoria do produto

Valor elevado

Heurísticas simples

🔴 Risco ≥ 70 → integração bloqueada
🟢 Risco < 70 → integração aprovada

 Exemplo de uso
Digite o ID do usuário (1–10): 4
Digite o ID do produto (1–20): 7


Saída resumida:

Usuário: Patricia Lebsack | Julianne.OConner@kory.org
Produto: Mens Casual Premium Slim Fit T-Shirts
Risco: 42/100 — Integração aprovada ✅

 Como executar

1️ Instalar dependência:

pip install requests


2️ Executar o projeto:

python validador_api_v5.py

 Estrutura do Projeto
API_Trabalho/
├── validador_api_v5.py
├── README.md
├── Artigo_API_ValidatorVitor_Santos_Fernandes.docx
├── Resumo_Middleware_Servicos_Aplicacoes.docx

 Resumo

Projeto prático de validação entre APIs com análise antifraude simulada,
voltado para fins acadêmicos e demonstrações técnicas.

  Desenvolvido por Vitor Santos
