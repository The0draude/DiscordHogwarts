# ⚔️ Sistema de Combate por Duelo

Sistema estratégico de duelos 1v1 com **triângulo de vitória**, **sincronização de turnos**, **cooldowns** e **feitiços com tipos**.

## 📋 Visão Geral

Dois jogadores se enfrentam em duelo. **Primeiro a acertar N vezes ganha** (N configurável pelo admin, padrão: 3).

Cada turno:
1. Ambos os jogadores escolhem um **feitiço**
2. O sistema resolve o triângulo: **Ataque > Controle > Defesa**
3. Alguém recebe um acerto (ou não)
4. Cooldowns são reduzidos
5. Próximo turno!

---

## ⚔️ Triângulo de Vitória

```
       ATAQUE
        ╱  ╲
       ╱    ╲
    ganha  perde
     ╱        ╲
    ╱          ╲
 CONTROLE ─── DEFESA
```

### Mecânica:
- **Ataque > Controle**: Ataque passa, controle falha → **1 acerto**
- **Controle > Defesa**: Debuff passa pelo Protego → **1 acerto**
- **Defesa > Ataque**: Dano bloqueado → **TURNO EXTRA** ✨

### Avada Kedavra (Morte):
- ⚠️ **Ignora Defesa** — passa direto mesmo que defenda
- Ainda perde para Controle

---

## 🤝 Empates

| Cenário | Resultado |
|---------|-----------|
| **Ataque vs Ataque** | 💥 **Troca de dano** — ambos levam 1 acerto |
| **Defesa vs Defesa** | 🛡️ **Nada acontece** — turno perdido para ambos |
| **Controle vs Controle** | 🌪️ **Debuffs neutralizam** — efeito narrativo |

---

## ⏳ Cooldowns

- **Padrão**: 2 turnos para todos os feitiços
- Reduzem **-1 após cada turno**
- Admin pode mudar com `/set-cooldown`

**Exemplo**:
- Turno 1: Você usa "stupefy" → cooldown = 2
- Turno 2: Stupefy em cooldown (2 turnos faltam)
- Turno 3: Stupefy em cooldown (1 turno falta)
- Turno 4: ✅ Stupefy pronto!

---

## 🎯 Feitiços por Tipo

### 🔴 Ataque
- `stupefy` — ⭐ Atordoar
- `flipendo` — 👊 Empurrão
- `reducto` — 💥 Redução
- `sectumsempra` — 🔪 Corte
- `avada_kedavra` — ☠️ **Morte (ignora Defesa!)**

### 🟢 Defesa
- `protego` — 🛡️ Proteção
- `expelliarmus` — 🗡️ Desarmar

### 🟡 Controle
- `crucio` — 🌪️ Maldição (debuff)

---

## 🎮 Como Jogar

### 1️⃣ Iniciar Duelo
```
/duelar @adversário
```
- Ambos precisam ter **ficha criada** (`/criar-ficha`)
- Cria um duelo com os `max_hits` configurados para cada um

### 2️⃣ Agir no Turno
```
/agir
```
- Mostra um **select dropdown** com feitiços disponíveis
- Pode usar apenas feitiços **desbloqueados** e **sem cooldown**
- Após escolher, fica **"Aguardando oponente..."**

### 3️⃣ Sincronização
- O sistema **espera os dois** escolherem
- Quando ambos escolhem: **resolve turno** automaticamente
- Mostra resultado + status

### 4️⃣ Verificar Status
```
/duelo-status
```
- Mostra acertos atuais, cooldowns, turno número
- Efêmero (só você vê)

### 5️⃣ Sair do Duelo
```
/sair-duelo
```
- Você **se rende** → outro jogador **vence**

---

## 🔧 Comandos Admin

### Configurar Max Hits
```
/set-max-hits @usuário 3
```
- Define quantos acertos o usuário aguenta
- Padrão: 3
- Duelo usa o **máximo entre os dois** jogadores

### Configurar Cooldown
```
/set-cooldown @usuário stupefy 2
```
- Muda o cooldown de um feitiço
- Padrão: 2 turnos

### Desbloquear Feitiço
```
/unlock-spell @usuário avada_kedavra
```

---

## 📊 Exemplo de Duelo

```
⚔️ Turno 1
Alice escolhe: Stupefy (Ataque)
Bob escolhe: Protego (Defesa)

Resultado:
⚔️ Bob lançou protego!
❌ Alice com stupefy não conseguiu se defender!
✨ Bloqueio perfeito! Bob ganha turno extra!

Status: Alice: 0/3 | Bob: 0/3

---

⚔️ Turno 2 (Bob tem turno extra)
Bob escolhe: Flipendo (Ataque)
Alice escolhe: Crucio (Controle)

Resultado:
⚔️ Alice lançou crucio!
❌ Bob com flipendo não conseguiu se defender!
✅ ACERTO! Alice: 1 | Bob: 0

---

⚔️ Turno 3
... duelo continua ...
```

---

## 🏆 Vencedor

Primeiro a atingir o `max_hits` **vence**!

```
🏆 DUELO FINALIZADO!
**@Alice** VENCEU!
```

---

## 🔐 Regras Estratégicas

1. **Faça o oponente gastar Protego**: Use Controle para forçar defesa
2. **Bloqueio oferece turno extra**: Defesa > Ataque é poderoso!
3. **Cooldowns são críticos**: Não desperdice Avada Kedavra no turno 1
4. **Troca de dano é arriscada**: Ambos levam acerto
5. **Controle vs Controle = nada**: Use para desligar turnos

---

## 📝 Estrutura Técnica

- `combat_system.py` — Lógica do triângulo, empates, sincronização
- `duel.py` — Comandos de duelo (`/duelar`, `/agir`, `/duelo-status`, `/sair-duelo`)
- `admin.py` — Comando `/set-max-hits`

### Fluxo:
1. `CombatSystem.create_duel()` → Cria duelo
2. `set_action()` → Registra ação de um jogador
3. Quando 2 prontos → `execute_round()` → resolve triângulo
4. `reduce_cooldowns()` → atualiza para próximo turno
5. Verifica `max_hits` → alguém venceu?

