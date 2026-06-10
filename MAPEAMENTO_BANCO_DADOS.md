# Mapeamento do Banco de Dados - Projeto Fuzzy

## Índice
1. [Visão Geral](#visão-geral)
2. [Tabelas](#tabelas)
3. [Relacionamentos](#relacionamentos)
4. [Diagrama de Relacionamentos](#diagrama-de-relacionamentos)

---

## Visão Geral

O banco de dados utiliza **PostgreSQL 16** com um total de **9 tabelas**. Todas as tabelas utilizam IDs do tipo `BigInteger` como chave primária. A maioria dos relacionamentos implementa `ondelete='CASCADE'` para manter integridade referencial ao deletar projetos.

---

## Tabelas

### 1. **projects** (Projeto Raiz)
Tabela principal que contém os projetos do sistema.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| name | String | NOT NULL | Nome do projeto |
| created_at | DateTime(timezone=True) | NOT NULL, DEFAULT: now() | Data de criação com timezone |

**Chave Primária:** `id`

**Relacionamentos de Saída:**
- N relacionamentos 1:N com outras tabelas (alternativas, critérios, classes, fuzzy_terms, criteria_weights, criterion_class_thresholds, evaluations)

---

### 2. **alternatives** (Alternativas)
Contém as alternativas de decisão para cada projeto.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| code | String | NOT NULL | Código da alternativa (ex: A1, A2) |
| name | String | NOT NULL | Nome da alternativa |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |

**Constraints Únicos:**
- `uq_alternatives_project_code`: Combinação única de `(project_id, code)` - não pode haver dois codes iguais no mesmo projeto

**Relacionamentos de Entrada:**
- Referenciada por `evaluations` (1:N)

---

### 3. **classes** (Classificações)
Define as classes de classificação para os critérios.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| code | String | NOT NULL | Código da classe (ex: C1, C2) |
| description | String | NOT NULL | Descrição da classe |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |

**Constraints Únicos:**
- `uq_classes_project_code`: Combinação única de `(project_id, code)`

**Relacionamentos de Entrada:**
- Referenciada por `criterion_class_thresholds` (1:N)

---

### 4. **criteria** (Critérios)
Define os critérios de avaliação para o projeto.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| code | String | NOT NULL | Código do critério (ex: C1, C2) |
| name | String | NOT NULL | Nome do critério |
| kind | Enum | NOT NULL | Tipo de critério: `'beneficio'` ou `'custo'` |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |

**Constraints Únicos:**
- `uq_criteria_project_code`: Combinação única de `(project_id, code)`

**Tipo Enum:**
- `criterion_kind`: 'beneficio' | 'custo'

**Relacionamentos de Entrada:**
- Referenciada por `criteria_weights` (1:N)
- Referenciada por `criterion_class_thresholds` (1:N)
- Referenciada por `criterion_descriptions` (1:N)
- Referenciada por `evaluations` (1:N)

---

### 5. **fuzzy_terms** (Termos Fuzzy)
Define os termos linguísticos fuzzy (números fuzzy triangulares) utilizados no sistema.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| code | String | NOT NULL | Código do termo (ex: Baixo, Médio, Alto) |
| description | String | NOT NULL | Descrição do termo |
| l | Numeric(10,4) | NOT NULL | Limite inferior do número fuzzy triangular |
| m | Numeric(10,4) | NOT NULL | Valor médio do número fuzzy triangular |
| u | Numeric(10,4) | NOT NULL | Limite superior do número fuzzy triangular |
| term_type | Enum | NOT NULL | Tipo do termo: `'alternative'` ou `'weight'` |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |

**Constraints Únicos:**
- `uq_fuzzy_terms_project_code_type`: Combinação única de `(project_id, code, term_type)` - mesmo código pode existir com tipos diferentes

**Constraints de Verificação:**
- `ck_fuzzy_terms_lmu_order`: `l <= m AND m <= u` - garante que l ≤ m ≤ u

**Tipo Enum:**
- `term_type`: 'alternative' | 'weight'

**Relacionamentos de Entrada:**
- Referenciada por `criteria_weights` (1:N)
- Referenciada por `criterion_class_thresholds` (1:N)
- Referenciada por `criterion_descriptions` (1:N)

---

### 6. **criteria_weights** (Pesos dos Critérios)
Armazena os pesos fuzzy associados a cada critério.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| criterion_id | BigInteger | FK, NOT NULL | Referência ao critério |
| weight_term_id | BigInteger | FK, NULLABLE | Referência ao termo fuzzy de peso |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |
| criterion_id | criteria.id | CASCADE | - |
| weight_term_id | fuzzy_terms.id | SET NULL | - |

**Constraints Únicos:**
- `uq_criteria_weights_project_crit`: Combinação única de `(project_id, criterion_id)` - cada critério tem apenas um peso por projeto

---

### 7. **criterion_class_thresholds** (Limites de Classe por Critério)
Define os limites/thresholds dos termos fuzzy para cada combinação critério-classe.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| criterion_id | BigInteger | FK, NOT NULL | Referência ao critério |
| class_id | BigInteger | FK, NOT NULL | Referência à classe |
| min_alternative_term_id | BigInteger | FK, NULLABLE | Referência ao termo fuzzy mínimo alternativa |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| criterion_id | criteria.id | CASCADE | - |
| class_id | classes.id | CASCADE | - |
| min_alternative_term_id | fuzzy_terms.id | SET NULL | - |

**Constraints Únicos:**
- `uq_criterion_class_threshold`: Combinação única de `(criterion_id, class_id)` - cada classe tem apenas um threshold por critério

---

### 8. **criterion_descriptions** (Descrições de Critério)
Define as descrições linguísticas para os critérios com seus termos fuzzy associados.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| criterion_id | BigInteger | FK, NOT NULL | Referência ao critério |
| description | String | NOT NULL | Texto da descrição |
| alternative_term_id | BigInteger | FK, NULLABLE | Referência ao termo fuzzy alternativa |
| weight_term_id | BigInteger | FK, NULLABLE | Referência ao termo fuzzy peso |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| criterion_id | criteria.id | CASCADE | - |
| alternative_term_id | fuzzy_terms.id | SET NULL | - |
| weight_term_id | fuzzy_terms.id | SET NULL | - |

---

### 9. **evaluations** (Avaliações)
Contém as avaliações das alternativas segundo cada critério.

| Atributo | Tipo | Constraint | Descrição |
|----------|------|-----------|-----------|
| id | BigInteger | PK | Identificador único |
| project_id | BigInteger | FK, NOT NULL | Referência ao projeto |
| alternative_id | BigInteger | FK, NOT NULL | Referência à alternativa |
| criterion_id | BigInteger | FK, NOT NULL | Referência ao critério |
| criterion_description_id | BigInteger | FK, NULLABLE | Referência à descrição do critério |

**Chave Primária:** `id`

**Chaves Estrangeiras:**
| Campo | Referencia | ondelete | onupdate |
|-------|-----------|----------|----------|
| project_id | projects.id | CASCADE | - |
| alternative_id | alternatives.id | CASCADE | - |
| criterion_id | criteria.id | CASCADE | - |
| criterion_description_id | criterion_descriptions.id | SET NULL | - |

**Constraints Únicos:**
- `uq_evaluations_project_alt_crit`: Combinação única de `(project_id, alternative_id, criterion_id)` - cada alternativa pode ter apenas uma avaliação por critério

---

## Relacionamentos

### Hierarquia de Cascade Delete

```
projects (raiz)
    ├── alternatives → evaluations
    ├── classes → criterion_class_thresholds
    ├── criteria
    │   ├── criteria_weights
    │   ├── criterion_class_thresholds
    │   ├── criterion_descriptions
    │   └── evaluations
    └── fuzzy_terms
        ├── criteria_weights (SET NULL)
        ├── criterion_class_thresholds (SET NULL)
        └── criterion_descriptions (SET NULL)
```

### Regras de Integridade Referencial

1. **CASCADE DELETE (ondelete='CASCADE'):**
   - Quando um projeto é deletado, TODAS as entidades relacionadas são deletadas em cascata
   - Quando uma alternativa é deletada, suas avaliações são deletadas
   - Quando um critério é deletado, seus pesos, thresholds, descrições e avaliações são deletados
   - Quando uma classe é deletada, seus thresholds são deletados

2. **SET NULL (ondelete='SET NULL'):**
   - Aplicado apenas a relacionamentos opcionais (NULLABLE)
   - Quando um termo fuzzy é deletado, os relacionamentos que o referenciam são apenas NULADOs
   - Afeta: `criteria_weights.weight_term_id`, `criterion_class_thresholds.min_alternative_term_id`, `criterion_descriptions.alternative_term_id`, `criterion_descriptions.weight_term_id`, `evaluations.criterion_description_id`

---

## Diagrama de Relacionamentos

```
┌──────────────┐
│   projects   │ (raiz)
└──────────────┘
       │
       ├─────────────────────────────────────┬─────────────────────┬─────────────────┐
       │                                     │                     │                 │
       ▼ (1:N CASCADE)                       ▼ (1:N CASCADE)       ▼ (1:N CASCADE)   ▼ (1:N CASCADE)
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐
│ alternatives    │  │   classes    │  │   criteria   │  │   fuzzy_terms  │
└─────────────────┘  └──────────────┘  └──────────────┘  └────────────────┘
       │                     │                  │              /      │      \
       │                     │                  │             /       │       \
       │ (1:N CASCADE)       │                  │            /        │        \
       │                     │ (1:N CASCADE)    │           /         │         \
       │                     │                  │          /          │          \
       ▼                     ▼                  ▼         ▼           ▼           ▼
┌─────────────────┐  ┌──────────────────────────┐  ┌──────────────────┐
│  evaluations    │  │ criterion_class_thresholds│  │ criteria_weights │
└─────────────────┘  └──────────────────────────┘  └──────────────────┘
       │                     │                             │
       │ (1:N CASCADE)       │ (1:N CASCADE)               │ (1:N CASCADE)
       │                     │                             │
       ▼                     ▼                             ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────┐
│ criterion_descriptions│  │ criterion_descriptions│  │ fuzzy_terms  │
└──────────────────────┘  └──────────────────────┘  └──────────────┘
```

---

## Resumo de Constraints

### Tipos de Constraints Utilizados

| Tipo | Quantidade | Exemplos |
|------|-----------|----------|
| Primary Key (PK) | 9 | Um `id` em cada tabela |
| Foreign Key (FK) | 14 | Relacionamentos entre tabelas |
| Unique (UNIQUE) | 7 | Combinações únicas de campos |
| Check (CHECK) | 1 | `ck_fuzzy_terms_lmu_order` |
| Enum | 2 | `criterion_kind`, `term_type` |
| NOT NULL | 30+ | Maioria dos campos obrigatórios |

### Distribuição de Relacionamentos

| Tipo ondelete | Quantidade |
|---------------|-----------|
| CASCADE | 10 |
| SET NULL | 4 |
| **Total** | **14** |

---

## Notas Importantes

1. **Timezone:** Campo `created_at` em `projects` utiliza timezone
2. **Números Fuzzy:** Valores em `l`, `m`, `u` utilizam precisão 10,4 (máximo 999999.9999)
3. **Validação:** Constraint de check garante que números fuzzy triangulares mantêm a ordem: L ≤ M ≤ U
4. **Escalabilidade:** Todos os IDs utilizam `BigInteger` permitindo até 9.223.372.036.854.775.807 registros por tabela
5. **Integridade:** Estrutura garante que deletar um projeto limpa completamente todos os dados associados
6. **Opcionais:** Apenas campos de referência a termos fuzzy e descrições são opcionais (NULLABLE)
