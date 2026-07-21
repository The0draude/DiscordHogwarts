# RP Manager Bot

Bot para Discord (feito com `discord.py`) que automatiza a criação e gestão de categorias de RP (Roleplay), incluindo canais, cargos de dono/membro, permissões e um sistema de divulgação com cargos por reação.

## ⚙️ Requisitos

- Python 3.10+
- `discord.py` (com suporte a `commands`, forums e intents privilegiados)
- `python-dotenv`

```bash
pip install discord.py python-dotenv
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

- Não há persistência do `react_role_map` (perdido a cada restart).
- Não há tratamento de erro caso `!Setar`/`!DeletarCategorias` recebam nomes inexistentes de forma silenciosa para o usuário (os logs vão para o console, não para o Discord, na maioria dos comandos).
- Não há confirmação antes de `!DeletarCategorias` (ação destrutiva e irreversível).
- Uso de `discord.utils.get` por nome pode gerar ambiguidade se houver categorias/cargos duplicados.
