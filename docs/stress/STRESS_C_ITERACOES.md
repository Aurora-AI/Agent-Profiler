# Relatório de Stress Fase C: Evolução Iterativa

## Ciclo 1: Decorator Pattern para Cache (Refatoração)

**Mutação:**
Substituir a lógica de cache inline dentro do `GenerationService` por um padrão de **Decorator** (ou Proxy).
Atualmente, `GenerationService` conhece `CacheProvider`. Isso viola levemente o Single Responsibility Principle.

**Implementação:**
1. Criar `CachedGenerationService` que "embrulha" o `GenerationService` original.
2. O `GenerationService` volta a ser puro (apenas orquestra providers).

**Riscos:**
- Aumento da complexidade de injeção de dependência.
- Possível quebra de testes se a injeção na `main.py` falhar.

---

## Ciclo 2: Rate Limiting (Robustez)

**Mutação:**
Implementar um mecanismo de Rate Limit simples (Token Bucket) em memória para proteger o provider.

**Implementação:**
- Middleware ou Decorator na camada de serviço.
- Limite: 100 req/s.

**Riscos:**
- Rejeição de requisições legítimas no benchmark (falso negativo de performance).

---

## Ciclo 3: Circuit Breaker (Resiliência)

**Mutação:**
Adicionar Circuit Breaker para evitar chamadas ao Provider se ele estiver falhando consecutivamente.

**Implementação:**
- Lógica de estado (Closed -> Open -> Half-Open).
- Fallback para erro rápido.

**Riscos:**
- Complexidade de estado global.

---

*Iniciando execução dos ciclos...*
