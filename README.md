# 💈 Barbearia Premium - Gerenciador de Agendamentos

Este é um projeto completo de um **Gerenciador Exclusivo de Horários e Clientes para Barbearia**, desenvolvido com um visual premium (Obsidian & Gold) e estruturado com tecnologias modernas de mercado.

A aplicação divide-se em:
1. **Back-end**: API REST em **Python (FastAPI)** com **SQLAlchemy** (ORM).
2. **Front-end**: Interface web moderna e responsiva em **React** (Vite).
3. **Banco de Dados**: Suporta tanto **SQLite** (local para desenvolvimento leve) quanto **PostgreSQL** (para produção ou execução via Docker).

---

## 🏗️ Arquitetura e Estrutura do Projeto

O projeto é organizado de forma modular para separar as responsabilidades de negócio do front-end e do back-end:

```
Barbearia_Project/
├── backend/                  # Código do servidor FastAPI
│   ├── app/                  # Módulos principais da API
│   │   ├── routes/           # Endpoints HTTP (barbers, clients, appointments)
│   │   ├── services/         # Regras de negócio (ex: validação de conflito de horários)
│   │   ├── schemas/          # Modelos de validação de dados Pydantic
│   │   ├── models.py         # Entidades do SQLAlchemy (Banco de Dados)
│   │   ├── database.py       # Configuração da conexão de banco
│   │   └── main.py           # Inicializador do app, CORS e middlewares
│   ├── tests/                # Testes automatizados com pytest
│   └── pyproject.toml        # Dependências gerenciadas pelo 'uv'
│
├── frontend/                 # Código do cliente React
│   ├── src/
│   │   ├── App.jsx           # Tela unificada (Dashboard, formulários e listagem)
│   │   ├── index.css         # Design System da marca (Obsidian & Gold, animações)
│   │   └── main.jsx          # Renderizador do React
│   ├── Dockerfile            # Construção da imagem Docker do frontend
│   └── package.json          # Dependências npm
│
├── docker-compose.yml        # Orquestração local de serviços
└── README.md                 # Documentação do projeto (este arquivo)
```

---

## ⚡ Como Executar Localmente

### Opção 1: Sem Docker (Usando SQLite local)

Esta opção é ideal para desenvolvimento rápido e depuração, pois não requer containers rodando na máquina.

#### 1. Pré-requisitos
- **Python 3.11 ou superior** (com a ferramenta `uv` instalada para gerenciar dependências de forma rápida).
- **Node.js 18 ou superior** (com `npm`).

#### 2. Executando o Back-end
Abra um terminal na pasta `backend/`:
```bash
# Sincronizar dependências com uv
uv sync

# Executar a API em modo de recarregamento automático (reload)
uv run uvicorn app.main:app --reload
```
A API estará acessível em: `http://localhost:8000`. O arquivo SQLite `barbearia.db` será criado automaticamente na pasta `backend/`.

#### 3. Executando o Front-end
Abra outro terminal na pasta `frontend/`:
```bash
# Instalar as dependências do npm
npm install

# Iniciar o servidor de desenvolvimento Vite
npm run dev
```
O frontend estará acessível em: `http://localhost:5173`.

---

### Opção 2: Com Docker Compose (Usando PostgreSQL)

Esta opção inicializa toda a stack (PostgreSQL + API backend + frontend React) idêntica ao ambiente de produção.

#### 1. Pré-requisitos
- **Docker** e **Docker Compose** instalados e em execução.

#### 2. Configurando o Ambiente
Crie um arquivo `.env` na raiz do projeto (copie a partir do `.env.example`):
```env
POSTGRES_USER=barbearia
POSTGRES_PASSWORD=senha123
POSTGRES_DB=barbearia_db
DATABASE_URL=postgresql://barbearia:senha123@db:5432/barbearia_db
```

#### 3. Iniciando os Containers
Na raiz do projeto, execute o comando:
```bash
docker-compose up --build
```
Isso irá:
1. Criar e subir o banco **PostgreSQL** na porta `5432`.
2. Compilar e rodar a imagem do **backend** na porta `8000`.
3. Compilar a imagem do **frontend** usando Nginx e rodar na porta `5173`.

Basta acessar `http://localhost:5173` no seu navegador!

---

## 🧪 Testes Automatizados (Back-end)

A suíte de testes cobre as regras críticas de negócio (como a validação para que um barbeiro não receba dois agendamentos no mesmo horário e respostas de erros 404 e 409).

Para executar os testes com a geração de relatório de cobertura de código (coverage):

No terminal, acesse a pasta `backend/` e execute:
```bash
uv run python -m pytest --cov=app
```

Atualmente, o projeto conta com **96% de cobertura de testes** em todo o domínio de negócio!

---

## 🛠️ Detalhes das Regras de Negócio e Funcionalidades

### Validações Implementadas no Agendamento:
1. **Existência do Barbeiro**: Não é possível agendar com um ID de barbeiro inválido (retorna HTTP 404).
2. **Existência do Cliente**: Não é possível associar a um cliente inexistente (retorna HTTP 404).
3. **Conflito de Horário**: O sistema impede agendamentos simultâneos para o mesmo barbeiro (retorna HTTP 409 - Conflict).

### Observabilidade e Logs:
- Cada requisição HTTP no backend é interceptada por um middleware que gera um `Request ID` único (UUID).
- O tempo total de execução da requisição em milissegundos é calculado e logado no console com a tag `[Request ID]`.
- O cabeçalho `X-Request-ID` é exposto no CORS para que o frontend ou logs de rede possam rastrear a origem da requisição.

---

## Day 13 — End-to-End Debug Checklist

Esta etapa garante que o sistema funcione ponta a ponta e seja mais fácil de diagnosticar quando algo falhar.

### O que foi reforçado no projeto
- **CORS configurável por variável de ambiente** via `CORS_ORIGINS`, evitando erro de bloqueio ao trocar de domínio.
- **`/health` endpoint** para checagem rápida de disponibilidade da API.
- **`X-Request-ID`** retornado em toda resposta para rastrear uma requisição no log do backend.
- **Frontend com API configurável** por `VITE_API_URL`, permitindo apontar para local, Render ou outro ambiente.
- **Tratamento de erro no carregamento inicial** do dashboard para respostas HTTP não-200.

### Fluxo de debug recomendado
1. Testar API:
   - `GET /health`
   - `GET /barbers`, `GET /clients`, `GET /appointments`
2. Criar dados no frontend:
   - Cadastrar barbeiro
   - Cadastrar cliente
   - Criar agendamento
3. Validar regra de conflito:
   - Tentar agendar mesmo barbeiro no mesmo horário
   - Confirmar retorno `409`
4. Cancelar agendamento e validar remoção da agenda.
5. Quando houver erro, copiar o `X-Request-ID` da aba de rede e localizar no log da API.

---

## Day 14 — Deploy (Neon + Render + Vercel)

Arquitetura de produção sugerida:
- **Neon**: banco PostgreSQL gerenciado.
- **Render**: hospedagem da API FastAPI.
- **Vercel**: hospedagem do frontend React.

### 1) Banco no Neon
1. Crie um projeto no [Neon](https://neon.tech/).
2. Copie a connection string PostgreSQL (com SSL).
3. Guarde como `DATABASE_URL` para usar no Render.

Exemplo:
`postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require`

### 2) Backend no Render
1. Suba o repositório no GitHub.
2. No Render, crie um novo **Web Service** apontando para este repositório.
3. O projeto inclui `render.yaml` com:
   - `rootDir: backend`
   - build: `pip install uv && uv sync --frozen`
   - start: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Defina variáveis:
   - `DATABASE_URL` = string do Neon
   - `CORS_ORIGINS` = URL do frontend Vercel (e URLs locais, se quiser)
5. Deploy e valide:
   - `https://SEU-BACKEND.onrender.com/health`

### 3) Frontend no Vercel
1. Importe o mesmo repositório no [Vercel](https://vercel.com/).
2. Configure **Root Directory** como `frontend`.
3. Adicione variável:
   - `VITE_API_URL=https://SEU-BACKEND.onrender.com`
4. Faça o deploy.
5. O arquivo `frontend/vercel.json` já contém rewrite para SPA.

### 4) Ajuste final de CORS
No Render, garanta:
`CORS_ORIGINS=https://SEU-FRONTEND.vercel.app,http://localhost:5173`

---

## Roadmap (Days 10-14) — Status

- ✅ **Days 10-11**: Testes `pytest` com regras de negócio (404, 409, CRUD principal).
- ✅ **Day 12**: Logging com middleware de request + `X-Request-ID`.
- ✅ **Day 13**: Hardening de debug fim-a-fim (`/health`, CORS por env, frontend com `VITE_API_URL`).
- ✅ **Day 14**: Base de deploy pronta com `render.yaml`, `frontend/vercel.json` e guia Neon/Render/Vercel.
