# Plano de Estudo Avançado: Engenharia de Software & AI Foundations

Este documento redefine o plano de estudo anterior, elevando a barra de exigência e integrando princípios de neurociência do aprendizado com o uso estratégico do **NotebookLM** como um amplificador cognitivo.

## 1. Fundamentos Científicos do Aprendizado (O "Como")

Para maximizar a retenção e a transferência de conhecimento, este plano adota estritamente:

1.  **Recuperação Ativa (Active Recall)**: Em vez de reler, você deve forçar seu cérebro a recuperar a informação.
    *   *Aplicação*: Nunca leia um capítulo inteiro passivamente. Leia uma seção, feche o livro/PDF e explique para o NotebookLM ou para si mesmo em voz alta.
2.  **Repetição Espaçada (Spaced Repetition)**: Revisitar tópicos antes que sejam esquecidos.
    *   *Aplicação*: O plano intercala revisões de tópicos anteriores nas semanas subsequentes.
3.  **Intercalação (Interleaving)**: Misturar tipos de problemas.
    *   *Aplicação*: Não estude apenas "Árvores" por uma semana. Misture problemas de Árvores com Concorrência no mesmo dia de prática.
4.  **Codificação Dupla & Elaboração**: Associar conceitos abstratos a exemplos concretos e visuais.

---

## 2. Ecossistema de Ferramentas

### A. A "Fonte da Verdade" (Livros/PDFs)
Os livros listados abaixo são a base. Você deve ter os PDFs ou versões físicas disponíveis.

### B. O "Parceiro Cognitivo" (NotebookLM)
O NotebookLM não é apenas um "resumidor". Ele será seu:
1.  **Tutor Socrático**: Fará perguntas para testar seu entendimento.
2.  **Gerador de Conexões**: Ligará conceitos de diferentes livros.
3.  **Crítico de Código**: Analisará seus designs antes de você codar.

---

## 3. Biblioteca de Prompts de Alta Performance (NotebookLM)

Copie e use estes prompts durante seus estudos. Considere que você já fez upload dos PDFs relevantes para o notebook daquele tema.

### 🐛 Para Desbloquear Conceitos Difíceis
> "Aja como um Engenheiro Sênior do Google. Estou com dificuldade de entender profundamente [CONCEITO, ex: 'Condition Variables em Java']. Explique este conceito usando uma analogia do mundo real, depois mostre como ele é implementado no nível do OS e, finalmente, dê um exemplo de código Java onde o uso incorreto causaria um bug catastrófico."

### 🧠 Para Retenção (Tutor Socrático)
> "Baseado nos capítulos que li sobre [TEMA], não me dê um resumo. Em vez disso, faça 3 perguntas conceituais difíceis que testem se eu realmente entendi as nuances. Aguarde minha resposta para cada uma antes de me corrigir."

### 🏗️ Para Arquitetura e Design
> "Estou projetando um sistema que precisa de [REQUISITO, ex: 'alta consistência de escrita']. Baseado no livro 'Designing Data-Intensive Applications' (ou similar na fonte), quais são os trade-offs de usar [TECNOLOGIA A] vs [TECNOLOGIA B]? Cite as páginas ou seções onde isso é discutido."

### 🔄 Para Síntese Cross-Topic
> "Encontre conexões entre [TEMA A, ex: 'Garbage Collection'] e [TEMA B, ex: 'Latência de API']. Como as escolhas feitas em A impactam diretamente B segundo os textos fornecidos?"

---

## 4. O Plano Mestre (Estrutura Detalhada)

### **Fase 1: Algo & Core Foundations (Semanas 1-6)**
**Objetivo**: Fluência em modelagem de problemas e entendimento profundo de como o código interage com a máquina.

#### 📚 Fontes Primárias (Notebook "Core CS"):
1.  *Entendendo Algoritmos* (Bhargava) - Para intuição.
2.  *Algoritmos: Teoria e Prática* (CLRS) - Para rigor.
3.  *Java Concurrency in Practice* (Goetz) - Para realidade.
4.  *Operating Systems: Three Easy Pieces* (OSTEP) - Para base.

#### 🗓️ Semana 1-2: Estruturas de Dados e Análise Assintótica
*   **Foco**: Big O, Arrays, Lists, Hash Tables, Recursão.
*   **Protocolo de Estudo**:
    1.  **Leitura Ativa**: Leia *Entendendo Algoritmos* caps 1-4.
    2.  **Prompt NotebookLM**: "Crie uma tabela comparativa de complexidade Big O para operações de busca, inserção e deleção em Arrays, Listas Ligadas e Hash Tables. Destaque os piores casos."
    3.  **Prática Deliberada**: Implementar `HashMap` do zero em Java (lidando com colisões).
    4.  **Deep Dive**: Ler CLRS cap 11 (Hash Tables) apenas as seções sobre endereçamento aberto vs encadeamento.

#### 🗓️ Semana 3-4: Grafos, Árvores e Busca
*   **Foco**: BFS, DFS, Dijkstra, BST, Árvores Balanceadas (conceito).
*   **Protocolo de Estudo**:
    1.  **Leitura Ativa**: *Entendendo Algoritmos* caps 6-7.
    2.  **Visualização**: Desenhar os algoritmos passo a passo no papel.
    3.  **Prompt NotebookLM**: "Analise os textos sobre Grafos. Quais são os casos de uso reais em redes sociais e mapas para BFS vs DFS? Gere um quiz com 5 cenários onde devo escolher um ou outro."
    4.  **Prática**: Resolver problemas de "Shortest Path" no LeetCode e pedir ao NotebookLM para explicar a solução ótima se travar.

#### 🗓️ Semana 5-6: Concorrência e Memória (O "Filtro")
*   **Foco**: Threads, Locks, Deadlocks, Memory Model, Garbage Collection.
*   **Protocolo de Estudo**:
    1.  **Leitura Difícil**: *Java Concurrency in Practice* caps 1-3. Este livro é denso.
    2.  **Prompt NotebookLM (Crucial)**: "Explique 'Memory Visibility' e 'Race Conditions' como se fosse para um júnior. Use metáforas. Em seguida, analise o texto sobre 'Volatile' e explique por que ele não garante atomicidade."
    3.  **Lab Prático**: Criar um programa que propositalmente causa um *Deadlock* e outro que causa uma *Race Condition*. Consertá-los.

---

### **Fase 2: Backend Engineering & System Design (Semanas 7-10)**
**Objetivo**: Construir sistemas robustos, escaláveis e seguros. Sair do "código que funciona" para "código que sobrevive à produção".

#### 📚 Fontes Primárias (Notebook "Backend Pro"):
1.  *Designing Web APIs* (Jin et al.)
2.  *HTTP: The Definitive Guide*
3.  *Designing Secure Software*
4.  *High Performance Browser Networking* (HPBN)

#### 🗓️ Semana 7-8: Protocolos (HTTP/2, gRPC, WebSocket) e API Design
*   **Foco**: Verbos, Status Codes, Caching, REST vs RPC, Real-time.
*   **Protocolo de Estudo**:
    1.  **Leitura**: *Http Guide* caps fundamentais + *HPBN* (seções de WebSocket).
    2.  **Prompt NotebookLM**: "Baseado no *Designing Web APIs*, quais são os anti-patterns comuns em design de APIs RESTful? Gere uma checklist de code-review para uma nova API."
    3.  **Desafio Prático**: Criar uma API simples onde o Caching (ETags/Last-Modified) funcione corretamente. Validar com `curl -v`.

#### 🗓️ Semana 9-10: Segurança e Identidade (AuthN/AuthZ)
*   **Foco**: OAuth2, OIDC, JWT, TLS, Ataques comuns (XSS, CSRF, Injection).
*   **Protocolo de Estudo**:
    1.  **Leitura**: *Designing Secure Software* + RFCs de OAuth2 (via NotebookLM).
    2.  **Prompt NotebookLM**: "Simule um auditor de segurança. Eu vou descrever um fluxo de autenticação que projetei e você deve encontrar vulnerabilidades baseadas nos textos carregados."
    3.  **Prática**: Implementar um fluxo "Login with Google" sem usar bibliotecas de alto nível (para entender os redirects e tokens).

---

### **Fase 3: Consolidação e Arquitetura (Semanas 11-12)**

#### 🗓️ Semana 11-12: System Design & Review
*   **Foco**: Juntar tudo. Como escalar? Como desenhar componentes desacoplados?
*   **Atividade Principal**: "Mock Design Sessions".
*   **Prompt NotebookLM (O "Interviewer")**: "Aja como um entrevistador de System Design. Me dê um problema vago (ex: 'Desenhe o Twitter'). Eu vou descrever minha abordagem passo a passo. A cada passo, critique minha escolha de banco de dados, protocolo ou algoritmo baseando-se nos princípios dos livros que carregamos."

---

## 5. A Rotina Diária (Micro-Ciclo de Estudo)

Para cada sessão de estudo (1h - 2h), siga este roteiro:

1.  **Prep (5 min)**:
    *   Abra o NotebookLM com as fontes do tema.
    *   Defina o objetivo claro: "Hoje vou entender como funciona o *ReentrantLock*".

2.  **Imersão (25-40 min)**:
    *   Leia o material focado.
    *   **Não anote passivamente**. Grife apenas o crucial.
    *   Se travar, use o prompt "Desbloquear Conceitos Difíceis".

3.  **Síntese Ativa (15 min)**:
    *   Feche o livro.
    *   Vá ao NotebookLM e dite (ou escreva): "Aqui está o que eu entendi sobre X... [Explicação]".
    *   Peça: "Avalie minha explicação. O que eu perdi? O que está impreciso?"

4.  **Prática (Restante do tempo)**:
    *   Escreva código. Não há aprendizado sem implementação.
    *   Se for System Design, desenhe diagramas.

5.  **Encerramento (Podcast)**:
    *   Gere um "Audio Overview" no NotebookLM sobre o texto lido para ouvir enquanto faz outra coisa (fixação passiva).

---

## 6. Próximos Passos (Action Items)

1.  [ ] **Organizar Notebooks**: Crie notebooks separados no NotebookLM para "Core CS", "Java Internals" e "Backend Architecture".
2.  [ ] **Carregar Fontes**: Faça upload dos PDFs listados na seção "Referências Essenciais" do arquivo anterior.
3.  [ ] **Iniciar Fase 1**: Comece hoje com Complexidade de Algoritmos.