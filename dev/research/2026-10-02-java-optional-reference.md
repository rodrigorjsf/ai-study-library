---
date: 2026-10-02T00:00:00-03:00
topic: "java.util.Optional — Guia de Referência Completo: API, Boas Práticas, Antipatterns, Null Safety e Refactoring"
tags: [research, java, optional, null-safety, functional-programming, refactoring, code-review, best-practices]
status: complete
last_updated: 2026-10-02
java_baseline: "Java 8 (API original) → Java 25 LTS (API inalterada desde o Java 11)"
sources:
  - Javadoc oficial de java.util.Optional (JDK 8, 9, 10, 11, 21, 25)
  - Brian Goetz — resposta no StackOverflow sobre a intenção de design do Optional
  - Stuart Marks — "Optional: The Mother of All Bikesheds" (Devoxx 2016)
  - Joshua Bloch — Effective Java, 3ª ed., Item 55 "Return optionals judiciously"
  - SonarSource Java rules, inspeções do IntelliJ IDEA, JSpecify
intended_audience: "Desenvolvedores Java e agentes LLM que geram skills, rules, checklists de code review ou refactorings sobre Optional"
---

# `java.util.Optional` — Guia de Referência Completo

> **Como usar este documento.** Ele foi escrito para ser **fonte única e confiável** sobre `Optional`.
> Cada regra normativa tem um **ID estável** (`OPT-xx`, `AP-xx`, `RF-xx`) para que skills, rules
> (Claude Code, Cursor `.mdc`, Sonar custom rules, checklists) possam citá-la diretamente.
> As seções são independentes: uma rule pode copiar só o [Catálogo de Antipatterns](#7-catálogo-de-antipatterns)
> ou só o [Catálogo de Refactoring](#8-catálogo-de-refactoring-oportunidades-de-usar-a-api).
> Os exemplos de código compilam em **Java 11+** salvo indicação contrária (`// Java 9+`, etc.).

## Sumário

0. [TL;DR — As regras de ouro](#0-tldr--as-regras-de-ouro)
1. [O que é Optional e por que ele existe](#1-o-que-é-optional-e-por-que-ele-existe)
2. [Mapa completo da API (com versão do JDK)](#2-mapa-completo-da-api)
3. [Uso detalhado de cada método](#3-uso-detalhado-de-cada-método)
4. [`map` vs `flatMap` vs `filter` vs `or` — quando usar cada um](#4-map-vs-flatmap-vs-filter-vs-or)
5. [Optional como ferramenta de null safety](#5-optional-como-ferramenta-de-null-safety)
6. [Boas práticas](#6-boas-práticas)
7. [Catálogo de antipatterns](#7-catálogo-de-antipatterns)
8. [Catálogo de refactoring](#8-catálogo-de-refactoring-oportunidades-de-usar-a-api)
9. [Optionals primitivos](#9-optionals-primitivos-optionalint-optionallong-optionaldouble)
10. [Optional e Streams](#10-optional-e-streams)
11. [Optional em frameworks e bibliotecas](#11-optional-em-frameworks-e-bibliotecas)
12. [Performance](#12-performance)
13. [Testando código com Optional](#13-testando-código-com-optional)
14. [Árvore de decisão](#14-árvore-de-decisão)
15. [Checklist de code review](#15-checklist-de-code-review)
16. [Tabela de detecção (ferramentas estáticas)](#16-tabela-de-detecção-ferramentas-estáticas)
17. [Fontes](#17-fontes)

---

## 0. TL;DR — As regras de ouro

| ID | Regra |
|----|-------|
| **OPT-01** | Use `Optional<T>` **principalmente como tipo de retorno** de métodos que podem legitimamente não ter resultado. |
| **OPT-02** | **Nunca** retorne `null` de um método cujo tipo de retorno é `Optional`, e nunca atribua `null` a uma variável `Optional`. Use `Optional.empty()`. |
| **OPT-03** | **Não** use `Optional` como tipo de **campo**, **parâmetro de método/construtor** ou **elemento de coleção/valor de Map**. |
| **OPT-04** | **Não** envolva coleções, arrays ou streams em `Optional`. Retorne a coleção vazia. |
| **OPT-05** | Evite `get()`. Se for extrair incondicionalmente, prefira `orElseThrow()` (Java 10+), que tem o mesmo comportamento com um nome honesto. |
| **OPT-06** | Prefira as operações funcionais (`map`, `flatMap`, `filter`, `or`, `ifPresent`, `ifPresentOrElse`, `orElse*`) ao par `isPresent()` + `get()`. |
| **OPT-07** | Use `orElse(x)` só quando `x` já existe ou é barato (constante/literal). Para valores calculados, com efeitos colaterais ou caros, use `orElseGet(supplier)`. |
| **OPT-08** | Use `Optional.of(x)` quando `x` **não pode** ser null (falha rápido); `Optional.ofNullable(x)` só na fronteira com código que pode retornar null. |
| **OPT-09** | Não crie um `Optional` apenas para encadear métodos e obter um valor em seguida — um `if`/ternário ou `Objects.requireNonNullElse` é mais claro. |
| **OPT-10** | Use `flatMap` quando a função **já retorna `Optional`**; use `map` quando ela retorna um valor simples (possivelmente null). |
| **OPT-11** | Para primitivos, use `OptionalInt`, `OptionalLong`, `OptionalDouble`; nunca `Optional<Integer>` em APIs de alto volume. |
| **OPT-12** | `Optional` é uma *value-based class*: nunca use `==`, `synchronized` ou identidade sobre ele; compare com `equals`. |
| **OPT-13** | `Optional` **não é `Serializable`**: não o use em campos de classes serializáveis, entidades JPA ou DTOs serializados por mecanismos de identidade. |
| **OPT-14** | Não use `Optional` para controle de fluxo genérico ou para substituir todo `if (x != null)`. Ele é para **modelar ausência no contrato da API**. |

---

## 1. O que é Optional e por que ele existe

`java.util.Optional<T>` (Java 8+) é um **contêiner que pode ou não conter um valor não-nulo**. Ele existe
para que o **tipo de retorno** de um método comunique explicitamente "talvez não haja resultado",
forçando o chamador a lidar com a ausência em vez de receber um `null` silencioso.

### 1.1 Intenção de design (fonte primária)

O próprio Javadoc (Java 9+) traz uma **API Note** a nível de classe:

> *"Optional is primarily intended for use as a method return type where there is a clear need to
> represent "no result," and where using null is likely to cause errors. A variable whose type is
> Optional should never itself be null; it should always point to an Optional instance."*

Brian Goetz (arquiteto da linguagem Java na Oracle) resumiu a intenção no StackOverflow:

> *"Our intention was to provide a limited mechanism for library method return types where there
> needed to be a clear way to represent "no result", and using null for such was overwhelmingly likely
> to cause errors."* — e acrescenta que nunca se deve usá-lo para algo que retorna um array ou lista
> de resultados (retorne a lista vazia), nem como campo de algo ou como parâmetro de método.

### 1.2 As 7 regras de Stuart Marks (Devoxx 2016)

Stuart Marks (mantenedor das bibliotecas core do JDK na Oracle) consolidou o uso em sete regras,
amplamente citadas como referência canônica:

1. *"Never, ever, use null for an Optional variable or return value."* → OPT-02
2. *"Never use Optional.get() unless you can prove that the Optional is present."* → OPT-05
3. *"Prefer alternatives to Optional.isPresent() and Optional.get()."* → OPT-06
4. It's generally a bad idea to create an Optional for the specific purpose of chaining methods from it to get a value. → OPT-09
5. If an Optional chain is nested or has an intermediate result of `Optional<Optional<T>>`, it's probably too complex. → OPT-10
6. Avoid using Optional in fields, method parameters, and collections. → OPT-03
7. Avoid using identity-sensitive operations on Optionals. → OPT-12

Consequência prática: **Optional não é o "Maybe/Option" completo de Haskell/Scala/Vavr**. É uma
ferramenta deliberadamente limitada. Muitos antipatterns nascem de tratá-lo como se fosse.

### 1.3 Características do tipo

| Característica | Detalhe | Implicação |
|---|---|---|
| `final class` | Não pode ser estendida | — |
| Imutável | Não há setters | Seguro para compartilhar entre threads (se `T` for) |
| **Value-based** | Javadoc: *"programmers should treat instances that are equal as interchangeable and should not use instances for synchronization, or unpredictable behavior may occur"* | Nunca use `==`, `synchronized`, `System.identityHashCode` (OPT-12) |
| **Não `Serializable`** | Decisão intencional | Não use como campo (OPT-13) |
| Nunca contém `null` | `of(null)` lança NPE; `map` que retorna `null` vira `empty()` | O valor presente é sempre não-nulo |
| `equals`/`hashCode`/`toString` | Igualdade estrutural; `toString` → `Optional[valor]` ou `Optional.empty` | Pode ser usado em asserts de teste |
| Singleton vazio | `Optional.empty()` retorna sempre a mesma instância hoje | **Não** dependa disso (value-based) |

---

## 2. Mapa completo da API

| Categoria | Método | Desde | Retorno | Comportamento resumido |
|---|---|---|---|---|
| **Criação** | `static <T> Optional<T> empty()` | 8 | `Optional<T>` | Optional vazio |
| | `static <T> Optional<T> of(T value)` | 8 | `Optional<T>` | Presente; **NPE se `value == null`** |
| | `static <T> Optional<T> ofNullable(T value)` | 8 | `Optional<T>` | Vazio se `null`, presente caso contrário |
| **Teste** | `boolean isPresent()` | 8 | `boolean` | `true` se há valor |
| | `boolean isEmpty()` | **11** | `boolean` | `true` se não há valor |
| **Extração** | `T get()` | 8 | `T` | Valor ou `NoSuchElementException` (**evitar** — OPT-05) |
| | `T orElseThrow()` | **10** | `T` | Idêntico a `get()`, nome explícito (preferido) |
| | `<X extends Throwable> T orElseThrow(Supplier<? extends X>) throws X` | 8 | `T` | Valor ou lança a exceção fornecida (pode ser checked); NPE se o supplier produzir `null` |
| | `T orElse(T other)` | 8 | `T` | Valor ou `other` (avaliado **sempre**, eager) |
| | `T orElseGet(Supplier<? extends T>)` | 8 | `T` | Valor ou resultado do supplier (lazy) |
| **Ação** | `void ifPresent(Consumer<? super T>)` | 8 | `void` | Executa consumer se presente |
| | `void ifPresentOrElse(Consumer<? super T>, Runnable)` | **9** | `void` | Consumer se presente, Runnable se vazio |
| **Transformação** | `<U> Optional<U> map(Function<? super T, ? extends U>)` | 8 | `Optional<U>` | Aplica função; resultado `null` → `empty()` |
| | `<U> Optional<U> flatMap(Function<? super T, ? extends Optional<? extends U>>)` | 8 (wildcard ajustado no 9) | `Optional<U>` | Aplica função que já retorna Optional; **NPE se a função retornar `null`** |
| | `Optional<T> filter(Predicate<? super T>)` | 8 | `Optional<T>` | Mantém o valor se o predicado for verdadeiro; senão `empty()` |
| | `Optional<T> or(Supplier<? extends Optional<? extends T>>)` | **9** | `Optional<T>` | Se vazio, retorna o Optional alternativo (lazy); NPE se o supplier produzir `null` |
| **Interop** | `Stream<T> stream()` | **9** | `Stream<T>` | Stream de 0 ou 1 elemento |
| **Object** | `equals`, `hashCode`, `toString` | 8 | — | Igualdade estrutural |

> **Estabilidade da API:** não houve adições públicas entre o Java 11 e o Java 25 (nem no 26/27 —
> só mudanças internas e de Javadoc). Nenhum método está deprecated.
>
> **Sobre `get()`:** em 2016 Stuart Marks propôs depreciar `get()` (chamando-o de *"attractive nuisance"*).
> O ticket JDK-8140281 acabou entregue no Java 10 como *"add no-arg orElseThrow() as preferred alternative
> to get()"*. O Javadoc atual de `get()` diz: *"The preferred alternative to this method is orElseThrow()."*
> Brian Goetz, retrospectivamente: *"we should have called get something like
> getOrElseThrowNoSuchElementException"*.
>
> **Futuro (Valhalla):** com o JEP 401 (*Value Objects*, preview), `Optional` passa a ser uma
> **value class** quando preview features estão habilitadas — o código-fonte do OpenJDK (linha de
> desenvolvimento do JDK 28) já documenta: *"Use of value class instances for synchronization or with
> object references result in IdentityException."* Ou seja, OPT-12 deixa de ser só boa prática e vira
> erro em runtime. Código que já segue OPT-12 não é afetado.

---

## 3. Uso detalhado de cada método

Os exemplos usam este domínio:

```java
record Address(String street, String city, String zipCode) {}

class User {
    private final String id;
    private final String email;
    private final Address address;       // pode ser null (campo NÃO é Optional — OPT-03)
    private final String nickname;       // pode ser null

    // getters que expõem ausência via Optional (padrão recomendado)
    public Optional<Address> getAddress()  { return Optional.ofNullable(address); }
    public Optional<String>  getNickname() { return Optional.ofNullable(nickname); }
    public String getId()    { return id; }
    public String getEmail() { return email; }
}

interface UserRepository {
    Optional<User> findById(String id);   // uso canônico: retorno de busca
}
```

### 3.1 Criação: `empty()`, `of()`, `ofNullable()`

```java
Optional<String> a = Optional.empty();            // vazio
Optional<String> b = Optional.of("Ana");          // presente
Optional<String> c = Optional.of(null);           // ❌ NullPointerException imediata
Optional<String> d = Optional.ofNullable(null);   // vazio
Optional<String> e = Optional.ofNullable("Ana");  // presente
```

**Quando usar cada um:**

| Situação | Use | Por quê |
|---|---|---|
| Você **sabe** que não há valor | `Optional.empty()` | Intenção explícita; não `ofNullable(null)` |
| Você **sabe** que o valor é não-nulo | `Optional.of(x)` | Falha rápido (NPE) se a premissa estiver errada — é um *assert* gratuito |
| O valor vem de código que **pode** retornar null (legado, `Map.get`, API externa, JDBC, campo nullable) | `Optional.ofNullable(x)` | Converte a convenção `null` em `Optional` na fronteira |

```java
// ✅ Bom: fronteira com API que retorna null
public Optional<User> findInCache(String id) {
    return Optional.ofNullable(cache.get(id));     // Map.get pode retornar null
}

// ✅ Bom: caminhos explícitos
public Optional<Discount> discountFor(Order order) {
    if (order.total().compareTo(THRESHOLD) < 0) {
        return Optional.empty();
    }
    return Optional.of(new Discount(order.total().multiply(RATE)));  // nunca null aqui
}

// ❌ Ruim: ofNullable "por garantia" esconde bugs; se new Discount(...) nunca é null, use of()
return Optional.ofNullable(new Discount(...));
```

### 3.2 Teste: `isPresent()` e `isEmpty()`

```java
Optional<User> user = repo.findById(id);

if (user.isPresent()) { ... }   // Java 8+
if (user.isEmpty())   { ... }   // Java 11+ — prefira a !user.isPresent()
```

**Quando são aceitáveis:**

- **Guard clause com retorno antecipado** quando o ramo "vazio" faz algo que não cabe num lambda
  (ex.: `return`, `continue`, `break`, lançar exceção checked já tratada no contexto):

  ```java
  Optional<User> user = repo.findById(id);
  if (user.isEmpty()) {
      return ResponseEntity.notFound().build();
  }
  // ... muitas linhas usando user.orElseThrow()
  ```
  Mesmo assim, normalmente `map(...).orElseGet(...)` resolve (ver [RF-05](#rf-05)).

- **Em testes** (`assertTrue(opt.isPresent())`), embora asserções específicas sejam melhores ([§13](#13-testando-código-com-optional)).

- **Quando o resultado é só um booleano**: `boolean exists = repo.findById(id).isPresent();`
  (melhor ainda: um método `existsById` dedicado).

**Quando não usar:** como prefixo de `get()` (ver [AP-01](#ap-01)).

### 3.3 Extração: `get()`, `orElseThrow()`, `orElseThrow(Supplier)`

```java
User u1 = opt.get();                 // ❌ desencorajado: nome esconde que pode lançar
User u2 = opt.orElseThrow();         // ✅ Java 10+: mesmo comportamento, nome honesto
User u3 = opt.orElseThrow(() -> new UserNotFoundException(id));  // ✅ exceção de domínio
```

- `get()` e `orElseThrow()` lançam `NoSuchElementException("No value present")`.
- `orElseThrow(Supplier)` aceita **exceções checked**, porque o tipo `X extends Throwable` é propagado:

  ```java
  public User load(String id) throws UserNotFoundException {     // checked
      return repo.findById(id)
                 .orElseThrow(() -> new UserNotFoundException(id));
  }
  ```

- Use **referência a construtor** quando a exceção não precisa de argumentos:
  `opt.orElseThrow(IllegalStateException::new)`.

**Regra prática:**

| Situação | Método |
|---|---|
| Ausência é um **erro de negócio** esperado (404, entidade inexistente) | `orElseThrow(() -> new XxxNotFoundException(...))` |
| Ausência é **impossível** pela lógica (invariante); se acontecer é bug | `orElseThrow()` |
| Código Java 8/9 | `orElseThrow(NoSuchElementException::new)` ou `get()` imediatamente após prova de presença |

### 3.4 Valores padrão: `orElse()` vs `orElseGet()`

```java
String name = user.getNickname().orElse("anonymous");                   // ✅ constante
String name = user.getNickname().orElseGet(() -> generateNickname());   // ✅ cálculo lazy
```

**A diferença crucial: avaliação eager vs lazy.**
O argumento de `orElse` é avaliado **antes** da chamada, *sempre*, mesmo quando o Optional está presente.

```java
// ❌ Bug sutil: createDefaultUser() roda SEMPRE — inclusive faz INSERT no banco!
User u = repo.findById(id).orElse(createDefaultUser());

// ✅ Só executa se vazio
User u = repo.findById(id).orElseGet(() -> createDefaultUser());
User u = repo.findById(id).orElseGet(this::createDefaultUser);
```

| Use `orElse(x)` quando `x` é… | Use `orElseGet(() -> x)` quando `x`… |
|---|---|
| literal / constante (`""`, `0`, `List.of()`, `DEFAULT`) | envolve chamada de método não trivial |
| variável local já calculada | tem efeitos colaterais (I/O, banco, log, métricas) |
| `null` (interop com legado: `orElse(null)`) | aloca objetos grandes ou é caro |

> `orElse(null)` é **aceitável** na fronteira com APIs que esperam null (ex.: preencher um campo
> nullable de entidade, chamar biblioteca legada). Não é um antipattern em si; é um adaptador.

### 3.5 Ações: `ifPresent()` e `ifPresentOrElse()`

```java
// Executa somente se presente
repo.findById(id).ifPresent(user -> mailer.sendWelcome(user.getEmail()));
repo.findById(id).map(User::getEmail).ifPresent(mailer::sendWelcome);

// Java 9+: os dois ramos
repo.findById(id).ifPresentOrElse(
    user -> log.info("Found user {}", user.getId()),
    ()   -> log.warn("User {} not found", id)
);
```

**Quando usar:** quando o objetivo é um **efeito colateral** (enviar, logar, gravar, publicar evento)
e não um valor. Se você precisa de um valor de retorno, use `map(...).orElse*()`.

**Limitações dos lambdas** — se o ramo precisa de:
- lançar exceção **checked** (não declarada pela interface funcional),
- `return` do método externo, `break`/`continue`,
- modificar variável local (não *effectively final*),

…então um `if (opt.isPresent())`/`isEmpty()` com `orElseThrow()` é legítimo e mais legível.

**Java 8 (sem `ifPresentOrElse`):**

```java
Optional<User> u = repo.findById(id);
if (u.isPresent()) { handle(u.get()); } else { handleMissing(); }
// ou
u.map(x -> { handle(x); return true; }).orElseGet(() -> { handleMissing(); return false; }); // ❌ evite: abuso de map
```

### 3.6 Transformação: `map()`

Aplica uma função ao valor, se presente, e embrulha o resultado. **Se a função retornar `null`, o
resultado é `Optional.empty()`** — isso torna `map` ideal para navegar em getters que retornam null.

```java
Optional<String> email = repo.findById(id).map(User::getEmail);
Optional<Integer> len  = Optional.of("abc").map(String::length);        // Optional[3]
Optional<String> none  = Optional.of("x").map(s -> null);               // Optional.empty

// Navegação segura em grafo de objetos com getters nullable (POJOs legados)
String city = Optional.ofNullable(order)
        .map(Order::getCustomer)       // pode ser null
        .map(Customer::getAddress)     // pode ser null
        .map(LegacyAddress::getCity)   // pode ser null
        .orElse("UNKNOWN");
```

### 3.7 Transformação: `flatMap()`

Use quando a função **já retorna um `Optional`**. `map` produziria `Optional<Optional<U>>`;
`flatMap` "achata" para `Optional<U>`.

```java
// User.getAddress() retorna Optional<Address>
Optional<Optional<Address>> nested = repo.findById(id).map(User::getAddress);     // ❌ aninhado
Optional<Address>           flat   = repo.findById(id).flatMap(User::getAddress); // ✅

// Encadeando buscas que podem falhar
Optional<Invoice> invoice = orderRepo.findById(orderId)
        .flatMap(order -> customerRepo.findById(order.customerId()))
        .flatMap(customer -> billing.lastInvoiceOf(customer));
```

> **Atenção:** se a função passada a `flatMap` retornar `null` (em vez de `Optional.empty()`),
> `flatMap` lança `NullPointerException`. É mais um motivo para OPT-02.

### 3.8 Transformação: `filter()`

Mantém o valor se o predicado for verdadeiro; caso contrário, vira vazio.

```java
Optional<User> activeAdult = repo.findById(id)
        .filter(User::isActive)
        .filter(u -> u.age() >= 18);

// Validação de entrada
Optional<String> validEmail = Optional.ofNullable(rawEmail)
        .map(String::strip)
        .filter(s -> !s.isEmpty())
        .filter(EMAIL_PATTERN.asMatchPredicate());
```

### 3.9 Alternativa: `or()` (Java 9+)

Fornece **outro Optional** quando o atual está vazio — lazy. Ideal para **cadeias de fallback**.

```java
Optional<User> user = cache.find(id)
        .or(() -> localDb.findById(id))
        .or(() -> remoteService.fetch(id));
```

| Método | Recebe | Retorna | Uso |
|---|---|---|---|
| `orElse(T)` | valor | `T` | termina a cadeia com um valor padrão |
| `orElseGet(Supplier<T>)` | supplier de valor | `T` | termina a cadeia com valor padrão lazy |
| `or(Supplier<Optional<T>>)` | supplier de Optional | `Optional<T>` | **continua** a cadeia com outra fonte opcional |

**Java 8 (sem `or`):**

```java
Optional<User> user = cache.find(id);
if (user.isEmpty()) user = localDb.findById(id);   // ou:
Optional<User> u2 = Stream.<Supplier<Optional<User>>>of(
        () -> cache.find(id), () -> localDb.findById(id), () -> remote.fetch(id))
    .map(Supplier::get).filter(Optional::isPresent).map(Optional::get).findFirst();
```

### 3.10 Interop: `stream()` (Java 9+)

Converte em `Stream` de 0 ou 1 elemento. O uso principal é **remover vazios de um stream de Optionals**:

```java
List<User> found = ids.stream()
        .map(repo::findById)          // Stream<Optional<User>>
        .flatMap(Optional::stream)    // Stream<User>, vazios descartados
        .toList();                    // Java 16+
```

Java 8 equivalente: `.filter(Optional::isPresent).map(Optional::get)`.

### 3.11 `equals`, `hashCode`, `toString`

```java
Optional.of("a").equals(Optional.of("a"));      // true
Optional.empty().equals(Optional.empty());      // true
Optional.of("a").toString();                    // "Optional[a]"
Optional.empty().toString();                    // "Optional.empty"
Optional.of("a") == Optional.of("a");           // ❌ indefinido — value-based (OPT-12)
```

---

## 4. `map` vs `flatMap` vs `filter` vs `or`

### 4.1 Tabela de decisão

| A função que você tem é… | Use |
|---|---|
| `T -> U` (U não-Optional, pode ser null) | `map` |
| `T -> Optional<U>` | `flatMap` |
| `T -> boolean` | `filter` |
| `() -> Optional<T>` (fonte alternativa) | `or` |
| `() -> T` (valor padrão) | `orElseGet` |
| `T -> void` (efeito colateral) | `ifPresent` / `ifPresentOrElse` |
| `() -> Exception` | `orElseThrow(supplier)` |

### 4.2 Sintoma: `Optional<Optional<T>>`

Se o tipo inferido virar `Optional<Optional<T>>`, você usou `map` onde devia usar `flatMap`.
Nunca "desembrulhe" com `.get().get()` ou `.orElse(Optional.empty())`.

```java
// ❌
Optional<Optional<Address>> x = user.map(User::getAddress);
Optional<Address> y = x.orElse(Optional.empty());
// ✅
Optional<Address> z = user.flatMap(User::getAddress);
```

### 4.3 Combinando dois Optionals (zip)

Não há `zip` na API. Use `flatMap` + `map`:

```java
Optional<Money> total = priceOf(item).flatMap(price ->
                        quantityOf(item).map(qty -> price.times(qty)));
```

Para 3+ valores isso fica ilegível — prefira guard clauses com `isEmpty()` / `orElseThrow()` ou um
método auxiliar.

### 4.4 Variância de tipos

`Optional<Dog>` **não** é `Optional<Animal>` (generics são invariantes):

```java
Optional<Dog> dog = findDog();
Optional<Animal> a1 = dog;                          // ❌ não compila
Optional<Animal> a2 = dog.map(d -> d);              // ✅ (ou .map(Animal.class::cast))
Optional<? extends Animal> a3 = dog;                // ✅ se só for ler
Optional<Animal> a4 = Optional.<Animal>empty().or(() -> dog);   // ✅ Java 9+ (wildcard em or)
```

---

## 5. Optional como ferramenta de null safety

### 5.1 O que Optional resolve

- **Torna a ausência parte do contrato** (assinatura), visível no tipo, no IDE e no Javadoc.
- **Força uma decisão** no chamador: não há como obter `T` sem escolher o que fazer quando vazio.
- **Elimina cadeias de `if (x != null)`** ao navegar por resultados opcionais (`map`/`flatMap`).
- **Valor presente nunca é null** — dentro de `map`/`filter`/`ifPresent` o argumento é garantidamente não-nulo.

### 5.2 O que Optional **não** resolve

- A própria referência `Optional` pode ser `null` (o compilador não impede) → OPT-02.
- Não protege **campos, parâmetros e elementos de coleção** — e não deve ser usado neles (OPT-03).
- Não substitui validação de entrada (`Objects.requireNonNull` em construtores/parâmetros).
- Não é uma solução de *null safety* do sistema de tipos (como Kotlin `T?`).

### 5.3 Estratégia completa de null safety em Java moderno

Optional é **uma** peça. Combine:

| Local | Ferramenta recomendada |
|---|---|
| **Retorno** que pode não existir | `Optional<T>` (ou coleção vazia, para múltiplos) |
| **Parâmetro** obrigatório | `Objects.requireNonNull(param, "param")` no início do método/construtor |
| **Parâmetro** opcional | Sobrecarga de método, builder, ou `@Nullable` |
| **Campo** opcional | Campo nullable (anotado `@Nullable`) + getter retornando `Optional` |
| **Default para valor possivelmente null** | `Objects.requireNonNullElse(x, def)` / `requireNonNullElseGet(x, supplier)` (Java 9+) |
| **Código inteiro** | Anotações JSpecify (`@NullMarked`, `@Nullable`) + verificador estático (NullAway, IntelliJ, Checker Framework) |
| **Mapas** | `getOrDefault`, `computeIfAbsent`, `Map.of` (rejeita null) |
| **Coleções** | `List.of`/`Set.of`/`Map.of` (rejeitam null), retornar vazio em vez de null |

### 5.4 Padrão "fronteira" (boundary)

Converta `null` ↔ `Optional` **somente nas bordas** do seu código:

```java
// Entrada: API legada retorna null → converta imediatamente
public Optional<Customer> findCustomer(String doc) {
    return Optional.ofNullable(legacyCrm.lookup(doc));
}

// Saída: API externa exige null → converta no último momento
legacyReport.setManagerName(employee.getManager().map(Manager::name).orElse(null));
```

Dentro do núcleo, trabalhe com valores não-nulos e `Optional` só em retornos.

### 5.5 Optional vs alternativas para null-checks simples

```java
// Dado: String input pode ser null; quero um default
String a = input != null ? input : "default";                 // ✅ claro
String b = Objects.requireNonNullElse(input, "default");      // ✅ Java 9+, mais claro ainda
String c = Optional.ofNullable(input).orElse("default");      // ⚠️ aceitável, mas OPT-09: cria Optional só para um default

// Já com transformação, Optional ganha:
String d = Optional.ofNullable(input).map(String::trim).filter(s -> !s.isEmpty()).orElse("default"); // ✅
```

> Stuart Marks (regra 4): criar um Optional apenas para encadear métodos e obter um valor é, em geral,
> má ideia. A regra prática: se a cadeia é só `ofNullable(x).orElse(y)`,
> use `Objects.requireNonNullElse`. Se há `map`/`filter`/`flatMap` no meio, Optional se paga.

---

## 6. Boas práticas

### BP-01 — Retorne Optional de métodos de busca/consulta que podem não ter resultado

```java
Optional<User> findByEmail(String email);
Optional<Config> loadOverride(Path path);
OptionalInt indexOf(String token);
```

### BP-02 — Getters de campos opcionais: armazene nullable, exponha Optional

```java
public class Employee {
    private final String name;
    private final @Nullable Employee manager;   // campo nullable, não Optional

    public Optional<Employee> getManager() {
        return Optional.ofNullable(manager);
    }
}
```

> **Records:** componentes de record viram accessors automáticos. Duas abordagens:
> (a) componente nullable + método extra `Optional<X> xOpt()` ; ou
> (b) componente `Optional<X>` — controverso, pois viola OPT-03 (é campo e parâmetro do construtor).
> **Recomendado:** (a). Se optar por (b) em DTOs internos, valide no construtor compacto que o
> componente não é `null`: `Objects.requireNonNull(manager)` (e use `Optional.empty()`).

### BP-03 — Prefira cadeias declarativas a condicionais imperativas

```java
return repo.findById(id)
           .filter(User::isActive)
           .map(mapper::toDto)
           .orElseThrow(() -> new NotFoundException("user", id));
```

### BP-04 — Uma operação por linha em cadeias longas

Facilita leitura, diffs e stack traces. Extraia lambdas grandes para métodos nomeados
(`.map(this::toInvoiceDto)` em vez de lambda de 15 linhas).

### BP-05 — Exceções de domínio em `orElseThrow`

```java
.orElseThrow(() -> new OrderNotFoundException(orderId))   // ✅ mensagem e tipo significativos
.orElseThrow()                                            // ✅ só quando ausência = bug
```

### BP-06 — Use `orElseGet` para defaults computados (OPT-07)

### BP-07 — Use `or()` para fallback entre fontes (Java 9+)

### BP-08 — Use `Optional::stream` para filtrar vazios em streams (Java 9+)

### BP-09 — Documente no Javadoc o que significa "vazio"

```java
/**
 * @return o desconto aplicável, ou {@link Optional#empty()} se o pedido não atinge o valor mínimo
 */
Optional<Discount> discountFor(Order order);
```

### BP-10 — Não retorne Optional de métodos que sempre têm valor

Se o método nunca retorna vazio, `Optional` é ruído e induz o chamador a tratar um caso impossível.

### BP-11 — Em interfaces públicas/bibliotecas, Optional no retorno é ótimo; em hot paths internos, pondere o custo ([§12](#12-performance))

### BP-12 — Mantenha lambdas puros em `map`/`filter`/`flatMap`

Efeitos colaterais vão em `ifPresent`/`ifPresentOrElse`, nunca em `map` ou `filter`.

---

## 7. Catálogo de antipatterns

Cada item: **sintoma → por que é ruim → correção**.

<a id="ap-01"></a>
### AP-01 — `isPresent()` + `get()` (o "null check com passos extras")

```java
// ❌
Optional<User> u = repo.findById(id);
if (u.isPresent()) {
    return u.get().getEmail();
} else {
    return "n/a";
}
// ✅
return repo.findById(id).map(User::getEmail).orElse("n/a");
```
Por quê: reproduz exatamente o `if (x != null)` que Optional veio substituir, com mais cerimônia, e
mantém o `get()` perigoso no código.

<a id="ap-02"></a>
### AP-02 — `get()` sem prova de presença

```java
// ❌ NoSuchElementException em produção
String email = repo.findById(id).get().getEmail();
// ✅
String email = repo.findById(id).map(User::getEmail)
                   .orElseThrow(() -> new UserNotFoundException(id));
```

<a id="ap-03"></a>
### AP-03 — Retornar `null` de um método que retorna Optional

```java
// ❌ quebra o contrato; o chamador fará NPE em .map()
public Optional<User> find(String id) {
    if (id == null) return null;
    ...
}
// ✅
if (id == null) return Optional.empty();
```

<a id="ap-04"></a>
### AP-04 — Optional como campo

```java
// ❌ não é Serializable, custa memória, JPA/Jackson antigos não entendem, e o próprio campo pode ser null
class Customer { private Optional<String> phone; }
// ✅
class Customer {
    private @Nullable String phone;
    public Optional<String> getPhone() { return Optional.ofNullable(phone); }
}
```

<a id="ap-05"></a>
### AP-05 — Optional como parâmetro de método/construtor

```java
// ❌ o chamador precisa embrulhar; ainda pode passar null; 3 estados (null, empty, present)
void send(Email email, Optional<Attachment> attachment)
send(email, Optional.empty());
// ✅ sobrecarga
void send(Email email)                         { send(email, List.of()); }
void send(Email email, Attachment attachment)  { ... }
// ✅ ou @Nullable para parâmetros genuinamente opcionais em métodos privados
```
Exceção pragmática: *endpoints* de frameworks que fazem binding de parâmetro opcional
(`@RequestParam Optional<String> q` no Spring MVC) — aqui o framework constrói o Optional,
nunca é null, e o uso é idiomático.

<a id="ap-06"></a>
### AP-06 — Optional envolvendo coleção, array ou stream

```java
// ❌ dois jeitos de dizer "nada": empty() e lista vazia
Optional<List<Order>> findOrders(String customerId);
// ✅
List<Order> findOrders(String customerId);   // retorna List.of() se não houver
```

<a id="ap-07"></a>
### AP-07 — Optional em coleções ou como valor de Map

```java
// ❌
List<Optional<User>> users;
Map<String, Optional<Price>> prices;
// ✅ filtre os vazios; para Map, ausência da chave já significa "sem valor"
List<User> users = optionals.stream().flatMap(Optional::stream).toList();
Map<String, Price> prices;   // use prices.get(k) → Optional.ofNullable(prices.get(k)) na consulta
```

<a id="ap-08"></a>
### AP-08 — `orElse` com chamada cara ou com efeito colateral

```java
// ❌ salva no banco mesmo quando o usuário existe
repo.findByEmail(email).orElse(repo.save(new User(email)));
// ✅
repo.findByEmail(email).orElseGet(() -> repo.save(new User(email)));
```

<a id="ap-09"></a>
### AP-09 — `Optional.ofNullable(x).isPresent()` / `.isEmpty()` em vez de comparação

```java
// ❌
if (Optional.ofNullable(name).isPresent()) { ... }
// ✅
if (name != null) { ... }
```

<a id="ap-10"></a>
### AP-10 — Optional criado só para fornecer default (ver OPT-09)

```java
// ⚠️
String s = Optional.ofNullable(value).orElse("x");
// ✅
String s = Objects.requireNonNullElse(value, "x");
```

<a id="ap-11"></a>
### AP-11 — `Optional<Optional<T>>` (map onde devia ser flatMap) — ver [§4.2](#42-sintoma-optionaloptionalt)

<a id="ap-12"></a>
### AP-12 — Efeitos colaterais em `map`/`filter`

```java
// ❌ map usado como "forEach"; resultado descartado
opt.map(u -> { audit.log(u); return u; });
// ✅
opt.ifPresent(audit::log);
```

<a id="ap-13"></a>
### AP-13 — Optional para controle de fluxo / substituto de `if` em tudo

```java
// ❌ não há ausência no contrato — é só um boolean disfarçado
Optional.of(order).filter(Order::isPaid).ifPresent(this::ship);
// ✅
if (order.isPaid()) ship(order);
```

<a id="ap-14"></a>
### AP-14 — Operações de identidade sobre Optional (value-based)

```java
// ❌
if (opt == Optional.empty()) { ... }
synchronized (opt) { ... }
// ✅
if (opt.isEmpty()) { ... }
```

<a id="ap-15"></a>
### AP-15 — `Optional<Boolean>` / `Optional<Integer>` para estados

`Optional<Boolean>` cria lógica de três estados confusa (empty/true/false). Modele com `enum`.
`Optional<Integer>`/`Long`/`Double` → use os tipos primitivos (`OptionalInt`…), [§9](#9-optionals-primitivos-optionalint-optionallong-optionaldouble).

<a id="ap-16"></a>
### AP-16 — `Optional.of()` com valor possivelmente null

```java
// ❌ NPE se map.get retornar null
Optional.of(map.get(key));
// ✅
Optional.ofNullable(map.get(key));
```

<a id="ap-17"></a>
### AP-17 — `ofNullable` com valor que nunca é null

Esconde a premissa e desativa o fail-fast. Use `of()` (OPT-08).

<a id="ap-18"></a>
### AP-18 — Capturar `NoSuchElementException` em vez de tratar a ausência

```java
// ❌
try { return opt.get(); } catch (NoSuchElementException e) { return fallback; }
// ✅
return opt.orElse(fallback);
```

<a id="ap-19"></a>
### AP-19 — `orElse(null)` seguido de null-check

```java
// ❌ volta ao mundo null sem motivo
User u = repo.findById(id).orElse(null);
if (u != null) { notify(u); }
// ✅
repo.findById(id).ifPresent(this::notify);
```

<a id="ap-20"></a>
### AP-20 — Optional em getters de entidades JPA mapeadas por propriedade / em DTOs de serialização sem suporte

Ver [§11](#11-optional-em-frameworks-e-bibliotecas). Com *access type* `PROPERTY`, o provider tenta
mapear o tipo `Optional`. Use acesso por campo (`@Id` no campo) ou não exponha Optional no getter mapeado.

<a id="ap-21"></a>
### AP-21 — `filter(...).isPresent()` em vez de expressão booleana

```java
// ❌
boolean adult = Optional.of(user).filter(u -> u.age() >= 18).isPresent();
// ✅
boolean adult = user.age() >= 18;
// ✅ (quando o Optional já existe, de um retorno)
boolean adult = repo.findById(id).filter(u -> u.age() >= 18).isPresent();   // ok
boolean adult = repo.findById(id).map(u -> u.age() >= 18).orElse(false);    // equivalente
```

<a id="ap-22"></a>
### AP-22 — Lambdas gigantes dentro da cadeia

Cadeias com lambdas de várias linhas perdem a vantagem de legibilidade. Extraia métodos privados
nomeados e use referência de método.

---

## 8. Catálogo de refactoring (oportunidades de usar a API)

Cada receita: **padrão a procurar → forma refatorada**. Útil para skills de refactoring automático.

<a id="rf-01"></a>
### RF-01 — Método que retorna `null` para "não encontrado" → `Optional`

```java
// Antes
public User findByEmail(String email) {
    for (User u : users) if (u.getEmail().equals(email)) return u;
    return null;
}
// Depois
public Optional<User> findByEmail(String email) {
    return users.stream().filter(u -> u.getEmail().equals(email)).findFirst();
}
```
> Mudança de assinatura pública é **breaking change** — atualize todos os chamadores no mesmo PR
> ou introduza um novo método e deprecie o antigo.

<a id="rf-02"></a>
### RF-02 — Null-checks aninhados → cadeia de `map`

```java
// Antes
String city = "UNKNOWN";
if (order != null) {
    Customer c = order.getCustomer();
    if (c != null) {
        Address a = c.getAddress();
        if (a != null && a.getCity() != null) {
            city = a.getCity();
        }
    }
}
// Depois
String city = Optional.ofNullable(order)
        .map(Order::getCustomer)
        .map(Customer::getAddress)
        .map(Address::getCity)
        .orElse("UNKNOWN");
```

<a id="rf-03"></a>
### RF-03 — `isPresent()` + `get()` → `map`/`orElse` (ver AP-01)

<a id="rf-04"></a>
### RF-04 — `isPresent()` + `get()` + `throw` → `orElseThrow`

```java
// Antes
Optional<Order> o = repo.findById(id);
if (!o.isPresent()) throw new OrderNotFoundException(id);
Order order = o.get();
// Depois
Order order = repo.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
```

<a id="rf-05"></a>
### RF-05 — `if/else` com retorno em ambos os ramos → `map().orElseGet()`

```java
// Antes
Optional<User> u = repo.findById(id);
if (u.isPresent()) {
    return ResponseEntity.ok(mapper.toDto(u.get()));
}
return ResponseEntity.notFound().build();
// Depois
return repo.findById(id)
           .map(mapper::toDto)
           .map(ResponseEntity::ok)
           .orElseGet(() -> ResponseEntity.notFound().build());
```

<a id="rf-06"></a>
### RF-06 — `if (isPresent) {efeito}` → `ifPresent`

```java
// Antes
if (opt.isPresent()) { publisher.publish(opt.get()); }
// Depois
opt.ifPresent(publisher::publish);
```

<a id="rf-07"></a>
### RF-07 — `if/else` só com efeitos → `ifPresentOrElse` (Java 9+)

```java
// Antes
if (opt.isPresent()) cache.put(key, opt.get()); else metrics.miss(key);
// Depois
opt.ifPresentOrElse(v -> cache.put(key, v), () -> metrics.miss(key));
```

<a id="rf-08"></a>
### RF-08 — `if (isPresent && condição)` → `filter`

```java
// Antes
if (u.isPresent() && u.get().isActive()) { grantAccess(u.get()); }
// Depois
u.filter(User::isActive).ifPresent(this::grantAccess);
```

<a id="rf-09"></a>
### RF-09 — Cadeia de tentativas com `if (result == null)` → `or()` (Java 9+)

```java
// Antes
User u = cache.get(id);
if (u == null) u = db.find(id);          // retorna null
if (u == null) u = remote.fetch(id);     // retorna null
// Depois (assumindo métodos já retornando Optional)
Optional<User> u = cache.find(id).or(() -> db.find(id)).or(() -> remote.fetch(id));
```

<a id="rf-10"></a>
### RF-10 — `.filter(Optional::isPresent).map(Optional::get)` → `.flatMap(Optional::stream)` (Java 9+)

<a id="rf-11"></a>
### RF-11 — `get()` → `orElseThrow()` (Java 10+)

Substituição mecânica, semântica idêntica, nome honesto. Seguro em refactoring automatizado.

<a id="rf-12"></a>
### RF-12 — `!opt.isPresent()` → `opt.isEmpty()` (Java 11+)

<a id="rf-13"></a>
### RF-13 — `orElse(computacao())` → `orElseGet(() -> computacao())`

Seguro sempre (só muda quando o argumento é avaliado). Obrigatório se há efeito colateral.
Para literais/constantes, o inverso (`orElseGet(() -> "x")` → `orElse("x")`) é uma simplificação válida.

<a id="rf-14"></a>
### RF-14 — `map(...)` retornando Optional + `orElse(Optional.empty())` → `flatMap`

<a id="rf-15"></a>
### RF-15 — `Optional.ofNullable(x).orElse(d)` simples → `Objects.requireNonNullElse(x, d)` (Java 9+)

<a id="rf-16"></a>
### RF-16 — `Optional.ofNullable(map.get(k)).orElse(d)` → `map.getOrDefault(k, d)`

> ⚠️ Não é 100% equivalente: se a chave existe **mapeada para `null`**, `getOrDefault` retorna `null`
> e a versão com Optional retorna `d`. Só aplique se o mapa não contém valores null
> (ex.: `Map.of`, `ConcurrentHashMap`, ou invariante do domínio).

<a id="rf-17"></a>
### RF-17 — Loop de busca manual → `stream().filter().findFirst()` / `findAny()` / `max()` / `min()`

```java
// Antes
Product cheapest = null;
for (Product p : products) {
    if (cheapest == null || p.price().compareTo(cheapest.price()) < 0) cheapest = p;
}
// Depois
Optional<Product> cheapest = products.stream().min(Comparator.comparing(Product::price));
```

<a id="rf-18"></a>
### RF-18 — Campo `Optional` → campo nullable + getter Optional (ver AP-04)

<a id="rf-19"></a>
### RF-19 — Parâmetro `Optional` → sobrecarga (ver AP-05)

<a id="rf-20"></a>
### RF-20 — `Optional<List<T>>` → `List<T>` vazia (ver AP-06)

<a id="rf-21"></a>
### RF-21 — `Optional<Integer>` → `OptionalInt` em APIs de alto volume (ver §9)

<a id="rf-22"></a>
### RF-22 — `orElse(null)` + `if != null` → `ifPresent` (ver AP-19)

### 8.1 Quando **não** refatorar para Optional

- Hot paths com milhões de chamadas/segundo onde alocações importam (meça antes — [§12](#12-performance)).
- Quando a cadeia resultante fica **menos** legível que o `if` original (ex.: precisa de `return`/`break`
  no meio, exceções checked em lambdas, 3+ Optionals combinados).
- Campos, parâmetros e coleções (OPT-03/04).
- Código que precisa compilar em Java 7 ou anterior (Android antigo).

---

## 9. Optionals primitivos (`OptionalInt`, `OptionalLong`, `OptionalDouble`)

Evitam boxing. São retornados por `IntStream.max()`, `min()`, `average()` (→ `OptionalDouble`),
`findFirst()`, `reduce(IntBinaryOperator)`, etc.

| Método | `Optional<T>` | `OptionalInt` (idem Long/Double) |
|---|---|---|
| `empty()`, `of()` | ✅ | ✅ |
| `ofNullable()` | ✅ | ❌ (primitivo não é null) |
| `isPresent()`, `isEmpty()` (11) | ✅ | ✅ |
| `get()` | ✅ | `getAsInt()` / `getAsLong()` / `getAsDouble()` |
| `orElse`, `orElseGet`, `orElseThrow()` (10), `orElseThrow(Supplier)` | ✅ | ✅ (com `IntSupplier` etc.) |
| `ifPresent`, `ifPresentOrElse` (9) | ✅ | ✅ (com `IntConsumer` etc.) |
| `stream()` (9) | ✅ | ✅ (`IntStream`) |
| `map`, `flatMap`, `filter`, `or` | ✅ | ❌ **não existem** |

```java
OptionalInt max = IntStream.of(3, 9, 4).max();      // OptionalInt[9]
int value = max.orElse(0);
OptionalDouble avg = orders.stream().mapToDouble(Order::total).average();
String label = avg.isPresent() ? "%.2f".formatted(avg.getAsDouble()) : "n/a";

// Como não há map: converta via stream() ou boxe conscientemente
Optional<String> s = max.stream().mapToObj(Integer::toString).findFirst();
```

> Effective Java (Item 55): nunca retorne `Optional<Integer>`/`Long`/`Double` — use as versões primitivas.
> Para os demais boxed (`Boolean`, `Short`, `Byte`, `Character`, `Float`) é aceitável `Optional<Boxed>`.

---

## 10. Optional e Streams

### 10.1 Operações de Stream que retornam Optional

| Operação | Retorno |
|---|---|
| `findFirst()`, `findAny()` | `Optional<T>` |
| `min(Comparator)`, `max(Comparator)` | `Optional<T>` |
| `reduce(BinaryOperator)` (sem identidade) | `Optional<T>` |
| `IntStream/LongStream/DoubleStream` `min/max/findFirst/findAny/reduce` | `OptionalInt/Long/Double` |
| `average()` | `OptionalDouble` |
| `Collectors.minBy`, `maxBy`, `reducing(BinaryOperator)` | `Collector<…, Optional<T>>` |

> `findFirst()`/`findAny()`/`min`/`max` lançam **NPE** se o elemento selecionado for `null`.
> Filtre nulls antes: `.filter(Objects::nonNull)`.

### 10.2 Padrões

```java
// Descartar vazios (Java 9+)
List<Address> addresses = users.stream().map(User::getAddress).flatMap(Optional::stream).toList();

// Agrupar e pegar o máximo por grupo, sem Optional no Map resultante
Map<String, Order> biggestByCustomer = orders.stream().collect(
    Collectors.toMap(Order::customerId, Function.identity(),
                     BinaryOperator.maxBy(Comparator.comparing(Order::total))));

// Se usar groupingBy + maxBy, desembrulhe com collectingAndThen
Map<String, Order> biggest = orders.stream().collect(Collectors.groupingBy(
    Order::customerId,
    Collectors.collectingAndThen(
        Collectors.maxBy(Comparator.comparing(Order::total)),
        Optional::orElseThrow)));   // seguro: grupo nunca é vazio

// Stream a partir de Optional, para reutilizar operações de stream
long count = opt.stream().filter(x -> x.isValid()).count();
```

---

## 11. Optional em frameworks e bibliotecas

| Contexto | Suporte / Recomendação |
|---|---|
| **Spring Data** (JPA, Mongo, etc.) | `CrudRepository.findById` retorna `Optional<T>`; métodos derivados (`findByEmail`) podem declarar `Optional<T>` como retorno. ✅ Uso canônico. |
| **Spring MVC** | `@RequestParam Optional<String>`, `@PathVariable Optional<…>`, `@RequestHeader Optional<…>` suportados. Exceção aceita ao AP-05. |
| **Spring DI** | Injeção `Optional<Bean>` suportada; `ObjectProvider<Bean>` é mais rico (`getIfAvailable`, `ifAvailable`). |
| **Jackson** | Jackson 2.x: registrar `Jdk8Module` (`jackson-datatype-jdk8`) — Spring Boot registra automaticamente. Jackson 3.x: suporte embutido no `jackson-databind`, sem registro. Serializa `Optional.empty()` como `null` e presente como o valor. Mesmo com suporte, prefira DTOs sem campos Optional (OPT-03). |
| **JPA / Hibernate** | **Não** use `Optional` como tipo de atributo de entidade. Com acesso por campo, um getter `Optional<X> getX()` é seguro. |
| **Bean Validation** | Suporta *value extraction* de `Optional` (`Optional<@Email String>`), mas isso só importa se você já tem Optional em parâmetros/campos — não é motivo para adotá-lo. |
| **Serialização Java** | `Optional` não é `Serializable` → `NotSerializableException` em campos (OPT-13). |
| **Kotlin interop** | Kotlin trata `Optional` como tipo comum; prefira `T?` no lado Kotlin e converta (`.orElse(null)`, `getOrNull()` do stdlib JDK8). |
| **Vavr / Guava** | `io.vavr.control.Option` (completo, serializável) e `com.google.common.base.Optional` (legado, pré-Java 8). Não misture com `java.util.Optional` sem necessidade; Guava recomenda migrar para `java.util.Optional`. |

---

## 12. Performance

- Cada `Optional` presente é uma **alocação** no heap (≈16 bytes de header+referência). `Optional.empty()` é um singleton.
- Em código "frio" (serviços, controllers, regras de negócio), o custo é **desprezível** frente a I/O.
- O JIT frequentemente elimina a alocação por **escape analysis** quando o Optional não escapa do método
  (cadeias curtas inline). Não é garantido.
- Em **hot loops** (parsing, processamento numérico, estruturas de dados de baixo nível), prefira
  sentinelas, `null` documentado e encapsulado, ou `OptionalInt` etc. **Meça com JMH** antes de otimizar.
- `Optional<Integer>` acumula **duas** indireções (Optional + Integer) — use `OptionalInt` (OPT-11).
- Campos `Optional` multiplicam o consumo de memória de objetos numerosos (AP-04).
- `orElse(caro())` desperdiça CPU sempre (AP-08).

---

## 13. Testando código com Optional

### JUnit 5

```java
assertEquals(Optional.of("ana@x.com"), service.emailOf("1"));   // equals estrutural funciona
assertTrue(service.emailOf("missing").isEmpty());
assertThrows(UserNotFoundException.class, () -> service.load("missing"));
```

### AssertJ (mais expressivo)

```java
assertThat(service.emailOf("1")).isPresent().contains("ana@x.com");
assertThat(service.emailOf("1")).hasValue("ana@x.com");
assertThat(service.emailOf("1")).hasValueSatisfying(e -> assertThat(e).endsWith("@x.com"));
assertThat(service.emailOf("missing")).isEmpty();
assertThat(repo.findById("1")).get().extracting(User::getEmail).isEqualTo("ana@x.com");
assertThat(OptionalInt.of(3)).hasValue(3);
```

### Mockito

```java
when(repo.findById("1")).thenReturn(Optional.of(user));
when(repo.findById("x")).thenReturn(Optional.empty());
```
Mockito 2+ retorna `Optional.empty()` por padrão (RETURNS_DEFAULTS) para métodos que retornam
Optional/Stream não *stubbed* — não é necessário mockar o caso vazio, mas fazê-lo explicita a intenção.

### O que testar

1. Caminho presente; 2. caminho vazio; 3. que o método **nunca** retorna `null`;
4. que `orElseGet`/`orElseThrow` não executam efeitos quando presente.

---

## 14. Árvore de decisão

```text
Preciso representar "pode não haver valor"?
│
├── É um RETORNO de método?
│   ├── Retorna múltiplos valores (List/Set/Map/array/Stream)? ──► Retorne coleção VAZIA (não Optional)
│   ├── É int/long/double? ──────────────────────────────────────► OptionalInt / OptionalLong / OptionalDouble
│   ├── Hot path medido como crítico? ───────────────────────────► null documentado / sentinela (encapsulado)
│   └── Caso geral ──────────────────────────────────────────────► Optional<T>
│
├── É um CAMPO? ─────────► Campo nullable (@Nullable) + getter que retorna Optional<T>
├── É um PARÂMETRO? ─────► Sobrecarga / builder / @Nullable (nunca Optional — exceto binding de framework)
├── É ELEMENTO de coleção / valor de Map? ──► Não armazene; filtre vazios / ausência da chave
└── É uma variável local com default simples? ──► ternário / Objects.requireNonNullElse

Tenho um Optional<T> e quero…
├── transformar com T → U ..................... map
├── transformar com T → Optional<U> ........... flatMap
├── descartar se não satisfaz condição ........ filter
├── tentar outra fonte Optional ............... or            (9+)
├── valor padrão constante .................... orElse
├── valor padrão computado / com efeito ....... orElseGet
├── falhar com exceção de domínio ............. orElseThrow(() -> new X(...))
├── falhar (ausência = bug) ................... orElseThrow() (10+)
├── efeito se presente ........................ ifPresent
├── efeito em ambos os casos .................. ifPresentOrElse (9+)
├── usar em um Stream ......................... stream()      (9+)
├── saber se existe ........................... isPresent / isEmpty (11+)
└── passar para API legada que aceita null .... orElse(null)
```

---

## 15. Checklist de code review

- [ ] Nenhum método com retorno `Optional` retorna `null` (OPT-02 / AP-03).
- [ ] Nenhum `get()`; `orElseThrow()` usado somente quando a ausência é impossível (OPT-05 / AP-02).
- [ ] Nenhum par `isPresent()` + `get()` substituível por `map`/`orElse*`/`ifPresent` (AP-01).
- [ ] Nenhum campo, parâmetro, elemento de coleção ou valor de Map do tipo `Optional` (OPT-03; exceções de framework justificadas).
- [ ] Nenhum `Optional<List/Set/Map/array/Stream>` (OPT-04 / AP-06).
- [ ] `orElse` só com constantes/valores prontos; computação → `orElseGet` (OPT-07 / AP-08).
- [ ] `Optional.of` apenas com valores comprovadamente não-nulos; `ofNullable` na fronteira (OPT-08).
- [ ] Nenhum `Optional<Optional<T>>`; `flatMap` usado onde a função retorna Optional (OPT-10).
- [ ] `Optional<Integer|Long|Double>` substituído por versões primitivas em APIs (OPT-11).
- [ ] Nenhum `==`, `synchronized` ou identidade sobre Optional (OPT-12).
- [ ] Nenhum efeito colateral em `map`/`filter`/`flatMap` (BP-12 / AP-12).
- [ ] Cadeias legíveis: uma operação por linha, lambdas longos extraídos (BP-04 / AP-22).
- [ ] Optional não criado só para fornecer default ou substituir `if` simples (OPT-09 / AP-10 / AP-13).
- [ ] Javadoc descreve o significado de "vazio" (BP-09).
- [ ] Exceções em `orElseThrow` são de domínio e com mensagem útil (BP-05).
- [ ] Testes cobrem caminhos presente e vazio (§13).

---

## 16. Tabela de detecção (ferramentas estáticas)

Para quem cria rules automatizadas: padrões e as ferramentas que já os detectam.

| ID deste guia | Padrão detectável | Regras verificadas (ID / nome) |
|---|---|---|
| AP-02 | `get()` sem verificação | SonarJava **S3655** *"Optional value should only be accessed after calling isPresent()"* · IntelliJ `OptionalGetWithoutIsPresent` |
| AP-03 | `null` atribuído/retornado/comparado com `Optional` | SonarJava **S2789** *"\"null\" should not be used with \"Optional\""* · IntelliJ `OptionalAssignedToNull` |
| AP-04, AP-05 | Campo ou parâmetro `Optional` | SonarJava **S3553** *"\"Optional\" should not be used for parameters"* · IntelliJ `OptionalUsedAsFieldOrParameterType` |
| AP-06 | `Optional` de coleção/array | SonarJava **S9404** *"\"Optional\" should not wrap collections, maps, or arrays"* · IntelliJ `OptionalContainsCollection` |
| AP-01, RF-03..08 | `isPresent()` em estilo não funcional | IntelliJ `OptionalIsPresent` (*"Non functional style 'Optional.isPresent()' usage"*) |
| RF-11..14, AP-11 | Cadeias simplificáveis | IntelliJ `SimplifyOptionalCallChains`, `RedundantStreamOptionalCall` |
| RF-02 | Ternário/condicional que pode virar Optional | IntelliJ `ConditionalCanBeOptional` |
| AP-13, AP-22 | Cadeia que seria mais clara como `if` | IntelliJ `OptionalToIf` (quick-fix inverso) |
| AP-16, AP-17 | `ofNullable` com argumento sempre null/não-null | IntelliJ `OptionalOfNullableMisuse` |
| AP-08 | `orElse` com chamada de método | Sem regra Sonar dedicada (há apenas pedido na comunidade); use regex abaixo ou regra custom (Error Prone/PMD/ArchUnit) |
| AP-14 | `synchronized` em value-based | `javac -Xlint:synchronization` (JEP 390, Java 16+) |
| RF-11, RF-12 | `get()` → `orElseThrow()`, `!isPresent()` → `isEmpty()` | Receitas de migração Java 10/11 do OpenRewrite (consulte o catálogo pela versão) |

> IDs Sonar e *shortNames* do IntelliJ verificados no código-fonte de `sonar-java` e `intellij-community`
> (S3655 vive no motor de execução simbólica, fora do repositório open-source). Note que **S6814** trata de
> parâmetros REST do Spring, não de `java.util.Optional`.

### Padrões de busca (regex) para auditoria rápida

```text
\bOptional<[^>]*>\s+\w+\s*[;=]\s*null           # Optional atribuído a null
return\s+null;                                   # em métodos com retorno Optional (filtrar por assinatura)
\.isPresent\(\)\s*\)\s*\{?[^}]*\.get\(\)         # isPresent + get
\.get\(\)                                        # revisar se o receptor é Optional
private\s+(final\s+)?Optional<                   # campo Optional
\(\s*[^)]*Optional<[^>]+>\s+\w+                  # parâmetro Optional
Optional<(List|Set|Map|Collection|Stream)<       # Optional de coleção
Optional<(Integer|Long|Double)>                  # deveria ser primitivo
\.orElse\(\s*\w+(\.\w+)*\(                       # orElse com chamada de método
\.map\([^)]*\)\.orElse\(Optional\.empty\(\)\)    # deveria ser flatMap
Optional\.ofNullable\([^)]*\)\.isPresent\(\)     # null check disfarçado
```

---

## 17. Fontes

### Primárias

1. **Javadoc `java.util.Optional` (Java SE 25)** — https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html
   (contém a *API Note* sobre uso como tipo de retorno e o aviso de *value-based class*)
2. **Javadoc `java.util.Optional` (Java SE 8)** — https://docs.oracle.com/javase/8/docs/api/java/util/Optional.html (API original)
3. **Value-based classes** — https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/doc-files/ValueBased.html
4. **`OptionalInt` / `OptionalLong` / `OptionalDouble`** — https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/OptionalInt.html
5. **`Objects.requireNonNullElse`** (Java 9) — https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Objects.html
6. **Brian Goetz — "Should Java 8 getters return optional type?"** — https://stackoverflow.com/questions/26327957/should-java-8-getters-return-optional-type
7. **Stuart Marks — "Optional: The Mother of All Bikesheds"** (Devoxx Belgium 2016) — slides: https://stuartmarks.wordpress.com/wp-content/uploads/2017/03/optionalmotherofallbikesheds-devoxxbe2016.pdf · recap: https://stuartmarks.wordpress.com/2017/03/18/devoxx-antwerp-2016-recap/
8. **JDK-8140281** — proposta original "deprecate Optional.get()", entregue no JDK 10 como "add no-arg orElseThrow() as preferred alternative to get()" — https://bugs.openjdk.org/browse/JDK-8140281 · thread: https://mail.openjdk.org/pipermail/core-libs-dev/2016-April/040531.html
9. **Código-fonte `Optional.java` (jdk-25+36)** — https://github.com/openjdk/jdk/blob/jdk-25%2B36/src/java.base/share/classes/java/util/Optional.java
10. **JEP 401 — Value Objects (Preview)** — https://openjdk.org/jeps/401
11. **JEP 390 — Warnings for Value-Based Classes** — https://openjdk.org/jeps/390
12. **Joshua Bloch — *Effective Java*, 3ª ed. (2018), Item 55: "Return optionals judiciously"**, Addison-Wesley.

### Ferramentas e ecossistema

13. SonarSource Java rules — https://rules.sonarsource.com/java/ (S3655, S2789, S3553, S9404) · fonte: https://github.com/SonarSource/sonar-java
14. IntelliJ IDEA inspections (fonte) — https://github.com/JetBrains/intellij-community
15. JPA e Optional — https://vladmihalcea.com/the-best-way-to-map-a-java-1-8-optional-entity-attribute-with-jpa-and-hibernate/
16. JSpecify (anotações de nulidade padrão) — https://jspecify.dev/
17. NullAway — https://github.com/uber/NullAway
18. Jackson `jackson-datatype-jdk8` — https://github.com/FasterXML/jackson-modules-java8 · Jackson 3 migration: https://github.com/FasterXML/jackson/blob/main/jackson3/MIGRATING_TO_JACKSON_3.md
19. Spring Data `CrudRepository#findById` — https://docs.spring.io/spring-data/commons/reference/repositories/core-concepts.html
20. AssertJ `OptionalAssert` — https://assertj.github.io/doc/
21. OpenRewrite Java migration recipes — https://docs.openrewrite.org/recipes/java/migrate

### Leitura complementar

22. Nicolai Parlog — "Java 9 Additions To Optional" — https://nipafx.dev/java-9-optional/
23. Baeldung — "Guide To Java Optional" — https://www.baeldung.com/java-optional
