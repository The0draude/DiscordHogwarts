# RP Manager Bot

Bot para Discord (feito com `discord.py`) que automatiza a criação e gestão de categorias de RP (Roleplay), incluindo canais, cargos de dono/membro, permissões e um sistema de divulgação com cargos por reação.

## ⚙️ Requisitos

- Python 3.10+
- `discord.py` (com suporte a `commands`, forums e intents privilegiados)
- `python-dotenv`

```bash
pip install "discord.py>=2.1" python-dotenv
```

## 🔑 Configuração

Crie um arquivo `.env` na raiz do projeto com o token do bot:

```
TOKEN=seu_token_aqui
```

No [Discord Developer Portal](https://discord.com/developers/applications), habilite os seguintes **Privileged Gateway Intents**:
- Server Members Intent
- Message Content Intent

## 🚀 Rodando o bot

```bash
python bot.py
```

O prefixo padrão de comandos é `!`.

## 📜 Comandos

Todos os comandos abaixo exigem permissão de **Administrador**.

| Comando | Descrição |
|---|---|
| `!Criar <categoria> <canal1, canal2, ...>` | Cria (ou reaproveita) uma categoria e adiciona canais de **texto** dentro dela. |
| `!CriarPostagem <categoria> <canal1, canal2, ...>` | Cria (ou reaproveita) uma categoria e adiciona canais de **fórum** (postagem). |
| `!CriarCargo <cargo1, cargo2, ...>` | Cria um ou mais cargos no servidor. |
| `!Criarowned <nome> @membro` | Cria uma categoria privada com cargos `<nome>Owner` e `<nome>Member`, atribuindo ambos ao membro mencionado. |
| `!CriarRP <nome> @membro` | Cria uma estrutura completa de RP: categoria privada, cargos Owner/Member, canais de avisos/regras/lore (somente Owner posta), fórum de fichas, separadores e canais de chat livre (geral/comandos). |
| `!RenomearCategoria <nome atual>,<novo nome>` | Renomeia uma categoria e seus cargos `Owner`/`Member` associados. |
| `!DeletarCategorias <categoria1, categoria2, ...>` | Deleta as categorias informadas, seus canais e os cargos `Owner`/`Member` correspondentes. |
| `!Setar <categoria> @membro1 @membro2 ...` | Atribui o cargo `<categoria>Member` aos membros mencionados. |
| `!Divulgar` | Publica uma mensagem listando todas as categorias que possuem cargo `Member`, com emojis únicos. Reagir na mensagem atribui automaticamente o cargo correspondente (e remover a reação retira o cargo). |
| `!Painel` | Publica um painel interativo com botões (📋 Listar RPs, 🚪 Sair do RP, 🔄 Transferir Owner, 🗑️ Deletar meu RP) para os próprios membros gerenciarem seus RPs sem precisar de comandos de texto. |

## 🎛️ Painel interativo (`!Painel`)

Publica um embed com 4 botões, todos usando componentes nativos do Discord (`discord.ui`):

- **📋 Listar RPs** — mostra (de forma efêmera, só visível pra quem clicou) todos os RPs do servidor, quantos membros cada um tem e se o usuário é dono/membro.
- **🚪 Sair do RP** — abre um menu de seleção com os RPs em que o usuário está, e remove os cargos `Owner`/`Member` correspondentes ao escolher.
- **🔄 Transferir Owner** — para donos: escolhe qual RP transferir e depois seleciona o novo dono (via seletor nativo de usuários do Discord); move o cargo `Owner` e garante que o novo dono também tenha `Member`.
- **🗑️ Deletar meu RP** — para donos: escolhe o RP e pede confirmação explícita (botões "Confirmar"/"Cancelar") antes de apagar categoria, canais e cargos.

Os botões do painel usam `custom_id` fixo e são reregistrados em `bot.add_view(PainelView())` no `on_ready`, então continuam funcionando mesmo depois de reiniciar o bot (diferente do `react_role_map` do `!Divulgar`, que ainda é só em memória).

> ⚠️ Requer `discord.py` com suporte a `discord.ui.UserSelect` (Select Menu de usuários), disponível a partir da versão 2.1+.

## 🧩 Como funciona a estrutura de RP

Ao usar `!CriarRP` ou `!Criarowned`, o bot cria dois cargos por RP:
- **`<nome>Owner`**: permissões administrativas sobre a categoria (gerenciar canais, permissões, mensagens, fixar mensagens etc).
- **`<nome>Member`**: acesso de visualização e participação (enviar mensagens, anexar arquivos, reagir).

A categoria fica invisível para `@everyone` (`view_channel=False`), visível apenas para quem tem um dos dois cargos.

Em `!CriarRP`, os canais criados seguem este layout:
1. `📣・avisos`, `📖・regras`, `🌎・lore-do-mundo` — somente o Owner pode enviar mensagens.
2. `👤・fichas` — canal de fórum, aberto para Owner e Member.
3. Canal separador.
4. `💬・geral`, `🤖・comandos` — livre para Owner e Member.
5. Canal separador final.

## 🔁 Sistema de cargos por reação (`!Divulgar`)

O bot mantém em memória (`bot.react_role_map`) um mapeamento `mensagem → {emoji: cargo}`. Ao reagir, o membro recebe o cargo `Member` da categoria correspondente; ao remover a reação, o cargo é retirado.

> ⚠️ Esse mapeamento é armazenado apenas em memória (não é persistido em disco/banco de dados). Se o bot reiniciar, mensagens de divulgação antigas deixam de funcionar até que `!Divulgar` seja executado novamente.

## 📝 Observações e possíveis melhorias futuras

- Não há persistência do `react_role_map` (perdido a cada restart) — diferente do `!Painel`, que já é persistente.
- A maioria dos comandos de texto (`!Criar`, `!DeletarCategorias`, `!Setar` etc.) ainda só loga no console, sem responder no Discord — o `!Painel` já resolve isso para as ações que ele cobre.
- `!DeletarCategorias` (comando de texto) ainda não pede confirmação — só a exclusão via `!Painel` tem esse passo.
- Uso de `discord.utils.get` por nome pode gerar ambiguidade se houver categorias/cargos duplicados.
- Migrar os comandos restantes para slash commands (`app_commands`) deixaria tudo mais descobrível no Discord.
- Log de auditoria (quem criou/deletou o quê) em um canal específico do servidor.
