# 🎮 Guia Rápido - Sistema de Duelo

## 👥 Para Jogadores

### 1. Iniciar um Duelo
```
/duelar @adversário
```
- Você precisa ter uma ficha criada
- O adversário também precisa ter ficha criada
- Nenhum dos dois pode estar em outro duelo

### 2. Escolher seu Feitiço
```
/agir
```
- Abre um menu para escolher o feitiço
- Mostra apenas os feitiços **desbloqueados** e **sem cooldown**
- Após escolher: **aguarde o oponente**

### 3. Ver Status do Duelo
```
/duelo-status
```
- Mostra quantos acertos você tem
- Mostra quantos acertos seu oponente tem
- Mostra turno atual
- Mostra se alguém tem turno extra

### 4. Desistir do Duelo
```
/sair-duelo
```
- Você se rende → **o outro jogador vence**

---

## 🔧 Para Administradores

### Criar Ficha de Jogador
```
/criar-ficha @usuário
```
- HP máximo: 80 (padrão, não afeta duelo)
- Poder mágico: 100 (padrão, não afeta duelo)
- Resistência: 0% (padrão, não afeta duelo)
- Feitiços: todos bloqueados (exceto stupefy e protego desbloqueados)

### Configurar Dificuldade
```
/set-max-hits @usuário 3
```
- Define quantos acertos o jogador aguenta
- Padrão: 3
- No duelo: usa o valor **máximo** entre os dois

### Desbloquear Feitiço
```
/unlock-spell @usuário avada_kedavra
```
- Libera um feitiço para o jogador usar

### Bloquear Feitiço
```
/lock-spell @usuário avada_kedavra
```
- Remove acesso ao feitiço

### Configurar Cooldown
```
/set-cooldown @usuário stupefy 2
```
- Define quantos turnos até o feitiço poder ser usado novamente
- Padrão: 2 turnos

---

## 📊 Exemplo Completo de Duelo

```
Alice: /duelar @Bob
> ⚔️ DESAFIO DE DUELO!
> Alice desafia Bob
> Alice: 3 acertos | Bob: 3 acertos
> Use /agir para começar!

Alice: /agir
> Select: Stupefy, Protego, Flipendo...
> Alice escolhe: Stupefy ✅
> Aguardando Bob...

Bob: /agir
> Select: Expelliarmus, Protego, Crucio...
> Bob escolhe: Crucio ✅

⚔️ Turno 1
Alice lançou stupefy!
❌ Bob com crucio não conseguiu se defender!
✅ ACERTO! Alice: 1 | Bob: 0

---

Alice: /agir
> Alice escolhe: Flipendo ✅
> Aguardando Bob...

Bob: /agir
> Bob escolhe: Protego ✅

⚔️ Turno 2
Bob lançou protego!
❌ Alice com flipendo não conseguiu se defender!
✨ Bloqueio perfeito! Bob ganha turno extra!
Alice: 1 | Bob: 0

--- (Bob vai agir novamente)

Bob: /agir
> Bob escolhe: Stupefy ✅
> Aguardando Alice...

Alice: /agir
> Alice escolhe: Stupefy ✅

💥 Turno 3
Ambos atacam simultaneamente!
⚡ TROCA DE DANO! Ambos levam acertos!
Alice: 2 | Bob: 1

... (continua até alguém atingir 3 acertos) ...

🏆 DUELO FINALIZADO!
**@Alice** VENCEU!
```

---

## 🎯 Dicas Estratégicas

1. **Reconheça o padrão do oponente**: 
   - Se ele sempre usa Ataque, prepare Defesa

2. **Use Controle para secar cooldown**:
   - Força o oponente a gastar defesa
   - Próximo turno pode atacar enquanto ele está com cooldown

3. **Turno extra é ouro**:
   - Defesa > Ataque oferece turno extra
   - Use esse turno para atacar ou secar cooldown do oponente

4. **Avada Kedavra é a ultima cartada**:
   - Ignora Defesa (a única coisa que passa por Defesa)
   - Use quando achar que seu oponente vai defender

5. **Sincronização é importante**:
   - Ambos devem escolher antes de resolver
   - Nenhuma vantagem de reação

