# References

| ref_id | title | path | type | edit_allowed | source | notes |
| --- | --- | --- | --- | --- | --- | --- |
| REF-0001 | ARCH-01 - High-level architecture | .aib_memory/docs/04 Technology/Architecture/ARCH-01.md | product-doc | Y | default | Bundled default |
| REF-0002 | ARCH-02 - Topology/network description | .aib_memory/docs/04 Technology/Architecture/ARCH-02.md | product-doc | Y | default | Bundled default |
| REF-0003 | ARCH-03 - Capacity model | .aib_memory/docs/04 Technology/Architecture/ARCH-03.md | product-doc | Y | default | Bundled default |
| REF-0004 | ARCH-04 - ADRs repository | .aib_memory/docs/04 Technology/Architecture/ARCH-04.md | product-doc | Y | default | Bundled default |
| REF-0005 | ARCH-06 - Runtime interaction sequences | .aib_memory/docs/04 Technology/Architecture/ARCH-06.md | product-doc | Y | default | Bundled default |
| REF-0006 | ARCH-07 - Resource catalog | .aib_memory/docs/04 Technology/Inventory/ARCH-07.md | product-doc | Y | default | Bundled default |
| REF-0007 | CMP-01 - Notebook/script catalog | .aib_memory/docs/04 Technology/Compute/CMP-01.md | product-doc | Y | default | Bundled default |
| REF-0008 | CMP-02 - Algorithm specification register | .aib_memory/docs/04 Technology/Compute/CMP-02.md | product-doc | Y | default | Bundled default |
| REF-0009 | DATA-01 - Source data catalog and data ingestion strategy | .aib_memory/docs/04 Technology/Data Sources/DATA-01.md | product-doc | Y | default | Bundled default |
| REF-0010 | DATA-02 - Data models (logical & physical) | .aib_memory/docs/04 Technology/Data Models/DATA-02.md | product-doc | Y | default | Bundled default |
| REF-0011 | DATA-03 - Data lineage | .aib_memory/docs/04 Technology/Data Workspace/DATA-03.md | product-doc | Y | default | Bundled default |
| REF-0012 | DATA-04 - Data storage strategy & patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-04.md | product-doc | Y | default | Bundled default |
| REF-0013 | DATA-05 - Data consumption & access patterns | .aib_memory/docs/04 Technology/Data Workspace/DATA-05.md | product-doc | Y | default | Bundled default |
| REF-0014 | DATA-06 - Metrics catalog | .aib_memory/docs/04 Technology/Analytics/DATA-06.md | product-doc | Y | default | Bundled default |
| REF-0015 | DATA-07 - Data quality rules, monitoring & reporting | .aib_memory/docs/04 Technology/Data Workspace/DATA-07.md | product-doc | Y | default | Bundled default |
| REF-0016 | DATA-08 - Data archiving & deletion policy | .aib_memory/docs/04 Technology/Data Workspace/DATA-08.md | product-doc | Y | default | Bundled default |
| REF-0017 | DATA-09 - Dashboard inventory | .aib_memory/docs/04 Technology/Analytics/DATA-09.md | product-doc | Y | default | Bundled default |
| REF-0018 | KNW-01 - Domain glossary | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-01.md | product-doc | Y | default | Bundled default |
| REF-0019 | KNW-02 - Business process catalog | .aib_memory/docs/02 Domain/Terms and Concepts/KNW-02.md | product-doc | Y | default | Bundled default |
| REF-0020 | KNW-03 - Use cases & personas | .aib_memory/docs/02 Domain/Use Cases and Personas/KNW-03.md | product-doc | Y | default | Bundled default |
| REF-0021 | OBS-01 - Logging | .aib_memory/docs/04 Technology/Observability/OBS-01.md | product-doc | Y | default | Bundled default |
| REF-0022 | RQT-01 - Product charter | .aib_memory/docs/01 Product Management/Product Charter/RQT-01.md | product-doc | Y | default | Bundled default |
| REF-0023 | RQT-02 - Requirements document | .aib_memory/docs/03 Requirements/RQT-02.md | product-doc | Y | default | Bundled default |
| REF-0024 | SEC-01 - Access management | .aib_memory/docs/04 Technology/Access and Security/SEC-01.md | product-doc | Y | default | Bundled default |
| REF-0025 | SEC-02 - Infrastructure data protection | .aib_memory/docs/04 Technology/Access and Security/SEC-02.md | product-doc | Y | default | Bundled default |
| REF-0026 | SEC-03 - Secrets management & rotation policy | .aib_memory/docs/04 Technology/Access and Security/SEC-03.md | product-doc | Y | default | Bundled default |
| REF-0027 | SEC-04 - Infrastructure network security | .aib_memory/docs/04 Technology/Access and Security/SEC-04.md | product-doc | Y | default | Bundled default |
| REF-0028 | AIB Concepts | .aib_brain\Concepts.md | domain | N | user | This document describes the concepts for AI Builder |
| REF-0029 | AIB Context | .aib_memory/context.md | other | N | default | Unified workspace context synthesized by aib-context.md |
Validation rules:
- `ref_id` unique, format `REF-0001`.
- `path` unique and workspace-relative.
- `type` in `product-doc|source-code|domain|other`.
- `edit_allowed` in `Y|N`.
- `source` in `default|user`.
