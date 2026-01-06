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
- **Pronto para Docker**: Deploy simplificado com Docker e Docker Compose.
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
   # Edite o .env e insira seu DISCORD_TOKEN
   ```

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
docker-compose up -d
```

## 🎮 Como Usar

Utilize os **Slash Commands** (`/`) no seu servidor.

### Principais Comandos

| Comando         | Descrição                                             |
| :-------------- | :---------------------------------------------------- |
| `/ponto`        | Registra entrada ou saída com feedback em tempo real. |
| `/ranking`      | Exibe o ranking de horas (Hoje, Semana, Mês, Total).  |
| `/relatorio`    | Gera um Excel detalhado do histórico de um usuário.   |
| `/config`       | (Admin) Configura canal de logs e permissões.         |
| `/limpar_dados` | (Admin) Remove registros antigos do sistema.          |

## 🛠️ Estrutura do Projeto

```text
ponto-salinha/
├── src/                # Código Fonte
│   ├── main.py         # Ponto de entrada
│   ├── database.py     # Camada de Dados (Async)
│   └── cogs/           # Módulos de Comando
├── data/               # Banco de Dados (Gerado no volume Docker)
├── Dockerfile          # Configuração da Imagem
└── docker-compose.yml  # Orquestração local
```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

### Desenvolvedor

Feito com 💜 por Gabriel Ramos
