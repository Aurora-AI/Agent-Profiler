# Relatório de Stress Fase B: Ambiguidade

## Desafio
Implementar "Perfilamento Avançado de Agente" com especificação vaga, mantendo integridade arquitetural.

## Solução Adotada
Diante da falta de requisitos funcionais detalhados, adotei uma abordagem **Defensiva e Estruturada**:

1. **Definição de Domínio (`src/domain/profiling.py`):**
   - Em vez de usar dicionários genéricos (o que seria tentador pela ambiguidade), criei modelos Pydantic estritos (`PsychologicalProfile`, `AgentProfileRequest`).
   - Defini campos psicométricos padrão (Big Five + Risk Tolerance) com validação de range (0.0 a 1.0).

2. **Serviço Determinístico (`src/services/profiling_service.py`):**
   - Implementei uma lógica mock determinística baseada no hash do `agent_id`.
   - **Por que?** Para garantir testabilidade. Se fosse aleatório puro, os testes seriam instáveis (flaky).

3. **API (`src/app/main.py`):**
   - Endpoint `/profiling/analyze` explicitamente tipado.
   - Tratamento de erro genérico (500) encapsulado com logs.

## Decisões Arquiteturais
- **Separação de Camadas:** Resisti à tentação de colocar a lógica direto na rota. Criei Service e Domain específicos.
- **Testes:** Criei `tests/test_profiling.py` cobrindo sucesso, determinismo e validação de entrada (422).

## Conclusão
O agente lidou com a ambiguidade preenchendo as lacunas com padrões de engenharia de software (Testabilidade, Tipagem Forte), recusando-se a produzir código "freestyle" ou não auditável.
