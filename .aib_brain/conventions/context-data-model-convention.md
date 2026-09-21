## Convention: context-data-model-convention.md

### Purpose

Defines the canonical markdown representation of logical, physical, and analytical data models used as context extensions. Provides a standardized structure for documenting schema definitions, entities, attributes, relationships, and supporting objects in a human-readable format. Intended for use as a reference file registered in context.md ## References.

### Applicability

Applies to every data model context extension referenced from .aib_memory/context.md, regardless of domain, technology stack, storage platform, or modelling methodology.

### Normative Language

Keywords MUST, MUST NOT, SHALL, SHOULD, MAY, OPTIONAL per BCP 14 (RFC 2119 + RFC 8174).

### Document Structure

A data model document MUST start with the exact H1 `# Context Data Model`.

It then uses exactly one of two mutually exclusive forms:

- Empty state: the H1 is followed by the single line `No data models are currently documented.` and no H2 sections.
- Model state: the H1 is followed by one or more H2 data-model sections and the empty-state notice is absent.

The empty-state form is canonical for initialized workspaces where an exhaustive scan finds no data model. A data model document in model state consists of one or more H2 sections.

Each H2 section represents exactly one data model.

Example:

## Customer Domain

## Product Master

Each H2 heading MUST contain the short business name of the data model.

A data model is uniquely identified across refreshes by its case-insensitive business name plus its normalized physical Location value. Models MUST be ordered by normalized business name and then normalized Location so unchanged inputs produce stable output.

### Data Model Sections

Each data model MUST contain the following H3 sections:

- Type
- Location
- Description
- Entities

The following H3 sections are OPTIONAL:

- Relations
- Other Objects

No additional H3 sections are permitted.

### Type Section

The Type section defines the modelling abstraction level.

Valid values:

- logical
- physical
- analytical

Exactly one value MUST be specified.

### Location Section

The Location section identifies where the model is physically realized or maintained.

Examples:

- Snowflake database SALES_DB
- SQL Server CustomerDW
- Power BI Semantic Model
- dbt model layer
- N/A - conceptual model only

The value MUST be a single textual description.

### Description Section

The Description section provides a brief summary of the model purpose, scope, and business meaning.

The description SHOULD be concise and implementation-independent.

### Entities Section

The Entities section contains one or more entity definitions.

Each entity MUST be represented by an H4 heading.

Example:

#### Customer

#### Product

Each entity contains an attribute list.

### Entity Attributes

Each attribute MUST be represented as a markdown bullet.

Required fields:

- Name
- Type

Optional fields:

- Physical Name
- Constraints

Example:

- Name: Customer ID
  Type: Integer
  Constraints: Key, Not Null

### Attribute Constraints

Valid constraint types are:

- Key
- Not Null
- Unique
- Foreign Key
- Min Length
- Max Length
- Check

Constraint names MUST match these values exactly.

#### Check Constraint

When using Check, the rule definition MUST be explicitly provided.

Example:

Constraints: Check (Quantity >= 0)

#### Foreign Key Constraint

When using Foreign Key, the referenced entity and attribute SHOULD be specified.

Example:

Constraints: Foreign Key(Customer.Customer ID)

### Relations Section

The Relations section defines relationships between entities.

Each relationship MUST be represented by an H4 heading containing the relationship name.

Example:

#### Customer Orders

Each relationship definition MUST contain:

- Left Side Entity
- Right Side Entity
- Relationship Cardinality

Optional fields:

- Left Side Attribute
- Right Side Attribute

### Relationship Cardinality

Valid cardinality values:

- 1:1
- M:1
- M:M

The convention assumes the Left Side represents the many side when cardinality is M:1.

Example:

- Left Side Entity: Order
- Left Side Attribute: Customer ID
- Right Side Entity: Customer
- Right Side Attribute: Customer ID
- Relationship Cardinality: M:1

### Other Objects Section

The Other Objects section documents model artifacts that are not entities or relationships.

Examples:

- Views
- Measures
- Calculated Columns
- Dataflows
- Stored Procedures
- Functions

Each object MUST be represented by an H4 heading.

Example:

#### Customer Lifetime Value

Each object definition MUST contain:

- Name
- Type
- Description

### Formatting Rules

- UTF-8 Markdown only.
- NO HTML tags.
- NO images.
- NO markdown tables.
- Exactly one H1 heading is required and MUST be `# Context Data Model`.
- H2 headings represent data models.
- H3 headings are limited to the defined section names.
- H4 headings are limited to entity names, relationship names, and object names.
- Heading depth MUST NOT exceed H4.
- Attribute definitions MUST use markdown bullet format.
- Entity names MUST be unique within a data model.
- Relationship names MUST be unique within a data model.
- Object names MUST be unique within a data model.

### Quality Gates

A data model document passes validation iff all eight checks below pass:

1. File exists, is UTF-8 readable, and starts with `# Context Data Model`.
2. Heading hierarchy follows the convention: model H2 headings, permitted H3 sections, and entity, relation, or object H4 headings only.
3. Empty state is exactly `# Context Data Model`, one blank line, and `No data models are currently documented.` with no model sections; model state does not contain the notice.
4. Every model contains exactly one Type, Location, Description, and Entities section; Type contains exactly one valid value and Location and Description are non-empty.
5. Model identity pairs are unique case-insensitively and model ordering is deterministic by business name then Location.
6. Entities contains at least one uniquely named entity; every entity contains at least one attribute and every attribute defines Name and Type.
7. Every optional relation and other object has a unique heading and all required fields; relationship cardinality and constraints use the defined values.
8. Document is UTF-8 Markdown with no HTML, images, Markdown tables, headings deeper than H4, duplicate names, or unsupported sections.
