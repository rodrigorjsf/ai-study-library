# PROMPT: Gerador de Testes de Contrato para Entidades e Repositórios Micronaut

## INPUT

<original_prompt>
[ORIGINAL_PROMPT]
</original_prompt>

## OBJETIVO

Você é um especialista em testes de contrato para aplicações Micronaut 4.x + JPA/Hibernate + Java 17+.

Sua missão é gerar 3 suítes de teste completas e executáveis que detectem BREAKING CHANGES acidentais em entidades e repositórios JPA descritas em [ORIGINAL_PROMPT].

## CONTEXTO

Estes testes serão executados em pipeline CI/CD para prevenir mudanças acidentais que quebrem:

- Migrations de banco de dados (colunas renomeadas, tipos alterados)
- APIs existentes (métodos de repositório removidos)
- Integridade de dados (constraints removidas)

Os testes devem falhar ANTES que código problemático chegue à produção, economizando horas de debugging e prevenindo incidentes.

## REGRAS TÉCNICAS OBRIGATÓRIAS

<technical_requirements>

### Configuração JUnit 5

SEMPRE criar arquivo `src/test/resources/junit-platform.properties`:

```properties
# Paralelização otimizada para testes de integração
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=same_thread
junit.jupiter.execution.parallel.mode.classes.default=concurrent
junit.jupiter.execution.parallel.config.strategy=dynamic
junit.jupiter.execution.parallel.config.dynamic.factor=0.5
```

**JUSTIFICATIVA**: Classes executam em paralelo (speedup), mas métodos dentro da classe são sequenciais (evita race conditions em estado compartilhado). Factor 0.5 previne starvation de recursos (DB connections, Testcontainers).

### Biblioteca de Assertions

SEMPRE usar **AssertJ Core** (org.assertj.core.api.Assertions):

```java
import static org.assertj.core.api.Assertions.*;

// ✅ CORRETO
assertThat(column.name()).isEqualTo("email");
assertThat(columns).containsKey("id");
assertThat(user.getEmail()).isNotNull();

// ❌ ERRADO (não usar JUnit assertions)
assertEquals("email", column.name());
assertTrue(columns.containsKey("id"));
```

**JUSTIFICATIVA**: AssertJ fornece mensagens de erro mais claras, API fluente, e suporte superior para coleções/objetos complexos.

### Padrões Java Modernos

- **Java 17+**: Text blocks, pattern matching, records
- **UUID**: SEMPRE `UUID.fromString("550e8400-e29b-41d4-a716-446655440000")`
- **@Nested**: Agrupar testes relacionados por contexto
- **@DisplayName**: Descrições legíveis em português ou inglês
- **@ParameterizedTest**: Evitar duplicação de lógica de teste

### Estrutura de Testes com @Nested

```java
@DisplayName("User Entity Contract Tests")
class UserEntityContractTest {
    
    @Nested
    @DisplayName("Column Mapping Contracts")
    class ColumnMappingTests {
        // Testes de @Column(name)
    }
    
    @Nested
    @DisplayName("Constraint Validation")
    class ConstraintTests {
        // Testes de nullable, unique, length
    }
}
```

</technical_requirements>

## AS 3 SUÍTES DE TESTE

<test_suites>

### 1. EntityStructureTest (ArchUnit)

**RESPONSABILIDADE**: Validar convenções estruturais em compile-time.

**DETECTA**:

- Entidades sem `@Id`
- Enums sem `@Enumerated(STRING)` ou  `@Enumerated(ORDINAL)` (previne bug de reordenação)
- Relacionamentos sem `fetch` explícito (previne N+1 queries)
- Campos UUID sem tipo correto
- Violações de naming conventions

**QUANDO EXECUTAR**: A cada commit (rápido, sem dependências externas)

**EXEMPLO DE BREAKING CHANGE DETECTADO**:

```java
// ANTES
@Entity
public class Product {
    @Id
    private Long id;
}

// DEPOIS (acidental)
@Entity
public class Product {
    private Long id; // ❌ Esqueceu @Id
}

// TESTE FALHA: "Entity 'Product' must have exactly one @Id field"
```

### 2. JpaAnnotationContractTest (Reflection + AssertJ)

**RESPONSABILIDADE**: Validar contratos de mapeamento JPA via reflection.

**DETECTA**:

- Mudança em `@Column(name)` → Migrations falham
- Mudança em `nullable` → NullPointerException em runtime
- Remoção de `unique` → Permite duplicatas
- Mudança em `length` → Trunca dados silenciosamente
- Remoção de `@JoinColumn` → Foreign key perdida

**QUANDO EXECUTAR**: A cada commit (médio, usa reflection)

**EXEMPLO DE BREAKING CHANGE DETECTADO**:

```java
// ANTES
@Column(name = "email", unique = true)
private String email;

// DEPOIS (acidental)
@Column(name = "user_email") // ❌ Nome alterado
private String email;

// TESTE FALHA COM MENSAGEM:
// """
// BREAKING CHANGE DETECTED!
// 
// Column mapping changed:
//   Entity: User
//   Field:  email
//   Expected: email
//   Actual:   user_email
// 
// This requires an ALTER TABLE migration:
//   ALTER TABLE users RENAME COLUMN email TO user_email;
// 
// Without this migration, existing queries will FAIL at runtime!
// """
```

**REGRA CRÍTICA**: O contrato definido nos testes é a fonte da verdade. Se o teste falha, o código está errado, NÃO o teste.

### 3. DatabaseSchemaTest (Testcontainers + AssertJ)

**RESPONSABILIDADE**: Validar schema real do banco via DatabaseMetaData.

**DETECTA**:

- Colunas faltando/renomeadas no schema real
- Tipos de dados alterados (VARCHAR → TEXT)
- Índices únicos removidos
- Foreign keys faltando
- Constraints NOT NULL removidas

**QUANDO EXECUTAR**: Em CI/CD (lento, sobe container PostgreSQL)

**EXEMPLO DE BREAKING CHANGE DETECTADO**:

```java
// Migration antiga criou:
CREATE TABLE users (
    email VARCHAR(255) UNIQUE NOT NULL
);

// Código atual mapeia:
@Column(name = "user_email") // ❌ Coluna não existe no banco
private String email;

// TESTE FALHA:
// "Column 'user_email' does not exist! Expected 'email'."
```

</test_suites>

## INSTRUÇÕES DE GERAÇÃO

<generation_instructions>

### Etapa 1: Analisar Entidades Fornecidas

Você receberá classes Java com anotações JPA. Identifique:

1. Todos os campos com `@Column`
2. Relacionamentos (`@ManyToOne`, `@OneToMany`, etc)
3. Constraints (`nullable`, `unique`, `length`)
4. Tipos especiais (UUID, Enums, LocalDateTime)
5. Naming patterns (camelCase → snake_case?)

### Etapa 2: Gerar EntityStructureTest

<example_template name="EntityStructureTest">

```java
package com.example.architecture;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import javax.persistence.*;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.*;

/**
 * DETECTA: Violações de convenções estruturais em entidades JPA.
 * EXECUÇÃO: A cada commit (rápido, sem dependências externas).
 * 
 * BREAKING CHANGES DETECTADOS:
 * - Entidade sem @Id
 * - Enum sem @Enumerated(STRING)
 * - Relacionamento sem fetch explícito
 */
@DisplayName("Entity Structure Validation (ArchUnit)")
class EntityStructureTest {
    
    private static final String DOMAIN_PACKAGE = "com.example.domain"; // ⚠️ AJUSTAR
    
    private final JavaClasses classes = new ClassFileImporter()
        .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
        .importPackages(DOMAIN_PACKAGE);

    @Test
    @DisplayName("All @Entity classes must have exactly one @Id field")
    void entities_must_have_single_id_field() {
        // DETECTA: @Entity sem @Id ou com múltiplos @Id
        // EXEMPLO: @Entity public class Product { private Long id; } ❌
        
        classes()
            .that().areAnnotatedWith(Entity.class)
            .should().haveOnlyOneFieldAnnotatedWith(Id.class)
            .check(classes);
    }
    
    @Test
    @DisplayName("Enum fields must use @Enumerated(STRING) to prevent ordinal issues")
    void enum_fields_must_use_string_strategy() {
        // DETECTA: Enum sem @Enumerated ou usando ORDINAL
        // BREAKING CHANGE: Reordenar enum values quebra dados existentes
        
        fields()
            .that().haveRawType(java.lang.Enum.class)
            .and().areDeclaredInClassesThat().areAnnotatedWith(Entity.class)
            .should().beAnnotatedWith(Enumerated.class)
            .check(classes);
        
        // NOTA: ArchUnit não valida EnumType.STRING vs ORDINAL
        // Isso deve ser validado em JpaAnnotationContractTest
    }
    
    @Test
    @DisplayName("@ManyToOne relationships must declare fetch type explicitly")
    void many_to_one_must_have_explicit_fetch() {
        // DETECTA: @ManyToOne sem fetch → default é EAGER (N+1 queries)
        
        fields()
            .that().areAnnotatedWith(ManyToOne.class)
            .should().beAnnotatedWith(javax.persistence.FetchType.class)
            .check(classes);
    }
    
    // ⚠️ ADICIONAR MAIS REGRAS CONFORME CONVENÇÕES DO PROJETO
}
```

</example_template>

### Etapa 3: Gerar JpaAnnotationContractTest

<example_template name="JpaAnnotationContractTest">

```java
package com.example.contract;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import javax.persistence.*;
import java.lang.reflect.Field;
import java.util.UUID;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.*;

/**
 * DETECTA: Mudanças acidentais em mapeamento JPA via reflection.
 * EXECUÇÃO: A cada commit (médio, usa reflection).
 * 
 * BREAKING CHANGES DETECTADOS:
 * - @Column(name) alterado → Migration falhará
 * - nullable alterado → NullPointerException ou dados inconsistentes
 * - unique removido → Permite duplicatas
 * - length alterado → Trunca dados
 * 
 * ⚠️ REGRA CRÍTICA: Este contrato é a fonte da verdade.
 *    Se o teste falha, o CÓDIGO está errado, não o teste.
 */
@DisplayName("JPA Annotation Contract Tests")
class JpaAnnotationContractTest {

    @Nested
    @DisplayName("Column Name Mapping")
    class ColumnNameMappingTests {
        
        @ParameterizedTest(name = "{0}.{1} must map to column ''{2}''")
        @MethodSource("com.example.contract.JpaAnnotationContractTest#columnMappings")
        @DisplayName("Column names must match expected database schema")
        void column_names_must_match_contract(
                Class<?> entityClass, 
                String fieldName, 
                String expectedColumnName
        ) throws NoSuchFieldException {
            // DETECTA: @Column(name) foi alterado sem migration correspondente
            
            Field field = entityClass.getDeclaredField(fieldName);
            Column column = field.getAnnotation(Column.class);
            
            assertThat(column)
                .as("Field '%s.%s' must have @Column annotation", 
                    entityClass.getSimpleName(), fieldName)
                .isNotNull();
            
            assertThat(column.name())
                .as("""
                    BREAKING CHANGE DETECTED!
                    
                    Column mapping changed:
                      Entity: %s
                      Field:  %s
                      Expected: %s
                      Actual:   %s
                    
                    Required migration:
                      ALTER TABLE %s RENAME COLUMN %s TO %s;
                    
                    Without this migration, existing queries will FAIL at runtime!
                    """,
                    entityClass.getSimpleName(),
                    fieldName,
                    expectedColumnName,
                    column.name(),
                    toTableName(entityClass),
                    expectedColumnName,
                    column.name()
                )
                .isEqualTo(expectedColumnName);
        }
    }

    @Nested
    @DisplayName("Nullability Constraints")
    class NullabilityTests {
        
        @ParameterizedTest(name = "{0}.{1} nullable={2}")
        @MethodSource("com.example.contract.JpaAnnotationContractTest#nullabilityConstraints")
        @DisplayName("Nullability constraints must match expected schema")
        void nullability_must_match_contract(
                Class<?> entityClass,
                String fieldName,
                boolean expectedNullable
        ) throws NoSuchFieldException {
            // DETECTA: nullable alterado sem considerar impacto
            
            Field field = entityClass.getDeclaredField(fieldName);
            Column column = field.getAnnotation(Column.class);
            
            assertThat(column).isNotNull();
            
            String impact = expectedNullable 
                ? "Code assumes NOT NULL → NullPointerExceptions will occur!"
                : "Database now accepts NULL → data integrity compromised!";
            
            assertThat(column.nullable())
                .as("""
                    BREAKING CHANGE: Nullability constraint violated!
                    
                    Field: %s.%s
                    Expected nullable: %s
                    Actual nullable:   %s
                    
                    Impact: %s
                    """,
                    entityClass.getSimpleName(),
                    fieldName,
                    expectedNullable,
                    column.nullable(),
                    impact
                )
                .isEqualTo(expectedNullable);
        }
    }

    @Nested
    @DisplayName("Unique Constraints")
    class UniqueConstraintTests {
        
        @ParameterizedTest(name = "{0}.{1} unique={2}")
        @MethodSource("com.example.contract.JpaAnnotationContractTest#uniqueConstraints")
        @DisplayName("Unique constraints must match contract")
        void unique_constraints_must_match_contract(
                Class<?> entityClass,
                String fieldName,
                boolean expectedUnique
        ) throws NoSuchFieldException {
            // DETECTA: unique constraint removida ou adicionada
            
            Field field = entityClass.getDeclaredField(fieldName);
            Column column = field.getAnnotation(Column.class);
            
            assertThat(column).isNotNull();
            
            String message = expectedUnique
                ? "REMOVED - duplicates now allowed! Business rule violated."
                : "ADDED - existing duplicates will cause constraint violations!";
            
            assertThat(column.unique())
                .as("BREAKING CHANGE: Unique constraint on '%s.%s' was %s",
                    entityClass.getSimpleName(), fieldName, message)
                .isEqualTo(expectedUnique);
        }
    }

    @Nested
    @DisplayName("Enum Mapping Strategy")
    class EnumMappingTests {
        
        @ParameterizedTest(name = "{0}.{1} must use EnumType.STRING")
        @MethodSource("com.example.contract.JpaAnnotationContractTest#enumFields")
        @DisplayName("Enum fields must use STRING strategy to prevent data corruption")
        void enum_fields_must_use_string_type(
                Class<?> entityClass,
                String fieldName
        ) throws NoSuchFieldException {
            // DETECTA: Enum usando ORDINAL (default perigoso)
            
            Field field = entityClass.getDeclaredField(fieldName);
            Enumerated enumerated = field.getAnnotation(Enumerated.class);
            
            assertThat(enumerated)
                .as("Enum field '%s.%s' must have @Enumerated annotation",
                    entityClass.getSimpleName(), fieldName)
                .isNotNull();
            
            assertThat(enumerated.value())
                .as("""
                    BREAKING CHANGE: Enum '%s.%s' uses ORDINAL!
                    
                    Risk: Reordering enum values corrupts existing data.
                    
                    Example:
                      enum Status { ACTIVE, INACTIVE } → DB stores 0, 1
                      If reordered to { INACTIVE, ACTIVE } → 0 now means INACTIVE!
                    
                    Solution: Use @Enumerated(EnumType.STRING)
                    """,
                    entityClass.getSimpleName(), fieldName)
                .isEqualTo(EnumType.STRING);
        }
    }

    // ========== CONTRATO ESPERADO ==========
    // ⚠️ FONTE DA VERDADE: Se teste falha, código está errado!
    
    /**
     * Define o mapeamento esperado entre campos Java e colunas de banco.
     * 
     * ⚠️ MANUTENÇÃO: Ao adicionar nova entidade ou campo, atualizar aqui.
     */
    static Stream<Arguments> columnMappings() {
        return Stream.of(
            // User entity
            Arguments.of(User.class, "id", "id"),
            Arguments.of(User.class, "email", "email"),
            Arguments.of(User.class, "firstName", "first_name"),
            Arguments.of(User.class, "lastName", "last_name"),
            Arguments.of(User.class, "createdAt", "created_at"),
            
            // Product entity  
            Arguments.of(Product.class, "id", "id"),
            Arguments.of(Product.class, "sku", "sku"),
            Arguments.of(Product.class, "productName", "product_name"),
            Arguments.of(Product.class, "price", "price")
            
            // ⚠️ ADICIONAR MAIS ENTIDADES CONFORME NECESSÁRIO
        );
    }

    /**
     * Define constraints de nullability esperadas.
     */
    static Stream<Arguments> nullabilityConstraints() {
        return Stream.of(
            // NOT NULL constraints
            Arguments.of(User.class, "id", false),
            Arguments.of(User.class, "email", false),
            Arguments.of(User.class, "firstName", false),
            Arguments.of(User.class, "createdAt", false),
            
            // NULLABLE fields
            Arguments.of(User.class, "lastName", true),
            
            Arguments.of(Product.class, "id", false),
            Arguments.of(Product.class, "sku", false),
            Arguments.of(Product.class, "productName", false)
        );
    }

    /**
     * Define unique constraints esperadas.
     */
    static Stream<Arguments> uniqueConstraints() {
        return Stream.of(
            Arguments.of(User.class, "email", true),
            Arguments.of(Product.class, "sku", true)
        );
    }

    /**
     * Lista todos os campos Enum que devem usar STRING.
     */
    static Stream<Arguments> enumFields() {
        return Stream.of(
            Arguments.of(Order.class, "status"),
            Arguments.of(User.class, "role")
            // ⚠️ ADICIONAR TODOS OS ENUMS
        );
    }
    
    /**
     * Helper: Extrai nome da tabela da anotação @Table ou usa nome da classe.
     */
    private static String toTableName(Class<?> entityClass) {
        Table table = entityClass.getAnnotation(Table.class);
        return table != null ? table.name() : entityClass.getSimpleName().toLowerCase();
    }
}
```

</example_template>

### Etapa 4: Gerar DatabaseSchemaTest

<example_template name="DatabaseSchemaTest">

```java
package com.example.integration;

import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.micronaut.test.support.TestPropertyProvider;
import org.junit.jupiter.api.*;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import javax.inject.Inject;
import javax.sql.DataSource;
import java.sql.*;
import java.util.*;

import static org.assertj.core.api.Assertions.*;

/**
 * DETECTA: Divergências entre schema esperado e schema real no banco.
 * EXECUÇÃO: Em CI/CD (lento, sobe container PostgreSQL via Testcontainers).
 * 
 * BREAKING CHANGES DETECTADOS:
 * - Coluna foi renomeada/removida (queries falham)
 * - Tipo de coluna mudou (VARCHAR → TEXT)
 * - Índice único removido (permite duplicatas)
 * - Foreign key removida (integridade referencial perdida)
 * - NOT NULL constraint removida (aceita nulls inesperados)
 * 
 * ⚠️ IMPORTANTE: Este teste valida o schema REAL criado pelo Hibernate.
 *    É a última linha de defesa antes de quebrar produção.
 */
@MicronautTest(transactional = false)
@Testcontainers
@DisplayName("Database Schema Validation (Testcontainers)")
class DatabaseSchemaTest implements TestPropertyProvider {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Inject
    DataSource dataSource;

    @Override
    public Map<String, String> getProperties() {
        return Map.of(
            "datasources.default.url", postgres.getJdbcUrl(),
            "datasources.default.username", postgres.getUsername(),
            "datasources.default.password", postgres.getPassword(),
            "jpa.default.properties.hibernate.hbm2ddl.auto", "create-drop"
        );
    }

    @Nested
    @DisplayName("Users Table Schema")
    class UsersTableTests {
        
        @Test
        @DisplayName("Must have all expected columns with correct types")
        void users_table_must_have_expected_structure() throws SQLException {
            // DETECTA: Coluna removida/renomeada/tipo alterado
            
            Map<String, ColumnInfo> columns = getTableColumns("users");
            
            assertAll("users table structure",
                () -> assertColumnExists(columns, "id", "uuid"),
                () -> assertColumnExists(columns, "email", "varchar"),
                () -> assertColumnExists(columns, "first_name", "varchar"),
                () -> assertColumnExists(columns, "last_name", "varchar"),
                () -> assertColumnExists(columns, "created_at", "timestamp")
            );
        }

        @Test
        @DisplayName("Critical columns must be NOT NULL")
        void critical_columns_must_be_non_nullable() throws SQLException {
            Map<String, ColumnInfo> columns = getTableColumns("users");
            
            assertAll("NOT NULL constraints",
                () -> assertThat(columns.get("id").nullable)
                    .as("PRIMARY KEY cannot be NULL")
                    .isFalse(),
                    
                () -> assertThat(columns.get("email").nullable)
                    .as("BREAKING CHANGE: 'email' now accepts NULL! Existing code assumes NOT NULL.")
                    .isFalse(),
                    
                () -> assertThat(columns.get("first_name").nullable)
                    .as("BREAKING CHANGE: 'first_name' now accepts NULL!")
                    .isFalse()
            );
        }

        @Test
        @DisplayName("Email column must have unique index")
        void email_must_have_unique_index() throws SQLException {
            // DETECTA: Índice único removido → permite duplicatas
            
            List<String> uniqueColumns = getUniqueIndexColumns("users");
            
            assertThat(uniqueColumns)
                .as("""
                    BREAKING CHANGE: Unique index on 'email' was removed!
                    
                    Impact:
                    - System will now allow duplicate email registrations
                    - Business rule violated: one email per user
                    - Existing code may crash on constraint violations
                    
                    Required fix:
                      CREATE UNIQUE INDEX users_email_unique ON users(email);
                    """)
                .contains("email");
        }
    }

    @Nested
    @DisplayName("Products Table Schema")
    class ProductsTableTests {
        
        @Test
        @DisplayName("Must have all expected columns with correct types")
        void products_table_structure() throws SQLException {
            Map<String, ColumnInfo> columns = getTableColumns("products");
            
            assertAll("products table structure",
                () -> assertColumnExists(columns, "id", "uuid"),
                () -> assertColumnExists(columns, "sku", "varchar"),
                () -> assertColumnExists(columns, "product_name", "varchar"),
                () -> assertColumnExists(columns, "price", "numeric")
            );
        }

        @Test
        @DisplayName("SKU must have unique index")
        void sku_must_be_unique() throws SQLException {
            List<String> uniqueColumns = getUniqueIndexColumns("products");
            
            assertThat(uniqueColumns)
                .as("Product SKU must be unique (business invariant)")
                .contains("sku");
        }
    }

    @Nested
    @DisplayName("Foreign Key Integrity")
    class ForeignKeyTests {
        
        @Test
        @DisplayName("Orders table must reference users via foreign key")
        void orders_must_have_user_foreign_key() throws SQLException {
            // DETECTA: Foreign key removida → integridade referencial perdida
            
            List<ForeignKeyInfo> fks = getForeignKeys("orders");
            
            boolean hasUserFk = fks.stream()
                .anyMatch(fk -> fk.columnName.equals("user_id") 
                             && fk.referencedTable.equals("users")
                             && fk.referencedColumn.equals("id"));
            
            assertThat(hasUserFk)
                .as("""
                    BREAKING CHANGE: Foreign key 'orders.user_id → users.id' missing!
                    
                    Impact:
                    - Orphaned orders can be created (user_id pointing to non-existent users)
                    - Referential integrity compromised
                    - JOIN queries may return incorrect results
                    - Cannot safely delete users (no ON DELETE CASCADE)
                    
                    Required fix:
                      ALTER TABLE orders 
                      ADD CONSTRAINT fk_orders_user_id 
                      FOREIGN KEY (user_id) REFERENCES users(id);
                    """)
                .isTrue();
        }
    }

    // ========== HELPER METHODS ==========
    
    /**
     * Extrai metadados de todas as colunas de uma tabela.
     */
    private Map<String, ColumnInfo> getTableColumns(String tableName) throws SQLException {
        Map<String, ColumnInfo> columns = new HashMap<>();
        
        try (Connection conn = dataSource.getConnection()) {
            DatabaseMetaData metaData = conn.getMetaData();
            try (ResultSet rs = metaData.getColumns(null, null, tableName, null)) {
                while (rs.next()) {
                    ColumnInfo info = new ColumnInfo(
                        rs.getString("COLUMN_NAME"),
                        rs.getString("TYPE_NAME"),
                        rs.getInt("NULLABLE") == DatabaseMetaData.columnNullable
                    );
                    columns.put(info.name, info);
                }
            }
        }
        
        return columns;
    }

    /**
     * Extrai nomes de colunas que possuem índice único.
     */
    private List<String> getUniqueIndexColumns(String tableName) throws SQLException {
        List<String> columns = new ArrayList<>();
        
        try (Connection conn = dataSource.getConnection()) {
            DatabaseMetaData metaData = conn.getMetaData();
            try (ResultSet rs = metaData.getIndexInfo(null, null, tableName, true, false)) {
                while (rs.next()) {
                    String columnName = rs.getString("COLUMN_NAME");
                    if (columnName != null) {
                        columns.add(columnName);
                    }
                }
            }
        }
        
        return columns;
    }

    /**
     * Extrai todas as foreign keys que referenciam outras tabelas.
     */
    private List<ForeignKeyInfo> getForeignKeys(String tableName) throws SQLException {
        List<ForeignKeyInfo> fks = new ArrayList<>();
        
        try (Connection conn = dataSource.getConnection()) {
            DatabaseMetaData metaData = conn.getMetaData();
            try (ResultSet rs = metaData.getImportedKeys(null, null, tableName)) {
                while (rs.next()) {
                    fks.add(new ForeignKeyInfo(
                        rs.getString("FKCOLUMN_NAME"),
                        rs.getString("PKTABLE_NAME"),
                        rs.getString("PKCOLUMN_NAME")
                    ));
                }
            }
        }
        
        return fks;
    }

    /**
     * Valida existência e tipo de uma coluna.
     */
    private void assertColumnExists(
            Map<String, ColumnInfo> columns,
            String columnName,
            String expectedType
    ) {
        assertThat(columns)
            .as("Column '%s' does not exist! Migration missing or entity removed.", columnName)
            .containsKey(columnName);
        
        ColumnInfo col = columns.get(columnName);
        
        assertThat(col.type.toLowerCase())
            .as("""
                BREAKING CHANGE: Column type mismatch!
                
                Column: %s
                Expected: %s
                Actual:   %s
                
                Data migration required! Existing data may be incompatible.
                """,
                columnName, expectedType, col.type)
            .startsWith(expectedType.toLowerCase());
    }

    // ========== DTOs ==========
    
    record ColumnInfo(String name, String type, boolean nullable) {}
    
    record ForeignKeyInfo(String columnName, String referencedTable, String referencedColumn) {}
}
```

</example_template>
</generation_instructions>

## EXEMPLOS DE USO

<examples>
<example name="User Entity - Cenário Completo">

**INPUT (Código fornecido pelo usuário):**

```java
package com.example.domain;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue
    private UUID id;
    
    @Column(name = "email", unique = true, nullable = false, length = 255)
    private String email;
    
    @Column(name = "first_name", nullable = false)
    private String firstName;
    
    @Column(name = "last_name")
    private String lastName;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false)
    private UserRole role;
    
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
    
    // getters/setters omitidos
}

enum UserRole {
    ADMIN, USER, GUEST
}
```

**OUTPUT ESPERADO:**

Claude deve gerar os 3 testes completos:

1. **EntityStructureTest**: Valida que User tem @Id, role tem @Enumerated, etc
2. **JpaAnnotationContractTest**: Define contratos:

   ```java
   columnMappings():
     User.id → "id"
     User.email → "email"
     User.firstName → "first_name"
     ...
   
   nullabilityConstraints():
     User.email → false (NOT NULL)
     User.lastName → true (NULLABLE)
     ...
   
   uniqueConstraints():
     User.email → true (UNIQUE)
   ```

3. **DatabaseSchemaTest**: Valida schema real:
   - Tabela `users` existe
   - Colunas `email`, `first_name`, etc existem com tipos corretos
   - Índice único em `email` existe
   - Constraints NOT NULL estão corretas
</example>

<example name="Breaking Change - Renomeação de Coluna">

**CENÁRIO**: Developer acidentalmente renomeia coluna sem criar migration.

```java
// ANTES (produção)
@Column(name = "email")
private String email;

// DEPOIS (novo código)
@Column(name = "user_email") // ❌ BREAKING CHANGE
private String email;
```

**RESULTADO DOS TESTES**:

✅ **EntityStructureTest**: PASSA (estrutura ok)

❌ **JpaAnnotationContractTest**: FALHA

```
BREAKING CHANGE DETECTED!

Column mapping changed:
  Entity: User
  Field:  email
  Expected: email
  Actual:   user_email

This requires an ALTER TABLE migration:
  ALTER TABLE users RENAME COLUMN email TO user_email;

Without this migration, existing queries will FAIL at runtime!
```

❌ **DatabaseSchemaTest**: FALHA (se rodar contra DB de produção)

```
Column 'user_email' does not exist! Expected 'email'.
```

**AÇÃO CORRETA**: Developer cria migration antes de fazer merge.
</example>

<example name="Breaking Change - Remoção de Unique Constraint">

**CENÁRIO**: Developer remove unique constraint sem perceber impacto.

```java
// ANTES
@Column(name = "email", unique = true)
private String email;

// DEPOIS
@Column(name = "email") // ❌ unique=true removido
private String email;
```

**RESULTADO DOS TESTES**:

✅ **EntityStructureTest**: PASSA

❌ **JpaAnnotationContractTest**: FALHA

```
BREAKING CHANGE: Unique constraint on 'User.email' was REMOVED!
System will now allow duplicate email registrations.
Business rule violated: one email per user.
```

❌ **DatabaseSchemaTest**: FALHA

```
BREAKING CHANGE: Unique index on 'email' was removed!

Impact:
- System will now allow duplicate email registrations
- Business rule violated: one email per user
- Existing code may crash on constraint violations

Required fix:
  CREATE UNIQUE INDEX users_email_unique ON users(email);
```

</example>
</examples>

## CHECKLIST DE QUALIDADE

<quality_checklist>
Antes de entregar o código, verifique:

### Imports e Dependências

- [ ] `import static org.assertj.core.api.Assertions.*;` presente
- [ ] `javax.persistence.*` para anotações JPA
- [ ] `org.junit.jupiter.api.*` para JUnit 5
- [ ] `com.tngtech.archunit.*` para ArchUnit
- [ ] `org.testcontainers.*` para Testcontainers

### Estrutura dos Testes

- [ ] `@Nested` usado para agrupar testes relacionados
- [ ] `@DisplayName` em todas as classes e métodos
- [ ] `@ParameterizedTest` para evitar duplicação
- [ ] Comentários `// DETECTA:` explicando o propósito

### AssertJ Assertions

- [ ] `assertThat(...).isEqualTo(...)` ao invés de `assertEquals`
- [ ] `assertThat(...).isNotNull()` ao invés de `assertNotNull`
- [ ] `.as("mensagem")` para contexto em falhas
- [ ] `assertAll()` para múltiplas assertions relacionadas

### UUID Handling

- [ ] `UUID.fromString("550e8400-e29b-41d4-a716-446655440000")` (UUID válido)
- [ ] NUNCA `new UUID(...)` ou `UUID.randomUUID()` em testes

### Mensagens de Erro

- [ ] Explicam O QUÊ quebrou
- [ ] Explicam POR QUÊ isso é um problema
- [ ] Sugerem COMO corrigir
- [ ] Usam text blocks """ para mensagens longas

### Configuração

- [ ] `junit-platform.properties` criado com paralelização
- [ ] Testcontainers configurado corretamente
- [ ] `@MicronautTest(transactional = false)` para testes de schema

### Compilação

- [ ] Código compila com `mvn clean compile`
- [ ] Testes executam com `mvn test`
- [ ] Sem warnings de deprecation
</quality_checklist>

## DEPENDÊNCIAS MAVEN

<dependencies>
Adicionar ao `pom.xml`:

```xml
<dependencies>
    <!-- AssertJ Core (OBRIGATÓRIO) -->
    <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.25.1</version>
        <scope>test</scope>
    </dependency>

    <!-- ArchUnit -->
    <dependency>
        <groupId>com.tngtech.archunit</groupId>
        <artifactId>archunit-junit5</artifactId>
        <version>1.2.1</version>
        <scope>test</scope>
    </dependency>

    <!-- Testcontainers -->
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>postgresql</artifactId>
        <version>1.19.3</version>
        <scope>test</scope>
    </dependency>
    
    <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>1.19.3</version>
        <scope>test</scope>
    </dependency>

    <!-- JUnit 5 Parametrized Tests -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter-params</artifactId>
        <scope>test</scope>
    </dependency>
    
    <!-- Micronaut Data JPA -->
    <dependency>
        <groupId>io.micronaut.data</groupId>
        <artifactId>micronaut-data-hibernate-jpa</artifactId>
    </dependency>
</dependencies>
```

</dependencies>

## COMO USAR ESTE PROMPT

<usage_guide>

### Passo 1: Preparar o Input

Cole suas classes de entidades JPA no formato:

```xml
<entities>
  <entity>
    <source>User.java</source>
    <code>
      [código da classe User]
    </code>
  </entity>
  
  <entity>
    <source>Product.java</source>
    <code>
      [código da classe Product]
    </code>
  </entity>
</entities>
```

### Passo 2: Solicitar Geração

```
Gere os 3 testes completos (EntityStructureTest, JpaAnnotationContractTest, DatabaseSchemaTest) 
para as entidades fornecidas. Use AssertJ para todas as assertions.
```

### Passo 3: Validar Output

Claude deve entregar:

1. **EntityStructureTest.java** - Completo e executável
2. **JpaAnnotationContractTest.java** - Com contratos mapeados
3. **DatabaseSchemaTest.java** - Com Testcontainers configurado
4. **junit-platform.properties** - Configuração de paralelização

### Passo 4: Integrar no Projeto

```bash
# Copiar testes gerados
cp EntityStructureTest.java src/test/java/com/example/architecture/
cp JpaAnnotationContractTest.java src/test/java/com/example/contract/
cp DatabaseSchemaTest.java src/test/java/com/example/integration/
cp junit-platform.properties src/test/resources/

# Executar
mvn test
```

</usage_guide>

## IMPORTANTE: REVISÃO HUMANA NECESSÁRIA

<human_review_required>
Após gerar os testes, você (humano) deve:

1. **Validar contratos**: Os `columnMappings()`, `nullabilityConstraints()` estão corretos?
2. **Ajustar package names**: `com.example.domain` → seu package real
3. **Verificar nomes de tabelas**: `users` → nome real da tabela no banco
4. **Adicionar regras específicas**: Seu projeto tem convenções adicionais?
5. **Testar localmente**: `mvn test` deve passar 100%

⚠️ **LEMBRE-SE**: Estes testes são a fonte da verdade. Se eles falharem, o código está errado, não os testes.
</human_review_required>
