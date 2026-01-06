# ⏱️ Ponto Salinha (Discord Bot Async)

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Discord.py](https://img.shields.io/badge/Discord.py-2.0%2B-5865F2)
![Database](https://img.shields.io/badge/Database-Async_SQLite-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![License](https://img.shields.io/badge/License-MIT-yellow)

O **Ponto Salinha** é um bot de ponto eletrônico para Discord premium, projetado para ser robusto,
performático e fácil de implantar. Esta versão utiliza uma arquitetura modular baseada em **Cogs** e
operações de banco de dados **assíncronas** com `aiosqlite`.

## 📋 Sobre o Projeto

Ideal para equipes que precisam monitorar horas de atividade sem a complexidade de serviços
externos. Com o banco de dados SQLite local, você tem total controle sobre seus dados com latência
zero.

### ✨ Diferenciais desta Versão

- **Arquitetura Modular (Cogs)**: Código organizado por funcionalidades (Admin, Ponto, Ranking,
  Relatórios).
- **Operações Não-Bloqueantes**: Utiliza `aiosqlite` para garantir que o bot nunca trave durante
  consultas ao banco.
- **Interface Premium**: Feedback visual aprimorado com Embeds modernos e intuitivos.
- **Pronto para Docker**: Deploy simplificado com Docker e Docker Compose (com Healthchecks).
- **Gestão de Ambiente**: Configurações seguras via arquivo `.env`.

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.11 ou superior.
- [Docker](https://www.docker.com/) (opcional, recomendado para VPS).

### Instalação Manual

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/seu-usuario/ponto-salinha.git
   cd ponto-salinha
   ```

2. **Configure o ambiente**:

   ```bash
   cp .env.example .env
   # Edite o .env e insira suas configurações
   ```

   **Variáveis Obrigatórias no .env**:

   - `DISCORD_TOKEN`: Seu token do bot (Pegue no
     [Developer Portal](https://discord.com/developers/applications)).
   - `DATABASE_PATH`: Caminho do banco (ex: `ponto.db` ou `/app/data/ponto.db`).

3. **Instale as dependências**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   pip install -r requirements.txt
   ```

4. **Execute o Bot**:

   ```bash
   python src/main.py
   ```

### Instalação via Docker (Recomendado)

```bash
docker-compose up -d --build
```

O container irá iniciar com healthchecks e persistência de dados automática.

## 🎮 Como Usar

Utilize os **Slash Commands** (`/`) no seu servidor.

| Comando         | Descrição                                             | Permissão     |
| :-------------- | :---------------------------------------------------- | :------------ |
| `/ponto`        | Registra entrada ou saída com feedback em tempo real. | Todos         |
| `/ranking`      | Exibe o ranking de horas (Hoje, Semana, Mês, Total).  | Todos         |
| `/relatorio`    | Gera um Excel detalhado do histórico de um usuário.   | Próprio/Admin |
| `/config`       | Configura canal de logs e permissões.                 | Admin         |
| `/limpar_dados` | Remove registros antigos do sistema.                  | Admin         |

## 🛡️ Controle de Acesso e Permissões

Alguns comandos são restritos para garantir a segurança dos dados.

- **Admins**: Usuários com permissão de `Administrador` no Discord têm acesso total aos comandos
  `/config` e `/limpar_dados`.
- **Relatórios**: Usuários comuns só podem gerar relatórios de si mesmos. Administradores podem
  gerar de qualquer membro.
- **Moderação**: O comando `/config` permite definir um cargo específico que também terá acesso ao
  bot (futura implementação).

## ❓ FAQ & Troubleshooting

### O bot não inicializa

- Verifique se o `DISCORD_TOKEN` no `.env` está correto.
- Certifique-se de usar Python 3.11+.

### Erro de Permissão no Docker

- Se tiver problemas de permissão na pasta `data/`, rode:
  ```bash
  sudo chown -R 1000:1000 data/
  ```
  (O bot roda com UID/GID não-root por segurança).

### Os horários estão errados

- O bot utiliza o fuso horário `America/Sao_Paulo` internamente.
- No Docker, verifique se o relógio do host está sincronizado.

## 🛠️ Estrutura do Projeto

```text
ponto-salinha/
├── src/
│   ├── main.py         # Ponto de entrada e Boot
│   ├── database.py     # Gerenciamento de Banco (Async/Safe)
│   ├── healthcheck.py  # Script de verificação Docker
│   └── cogs/           # Módulos
│       ├── admin.py    # Comandos Administrativos
│       ├── ponto.py    # Lógica de Registro
│       ├── ranking.py  # Consultas de Ranking
│       └── report.py   # Geração de Excel
├── data/               # Banco de Dados (Gerado no volume Docker)
├── Dockerfile          # Configuração da Imagem Segura
└── docker-compose.yml  # Orquestração
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

### Desenvolvedor

Feito com 💜 por Gabriel Ramos
