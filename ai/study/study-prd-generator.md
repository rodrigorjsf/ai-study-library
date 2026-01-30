# Prompt Genérico para Geração de PRD de Exercício Técnico

Você é um engenheiro sênior de backend responsável por criar especificações técnicas para exercícios práticos de aprendizado. Sua tarefa é gerar um PRD (Product Requirements Document) detalhado para implementação em Java.

O produto gerado deve ser um exercício técnico que permita ao usuário praticar um conceito técnico específico e que simule operações reais de um sistema e que possa ser usado como portfólio em seu repositório GitHub.

## Contexto do Exercício
**Tópico/Conceito a ser praticado:** [INSERIR TÓPICO - ex: "Hash Tables e tratamento de colisões", "Concorrência com threads e race conditions", "Rate Limiting distribuído"]

## Estrutura do PRD

### 1. OBJETIVO DE APRENDIZADO
- Liste 3-5 conceitos técnicos específicos que devem ser exercitados
- Para cada conceito, explique POR QUÊ ele é importante em sistemas reais
- Identifique armadilhas comuns (edge cases, bugs típicos) que o desenvolvedor deve encontrar e resolver

### 2. ESPECIFICAÇÃO FUNCIONAL

#### 2.1 Problema a Resolver
- Descreva um cenário real de negócio (ex: "Sistema de cache para e-commerce", "Processador de pedidos concorrentes")
- Defina requisitos funcionais claros e mensuráveis
- Inclua restrições e limites (ex: "Deve suportar 10.000 operações/segundo", "Memória limitada a 256MB")

#### 2.2 API Pública
Defina a interface Java que deve ser implementada:
```java
// Forneça assinaturas de métodos, javadocs, contratos esperados
public interface [NomeDaInterface] {
    /**
     * [Descrição do método]
     * @param [parametro] [descrição]
     * @return [descrição do retorno]
     * @throws [Exceção] quando [condição]
     */
    ReturnType metodoExemplo(ParameterType param);
}
```

#### 2.3 Comportamento Esperado
- Descreva o comportamento correto em casos normais
- Liste pelo menos 5 cenários de edge case que devem ser tratados
- Defina comportamento esperado para condições de erro

### 3. REQUISITOS TÉCNICOS

#### 3.1 Estruturas de Dados
- Quais estruturas de dados DEVEM ser usadas? Por quê?
- Quais estruturas de dados NÃO devem ser usadas? (para forçar implementação low-level quando relevante)
- Qual a complexidade de tempo/espaço esperada para cada operação?

#### 3.2 Considerações de Concorrência (quando aplicável)
- Quais operações devem ser thread-safe?
- Quais garantias de sincronização são necessárias? (ex: atomicidade, visibilidade, ordering)
- Defina cenários de teste concorrente específicos

#### 3.3 Restrições de Implementação
- Bibliotecas permitidas (ex: apenas java.util.concurrent.*, não pode usar Guava)
- Padrões de design que DEVEM ser aplicados
- Métricas de qualidade de código (ex: cobertura de testes > 80%, cyclomatic complexity < 10)

### 4. CRITÉRIOS DE SUCESSO

#### 4.1 Funcionalidade (40%)
- [ ] Todos os testes unitários passam
- [ ] Trata corretamente os 5 edge cases definidos
- [ ] Performance atende aos limites especificados

#### 4.2 Qualidade de Código (30%)
- [ ] Segue princípios SOLID
- [ ] Nomes de variáveis/métodos são autodescritivos
- [ ] Sem code smells óbvios (duplicação, métodos > 20 linhas, god classes)

#### 4.3 Entendimento Técnico (30%)
- [ ] Comentários explicam decisões de design (não o "quê", mas o "por quê")
- [ ] Análise de complexidade está documentada
- [ ] Trade-offs foram identificados e justificados

### 5. TESTES OBRIGATÓRIOS

#### 5.1 Testes Unitários (mínimo 10 casos)
Liste cenários específicos:
1. [Caso de teste 1 - ex: "Inserir 1000 elementos e verificar não há colisões"]
2. [Caso de teste 2 - ex: "Inserir elemento nulo deve lançar IllegalArgumentException"]
...

#### 5.2 Testes de Concorrência (quando aplicável)
Liste cenários específicos:
1. [Caso de teste 1 - ex: "10 threads inserindo simultaneamente 100 elementos cada"]
2. [Caso de teste 2 - ex: "1 thread escrevendo, 5 threads lendo - verificar consistência"]
...

#### 5.3 Testes de Performance (quando aplicável)
- Defina benchmarks mínimos (ex: "1 milhão de get() deve completar em < 100ms")
- Especifique como medir (ex: usar JMH, System.nanoTime())

### 6. ETAPAS DE IMPLEMENTAÇÃO SUGERIDAS

Divida em 3-4 milestones incrementais:

**Milestone 1: Estrutura Básica (2-3 horas)**
- [ ] Implementar interface básica
- [ ] Casos de teste básicos passando
- [ ] Funcionalidade happy path

**Milestone 2: Edge Cases (2-3 horas)**
- [ ] Tratamento de erros
- [ ] Casos limite
- [ ] Validações

**Milestone 3: Otimização (2-4 horas)**
- [ ] Atender requisitos de performance
- [ ] Reduzir complexidade onde possível
- [ ] Adicionar concorrência (se aplicável)

**Milestone 4: Refinamento (1-2 horas)**
- [ ] Refatoração
- [ ] Documentação
- [ ] Code review self-checklist

### 7. RECURSOS DE APOIO
- Links para documentação Java relevante
- Artigos/papers fundamentais sobre o conceito
- Exemplos de implementações similares em projetos open-source (para inspiração, não cópia)

### 8. DESAFIOS EXTRAS (Opcional)
Após implementação básica, sugerir 2-3 extensões:
- [Extensão 1 - ex: "Adicionar suporte a TTL (time-to-live) nos elementos"]
- [Extensão 2 - ex: "Implementar serialização para persistir estado em disco"]
- [Extensão 3 - ex: "Criar API assíncrona usando CompletableFuture"]

### 9. QUESTÕES DE REFLEXÃO PÓS-IMPLEMENTAÇÃO
Após completar, o desenvolvedor deve responder:
1. Quais decisões de design você tomou e por quê?
2. Onde estão os principais trade-offs da sua solução?
3. Como sua implementação se comportaria com 100x mais carga?
4. Quais partes você refatoraria se tivesse mais tempo?
5. Que bugs você descobriu durante os testes e como os corrigiu?

---

## INSTRUÇÕES PARA GERAÇÃO

1. **Seja específico, não genérico:** "Implementar hash table com chaining" é melhor que "Estudar hash tables"

2. **Force descoberta, não entregue respostas:** Inclua edge cases que façam o desenvolvedor tropeçar e aprender (ex: race conditions sutis, overflow numérico)

3. **Priorize profundidade sobre amplitude:** Melhor exercitar 3 conceitos profundamente que 10 superficialmente

4. **Conecte com sistemas reais:** Sempre explique onde isso aparece em produção (ex: "Guava Cache usa essa técnica", "Kafka usa essa estrutura de dados")

5. **Inclua armadilhas pedagógicas:** Requisitos que parecem simples mas têm pegadinhas (ex: "remover elementos durante iteração", "overflow em multiplication para hashing")

6. **Especifique métricas objetivas:** "Thread-safe" é vago; "Não deve ter data races detectáveis com ThreadSanitizer" é concreto

7. **Balanceie desafio:** Deve ser difícil o suficiente para forçar pensamento, mas completável em 6-10 horas

## OUTPUT ESPERADO

Gere o PRD completo em Markdown, pronto para ser adicionado ao NotebookLM ou convertido em Issues do GitHub/Jira. Inclua código de exemplo (interfaces, esqueletos de testes) quando apropriado.

---

## Exemplo de Uso do Prompt

**Input:**
```
[Cole o prompt genérico acima]

Tópico a ser praticado: "Concurrent Hash Map com Read-Write Locks"
```

**Output esperado:**
Um PRD de 3-5 páginas especificando implementação de um `ConcurrentHashMap` personalizado usando `ReadWriteLock`, incluindo testes de race conditions, benchmarks de throughput, e análise de trade-offs entre granularidade de locks vs contention.

---

## Melhorias ao Prompt (Você Pode Customizar)

**Adições opcionais dependendo do contexto:**

```markdown
### CONFIGURAÇÕES EXTRAS (Adicione ao prompt base quando relevante)

**Para tópicos de estruturas de dados:**
- Adicionar seção "Invariantes a Manter" (ex: "altura da AVL nunca difere mais que 1")
- Adicionar visualização esperada (ex: "desenhe como a memória deve estar organizada")

**Para tópicos de concorrência:**
- Adicionar cenários de interleaving específicos que devem ser testados
- Adicionar requisitos de instrumentação (ex: "log lock acquisitions para debug")

**Para tópicos de sistemas distribuídos:**
- Adicionar cenários de falha de rede/partições
- Adicionar requisitos de observabilidade (métricas, logs estruturados)

**Para APIs/REST:**
- Adicionar especificação OpenAPI
- Adicionar casos de uso de clientes (curl commands, código cliente exemplo)
```

---

## Crítica ao Seu Pedido (Construtiva)

**Pressuposto questionável:** Você pede um prompt "genérico" para "qualquer assunto". 

**Problema:** Exercícios eficazes são inerentemente específicos ao domínio:
- Estruturas de dados requerem análise de invariantes
- Concorrência requer testes de interleaving
- APIs requerem especificação de contratos HTTP

**Solução no prompt:** Incluí seções condicionais que você ativa/desativa baseado no tópico. Não tente gerar PRDs completamente genéricos—sempre customize minimamente.

**Pergunta para você:** Qual tópico específico você quer testar primeiro com este prompt? Posso gerar um PRD de exemplo para validar se a estrutura atende suas necessidades.