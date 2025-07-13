# SafeRoute — HS ↔ Sanctions Dataset  (v0.1 • 2025-07-15)

## 1. Overview
Open-source набор для обучения модели, которая предсказывает санкционный риск
по HS-коду, стране происхождения и описанию товара.
Содержит 5 642 уникальных кодов HS-92 и ≈ 82 000 строк торговой статистики.

## 2. Schema

| Field           | Type      | Description                                   | Example                   |
|-----------------|-----------|-----------------------------------------------|---------------------------|
| `hs_code`       | string(6) | 6-digit Harmonized System 1992                | `860900`                  |
| `description`   | string    | EN text from WCO                              | *Electric locomotives*    |
| `reporter_iso`  | string(3) | ISO-3166 of exporting country (Comtrade)      | `CN`                      |
| `consignee_name`| string    | Importer name (when available)                | *OOO Logistika*           |
| `label`         | int {0,1} | 1 = likely under sanctions (heuristic v0)     | `1`                       |
| `source`        | enum      | `keyword` or `name_match`                     | `keyword`                 |
| `last_update`   | date      | Date of last sanctions-list revision          | `2025-07-15`              |

*Full table generated automatically in `docs/_schema.html`.*

## 3. Source & Collection
| Component | Origin | Script | Refresh |
|-----------|--------|--------|---------|
| OFAC SDN  | <https://ofac.treasury.gov/downloads/sdn.csv> | `01_fetch_ofac.py` | daily |
| EU FSF    | … | `02_fetch_eu.py` | daily |
| UN SC     | … | `03_fetch_un.py` | daily |
| HS-92 CSV | GitHub datasets/harmonized-system | `04_fetch_hs.py` | static |
| Comtrade  | WorldBank Comtrade API | `05_fetch_comtrade.py` | yearly |

## 4. Pre-processing
* Merge names/aliases → lower-case, strip.  
* Remove duplicates by `sig = sha1(lower(name)+program)`.  
* `label = keyword_flag ∨ name_match` (see `20_build_dataset.py`).  

## 5. Splits
`train.parquet` 90 % / `holdout.parquet` 10 % stratified by `label`.  
Class balance: pos = 7.4 %.

## 6. Licensing
* Sanction-lists: **Public Domain** (US Gov, EU Council, UN Sec. Council).  
* HS codes: © WCO, redistributed under **CC-BY-4.0**.  
* Comtrade: © World Bank, **CC-BY-4.0**.

## 7. Ethics & Legal Considerations
Dataset не содержит персональных данных (имена юр. лиц).  
False-positive могут привести к необоснованному блокированию товара ⇒  
в продакшене предусмотрена ручная верификация результатов с порогом 0.8.

## 8. Maintenance
Nightly GitHub-Actions workflow [`nightly_pipeline.yml`](../.github/workflows/nightly.yml)  
проверяет обновления SDN/EU/UN, добавляет патчи и запускает retrain при δ ≥ 1 %.  
Issues: <https://github.com/TemaMind/saveroute-core/issues> label `dataset`.
