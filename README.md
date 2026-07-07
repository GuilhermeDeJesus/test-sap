# Cloud Log Access - Teste Fullstack (Base)

Projeto base para o teste técnico com foco em segurança, backend em Python e arquitetura em camadas.

## Stack (MVP atual)
- Backend: FastAPI + SQLAlchemy + JWT + Argon2
- Frontend: React + Vite + React Router + Zustand + Axios
- Cloud provider: interface desacoplada com implementação AWS S3 e fallback local
- Banco: SQLite
- Testes: Pytest
- Container: Docker Compose

## Endpoints
- `POST /auth/login`
- `GET /logs` (qualquer usuário autenticado)
- `GET /logs/{file_name}` (somente `admin`)
- `POST /logs/{file_name}/presigned` (somente `admin`)
- `GET /health`

## User Journey (UI)
1. Usuário acessa `/login`.
2. Usuário realiza autenticação (`admin` ou `viewer`).
3. Aplicação salva sessão em estado global persistido (token, role, username).
4. Route guard libera acesso para `/logs` somente para usuários autenticados.
5. Usuário visualiza lista de logs.
6. `admin` pode baixar arquivo e gerar link temporário.
7. `viewer` consegue listar, mas recebe bloqueio para download/presigned.

### Screenshots
- Login: [docs/screenshots/login.png](docs/screenshots/login.png)
- Logs (admin): [docs/screenshots/logs-admin.png](docs/screenshots/logs-admin.png)

## Usuários seeded
- `admin` / `123456` (role `admin`)
- `viewer` / `123456` (role `viewer`)

## Executar localmente
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Executar testes
```bash
cd backend
pytest -q
```

Saída esperada:
```text
6 passed
```

## Executar com Docker
```bash
docker compose up --build
```

Serviços:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Estrutura
- `backend/app/api`: rotas e dependências
- `backend/app/domain`: regras de negócio
- `backend/app/infrastructure`: banco, repositórios e providers cloud
- `backend/app/core`: config e segurança
- `backend/tests`: testes automatizados
- `frontend/src/pages`: telas de login e logs
- `frontend/src/store`: estado global de autenticação
- `frontend/src/router`: proteção de rotas

## Sample API Requests/Responses
### Login
```bash
curl -X POST http://localhost:8000/auth/login \
	-H "Content-Type: application/json" \
	-d '{"username":"admin","password":"123456"}'
```

```json
{
	"access_token": "eyJhbGciOi...",
	"token_type": "bearer"
}
```

### List Logs
```bash
curl -X GET http://localhost:8000/logs \
	-H "Authorization: Bearer <TOKEN>"
```

```json
[
	{ "name": "access.log", "size": 79 },
	{ "name": "nginx.log", "size": 58 }
]
```

### Download Log (admin)
```bash
curl -X GET http://localhost:8000/logs/access.log \
	-H "Authorization: Bearer <TOKEN>" \
	-o access.log
```

### Temporary Access Link (admin)
```bash
curl -X POST http://localhost:8000/logs/access.log/presigned \
	-H "Authorization: Bearer <TOKEN>"
```

```json
{
	"url": "https://s3.amazonaws.com/..."
}
```

## Design Decisions
- Arquitetura em camadas separando API, domínio e infraestrutura para manter regras de negócio desacopladas do framework e do provedor cloud.
- Interface de storage (`CloudStorageProvider`) para permitir troca de provider sem alteração de regras centrais.
- JWT com role embutida para simplificar autorização RBAC (`admin` e `viewer`) no challenge.
- Fallback local de logs para execução sem credenciais AWS, mantendo o mesmo contrato de API.
- Frontend com Zustand para sessão persistida e React Router para proteção de rotas.

## Security Checklist
- Hash de senha com Argon2.
- Tokens JWT para autenticação.
- RBAC em endpoints sensíveis (`download` e `presigned`).
- Rate limiting de login (5/min por IP).
- Headers de segurança (`X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, etc).
- Segredos em variáveis de ambiente (`.env`).
- Tratamento centralizado de exceções para evitar vazamento de stacktrace.

## Deliverable Checklist
- Backend BFF com endpoints obrigatórios: concluído.
- Frontend com Login + Logs + download: concluído.
- UI de link temporário (bônus): concluído.
- Docker Compose para execução local: concluído.
- README com setup, requests/responses e decisões: concluído.
- IaC (Terraform): pendente (bônus).
- CI workflow: pendente (bônus).

## Próximos passos sugeridos
- Migrar rate limiter para Redis em ambiente distribuído
- Adicionar trilha de auditoria para downloads (IP, user-agent, request-id)
- Incluir CI (pytest + lint)
# test-sap
