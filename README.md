# ⏱️ Ponto Salinha

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/Discord.py-2.0%2B-5865F2?style=flat-square&logo=discord&logoColor=white)
![Database](https://img.shields.io/badge/Database-Async_SQLite-4169E1?style=flat-square&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

> Um bot de registro de ponto eletrônico robusto, assíncrono e fácil de implantar para comunidades do Discord e equipes remotas.

## Descrição

O **Ponto Salinha** permite que os usuários registrem entrada e saída diretamente no Discord, acompanhando suas horas de trabalho com precisão. Projetado para equipes que precisam de um gerenciamento de tempo simples e eficaz sem depender de plataformas externas complexas, este bot garante latência zero e controle total dos dados por um banco de dados SQLite local.

### Principais Funcionalidades
- **Rastreamento em Tempo Real**: Feedback instantâneo para ações de entrada e saída com cálculo de duração.
- **Rankings de Produtividade**: Visualize os membros mais ativos por dia, semana, mês ou estatísticas gerais.
- **Relatórios em Excel**: Gere relatórios detalhados em formato `.xlsx` para usuários individuais ou para toda a equipe.
- **Arquitetura Assíncrona**: Construído com `aiosqlite` para garantir operações não bloqueantes, mesmo sob carga.
- **Docker Ready**: Configuração Docker pronta para uso com verificações de integridade (healthchecks) e persistência.

## Índice
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Início Rápido](#início-rápido--uso)
- [Comandos](#comandos)
- [Desenvolvimento](#desenvolvimento)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Instalação

### Pré-requisitos
- Python 3.11 ou superior
- [Docker](https://www.docker.com/) & Docker Compose (Recomendado para produção)
- Um Token de Bot do Discord (Obtenha no [Discord Developer Portal](https://discord.com/developers/applications))

### Opção 1: Docker (Recomendado)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/ponto-salinha.git
   cd ponto-salinha
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   # Certifique-se de que o arquivo .env.example existe na raiz do projeto
   cp .env.example .env
   # Abra o .env e adicione seu DISCORD_TOKEN
   ```

3. **Inicie o container:**
   ```bash
   docker-compose up -d --build
   ```

### Opção 2: Instalação Manual

1. **Clone e entre no diretório:**
   ```bash
   git clone https://github.com/seu-usuario/ponto-salinha.git
   cd ponto-salinha
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o bot:**
   ```bash
   python src/main.py
   ```

## Configuração

A aplicação é configurada via arquivo `.env` na raiz do projeto.

| Variável | Descrição | Padrão | Obrigatório |
|:---------|:------------|:--------|:---------|
| `DISCORD_TOKEN` | Token do seu Bot do Discord | - | Sim |
| `DATABASE_PATH` | Caminho para o arquivo do banco SQLite | `ponto.db` | Sim |
| `LOG_LEVEL` | Nível de detalhamento dos logs (DEBUG, INFO, WARNING) | `INFO` | Não |

**Exemplo de `.env`:**
```ini
DISCORD_TOKEN=OTk5...
DATABASE_PATH=data/ponto.db
LOG_LEVEL=INFO
```

## Início Rápido / Uso

Assim que o bot estiver online, ele exibirá o status "Jogando /ponto". Você pode interagir com ele usando Comandos de Barra (Slash Commands) em qualquer canal que o bot tenha acesso.

**Registrando Entrada:**
Digite `/ponto` para iniciar seu turno.
> **Bot:** "🟢 Ponto de Entrada registrado às 09:00:00"

**Registrando Saída:**
Digite `/ponto` novamente para encerrar seu turno.
> **Bot:** "🔴 Ponto de Saída registrado às 17:00:00. Duração: 8h 00min"

## Comandos

| Comando | Argumentos | Permissões | Descrição |
|:--------|:----------|:------------|:------------|
| `/ponto` | Nenhum | Todos | Alterna seu status entre "Trabalhando" e "Folga". |
| `/ranking` | `[periodo]` (hoje, semana, mes, total) | Todos | Exibe o ranking de horas trabalhadas. |
| `/relatorio` | `[usuario]` (Opcional) | Usuário/Admin | Gera um arquivo Excel com os logs de tempo. |
| `/config` | `canal_log` (Obrigatório), `[cargo]` (Opcional) | Admin | Define o canal de logs e o cargo autorizado opcional. |
| `/limpar_dados` | `periodo` | Admin | **⚠️ PERIGO**: Remove permanentemente registros do banco. Requer confirmação explícita. |

## Desenvolvimento

### Configuração do Ambiente de Dev

1. Instale as dependências do projeto.
2. Execute o bot localmente usando `python src/main.py`.
3. Use um `DISCORD_TOKEN` separado para testes de desenvolvimento.

### Executando Testes
*Atualmente, o projeto não possui uma suíte de testes dedicada. Contribuições adicionando testes unitários para `database.py` e Cogs são bem-vindas.*

## Contribuição

Contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito apreciada**.

1. Faça um Fork do projeto
2. Crie sua Branch de Funcionalidade (`git checkout -b feature/MinhaFuncionalidade`)
3. Faça o Commit de suas alterações (`git commit -m 'Adiciona MinhaFuncionalidade'`)
4. Faça o Push para a Branch (`git push origin feature/MinhaFuncionalidade`)
5. Abra um Pull Request

## Licença

Distribuído sob a Licença MIT. Veja `LICENSE` para mais informações.

## Autores & Agradecimentos

- **Gabriel Ramos** - *Trabalho Inicial*

*Construído com [discord.py](https://github.com/Rapptz/discord.py) e [aiosqlite](https://github.com/omnilib/aiosqlite).*

---

## Suporte

Se você encontrar algum problema ou tiver dúvidas, siga estas diretrizes:

- **Bugs**: Abra uma [Issue](https://github.com/seu-usuario/ponto-salinha/issues) usando o modelo de Bug. Inclua passos para reproduzir, comportamento esperado e logs, se possível.
- **Funcionalidades**: Para sugerir novas ideias, use o modelo de Feature Request descrevendo o caso de uso.
- **Dúvidas**: Para perguntas gerais ou ajuda com configuração, sinta-se à vontade para perguntar em nosso servidor do Discord ou nas Discussões do GitHub.
