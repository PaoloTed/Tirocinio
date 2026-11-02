# Ciclo di Vita dei Test E2E — `ghiscoding/angular-slickgrid`

> Tracciamento completo del ciclo di vita di tutti i file di test E2E Cypress attraverso le due epoche del progetto:
> 1. **Era JavaScript (`2019 – Gennaio 2023`)**: [ciclo_vita_test_javascript.csv](./ciclo_vita_test_javascript.csv) (33 file)
> 2. **Era TypeScript (`v5.4.0 – v8.14.1`)**: [ciclo_vita_test_typescript.csv](./ciclo_vita_test_typescript.csv) (46 file)

---

## 1. Le 4 Tappe Storiche di Ridenominazione dei File

1. **Marzo 2019 (`v2.4.4`)**: Nascita di Cypress con `cypress/integration/basic_grid.spec.js` e `example1.spec.js` .. `example9.spec.js`.
2. **Dicembre 2019 (`v2.14.5`)**: Spostamento nella sottocartella `test/` e numerazione a due cifre: `test/cypress/integration/example01.spec.js` .. `example33.spec.js`.
3. **Giugno 2022 (`v4.2.0` — Upgrade a Cypress 10)**: Ridenominazione da `.spec.js` a `.cy.js` e spostamento in `e2e/`: `test/cypress/e2e/example01.cy.js` .. `example33.cy.js`.
4. **27 Gennaio 2023 (`v5.4.0` — Punto del Cambiamento)**: Migrazione in TypeScript: `test/cypress/e2e/example01.cy.ts` .. `example33.cy.ts`.

---

## 2. Ciclo di Vita dei 33 Test nell'Era JavaScript (2019 – `v5.4.0`)

| # | File di Test (JS $\rightarrow$ TS) | Anno Nascita | Data Nascita | Versione Nascita | N. Versioni Anno | 1ª Versione di Modifica | $\Delta$ Versioni alla 1ª Modifica | Versioni di Modifica Successive (fino a `v5.4.0`) |
|---|---|---|---|---|---|---|---|---|
| 1 | `basic_grid.spec.js` $\rightarrow$ **`example01.cy.ts`** | **2019** | 2019-03-19 | `v2.4.4` | 65 | `v2.4.7` | **2 versioni** | `v2.9.7` (+19 v), `v2.10.0` (+3 v), `v2.14.3` (+19 v), `v2.14.5` (+2 v), `v2.16.0` (+6 v), `v2.17.1` (+7 v), `v2.17.11` (+10 v), `v2.18.0` (+1 v), `v2.23.0` (+23 v), `v2.29.0` (+14 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.1.0` (+1 v), `v4.2.0` (+5 v), `v5.4.0` (+22 v) |
| 2 | `example02.spec.js` $\rightarrow$ **`example02.cy.ts`** | **2020** | 2020-01-14 | `v2.16.0` | 53 | `v2.30.0` | **57 versioni** | `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 3 | `example03.spec.js` $\rightarrow$ **`example03.cy.ts`** | **2020** | 2020-07-18 | `v2.19.1` | 53 | `v2.26.0` | **22 versioni** | `v2.29.0` (+6 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.1.0` (+14 v), `v5.4.0` (+8 v) |
| 4 | `example4.spec.js` $\rightarrow$ **`example04.cy.ts`** | **2019** | 2019-11-18 | `v2.14.0` | 65 | `v2.16.0` | **11 versioni** | `v2.16.2` (+2 v), `v2.27.0` (+49 v), `v2.30.0` (+6 v), `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 5 | `example5.spec.js` $\rightarrow$ **`example05.cy.ts`** | **2019** | 2019-07-31 | `v2.10.0` | 65 | `v2.11.0` | **6 versioni** | `v2.12.3` (+7 v), `v2.13.1` (+2 v), `v2.14.0` (+1 v), `v2.14.3` (+3 v), `v2.14.5` (+2 v), `v2.16.0` (+6 v), `v2.16.4` (+4 v), `v2.16.5` (+1 v), `v2.19.0` (+21 v), `v2.23.1` (+16 v), `v2.25.1` (+6 v), `v2.30.0` (+9 v), `v3.0.0` (+5 v), `v3.1.0` (+6 v), `v3.2.0` (+1 v), `v4.0.0` (+4 v), `v4.1.0` (+1 v), `v4.1.1` (+1 v), `v4.2.0` (+4 v), `v5.1.0` (+14 v), `v5.4.0` (+8 v) |
| 6 | `example6.spec.js` $\rightarrow$ **`example06.cy.ts`** | **2019** | 2019-03-22 | `v2.4.4` | 65 | `v2.9.7` | **21 versioni** | `v2.10.0` (+3 v), `v2.11.0` (+6 v), `v2.12.3` (+7 v), `v2.14.0` (+3 v), `v2.14.3` (+3 v), `v2.14.5` (+2 v), `v2.16.0` (+6 v), `v2.16.2` (+2 v), `v2.16.4` (+2 v), `v2.21.0` (+27 v), `v2.27.0` (+20 v), `v2.29.0` (+4 v), `v2.29.1` (+1 v), `v2.30.0` (+1 v), `v4.0.0` (+16 v), `v4.1.1` (+2 v), `v4.2.0` (+4 v), `v5.4.0` (+22 v) |
| 7 | `example07.spec.js` $\rightarrow$ **`example07.cy.ts`** | **2019** | 2019-12-18 | `v2.14.5` | 65 | `v2.16.0` | **6 versioni** | `v2.23.0` (+41 v), `v2.30.0` (+16 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 8 | `example08.spec.js` $\rightarrow$ **`example08.cy.ts`** | **2019** | 2019-12-18 | `v2.14.5` | 65 | `v2.16.0` | **6 versioni** | `v2.17.1` (+7 v), `v2.17.5` (+4 v), `v2.23.0` (+30 v), `v2.25.1` (+7 v), `v2.30.0` (+9 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 9 | `example9.spec.js` $\rightarrow$ **`example09.cy.ts`** | **2019** | 2019-07-31 | `v2.10.0` | 65 | `v2.10.2` | **2 versioni** | `v2.12.3` (+11 v), `v2.14.3` (+6 v), `v2.14.5` (+2 v), `v2.15.3` (+4 v), `v2.16.0` (+2 v), `v2.29.0` (+55 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 10 | `example10.spec.js` $\rightarrow$ **`example10.cy.ts`** | **2019** | 2019-07-29 | `v2.9.9` | 65 | `v2.10.0` | **1 versioni** | `v2.14.3` (+19 v), `v2.16.0` (+8 v), `v2.16.1` (+1 v), `v2.16.5` (+4 v), `v2.17.0` (+1 v), `v2.17.3` (+3 v), `v2.23.1` (+33 v), `v2.25.1` (+6 v), `v2.30.0` (+9 v), `v3.0.0` (+5 v), `v3.2.0` (+7 v), `v4.0.0` (+4 v), `v4.2.0` (+6 v), `v5.1.0` (+14 v), `v5.4.0` (+8 v) |
| 11 | `example11.spec.js` $\rightarrow$ **`example11.cy.ts`** | **2020** | 2020-10-13 | `v2.22.2` | 53 | `v2.30.0` | **20 versioni** | `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 12 | `example12.spec.js` $\rightarrow$ **`example12.cy.ts`** | **2019** | 2019-11-29 | `v2.14.3` | 65 | `v2.14.5` | **2 versioni** | `v2.16.0` (+6 v), `v2.17.1` (+7 v), `v2.17.4` (+3 v), `v2.18.0` (+8 v), `v2.19.1` (+9 v), `v2.23.2` (+16 v), `v2.26.1` (+7 v), `v2.28.2` (+4 v), `v2.29.0` (+1 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.1.0` (+14 v), `v5.1.3` (+3 v), `v5.4.0` (+5 v) |
| 13 | `example13.spec.js` $\rightarrow$ **`example13.cy.ts`** | **2021** | 2021-02-15 | `v2.26.0` | 27 | `v2.26.1` | **1 versioni** | `v2.30.0` (+7 v), `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 14 | `example14.spec.js` $\rightarrow$ **`example14.cy.ts`** | **2020** | 2020-09-18 | `v2.22.0` | 53 | `v2.30.0` | **22 versioni** | `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 15 | `example15.spec.js` $\rightarrow$ **`example15.cy.ts`** | **2020** | 2020-06-29 | `v2.19.0` | 53 | `v2.27.0` | **25 versioni** | `v2.30.0` (+6 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 16 | `example16.spec.js` $\rightarrow$ **`example16.cy.ts`** | **2019** | 2019-08-05 | `v2.10.0` | 65 | `v2.14.3` | **19 versioni** | `v2.16.0` (+8 v), `v2.17.0` (+6 v), `v2.27.0` (+45 v), `v2.29.0` (+4 v), `v2.30.0` (+2 v), `v3.2.0` (+12 v), `v4.0.0` (+4 v), `v4.2.0` (+6 v), `v5.0.0-alpha.0` (+10 v), `v5.1.2` (+6 v), `v5.1.3` (+1 v), `v5.4.0` (+5 v) |
| 17 | `example17.spec.js` $\rightarrow$ **`example17.cy.ts`** | **2020** | 2020-04-07 | `v2.18.0` | 53 | `v2.22.0` | **17 versioni** | `v2.22.2` (+2 v), `v2.29.0` (+18 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.0.0-alpha.0` (+10 v), `v5.1.0` (+4 v), `v5.4.0` (+8 v) |
| 18 | `example19.spec.js` $\rightarrow$ **`example19.cy.ts`** | **2020** | 2020-09-18 | `v2.22.0` | 53 | `v2.30.0` | **22 versioni** | `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.0.0-alpha.0` (+10 v), `v5.1.2` (+6 v), `v5.4.0` (+6 v) |
| 19 | `example20.spec.js` $\rightarrow$ **`example20.cy.ts`** | **2020** | 2020-06-29 | `v2.19.0` | 53 | `v2.23.3` | **18 versioni** | `v2.27.0` (+7 v), `v2.29.0` (+4 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 20 | `example21.spec.js` $\rightarrow$ **`example21.cy.ts`** | **2020** | 2020-01-17 | `v2.16.0` | 53 | `v2.25.1` | **48 versioni** | `v2.29.0` (+7 v), `v2.30.0` (+2 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v4.2.2` (+2 v), `v5.4.0` (+20 v) |
| 21 | `example22.spec.js` $\rightarrow$ **`example22.cy.ts`** | **2019** | 2019-10-17 | `v2.12.0` | 65 | `v2.13.0` | **4 versioni** | `v2.16.4` (+17 v), `v2.22.2` (+33 v), `v2.27.0` (+14 v), `v2.30.0` (+6 v), `v3.0.0` (+5 v), `v4.0.0` (+11 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 22 | `example23.spec.js` $\rightarrow$ **`example23.cy.ts`** | **2020** | 2020-10-13 | `v2.22.2` | 53 | `v2.26.0` | **12 versioni** | `v2.29.1` (+7 v), `v2.30.0` (+1 v), `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 23 | `example24.spec.js` $\rightarrow$ **`example24.cy.ts`** | **2021** | 2021-02-15 | `v2.26.0` | 27 | `v2.30.0` | **8 versioni** | `v4.2.0` (+22 v), `v5.4.0` (+22 v) |
| 24 | `example25.spec.js` $\rightarrow$ **`example25.cy.ts`** | **2019** | 2019-08-16 | `v2.10.0` | 65 | `v2.14.0` | **16 versioni** | `v2.14.1` (+1 v), `v2.20.0` (+38 v), `v2.30.0` (+29 v), `v4.2.0` (+22 v), `v5.0.0-alpha.0` (+10 v), `v5.1.0` (+4 v), `v5.1.2` (+2 v), `v5.1.3` (+1 v), `v5.2.0` (+1 v), `v5.4.0` (+4 v) |
| 25 | `example26.spec.js` $\rightarrow$ **`example26.cy.ts`** | **2019** | 2019-12-18 | `v2.14.5` | 65 | `v2.16.2` | **8 versioni** | `v2.30.0` (+55 v), `v4.0.0` (+16 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 26 | `example27.spec.js` $\rightarrow$ **`example27.cy.ts`** | **2021** | 2021-02-15 | `v2.26.0` | 27 | `v2.26.1` | **1 versioni** | `v2.27.0` (+1 v), `v2.28.0` (+1 v), `v2.29.0` (+3 v), `v2.29.1` (+1 v), `v2.30.0` (+1 v), `v3.1.0` (+11 v), `v4.0.0` (+5 v), `v4.1.1` (+2 v), `v4.2.0` (+4 v), `v5.4.0` (+22 v) |
| 27 | `example28.spec.js` $\rightarrow$ **`example28.cy.ts`** | **2020** | 2020-07-15 | `v2.19.1` | 53 | `v2.29.0` | **28 versioni** | `v2.30.0` (+2 v), `v3.1.0` (+11 v), `v3.2.0` (+1 v), `v4.0.0` (+4 v), `v4.2.0` (+6 v), `v4.2.7` (+7 v), `v4.3.0` (+1 v), `v5.1.0` (+6 v), `v5.4.0` (+8 v) |
| 28 | `example29.spec.js` $\rightarrow$ **`example29.cy.ts`** | **2020** | 2020-05-19 | `v2.17.12` | 53 | `v2.29.0` | **36 versioni** | `v2.30.0` (+2 v), `v3.2.0` (+12 v), `v4.0.0` (+4 v), `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 29 | `example30.spec.js` $\rightarrow$ **`example30.cy.ts`** | **2021** | 2021-04-21 | `v2.28.0` | 27 | `v2.29.0` | **3 versioni** | `v2.30.0` (+2 v), `v3.0.0` (+5 v), `v3.1.0` (+6 v), `v4.2.0` (+11 v), `v5.0.0-alpha.0` (+10 v), `v5.1.0` (+4 v), `v5.4.0` (+8 v) |
| 30 | `example31.spec.js` $\rightarrow$ **`example31.cy.ts`** | **2021** | 2021-07-12 | `v3.0.0` | 27 | `v4.0.0` | **11 versioni** | `v4.2.0` (+6 v), `v5.4.0` (+22 v) |
| 31 | `example32.spec.js` $\rightarrow$ **`example32.cy.ts`** | **2021** | 2021-10-28 | `v3.3.0` | 27 | `v4.2.0` | **9 versioni** | `v5.4.0` (+22 v) |
| 32 | `example33.spec.js` $\rightarrow$ **`example33.cy.ts`** | **2022** | 2022-01-04 | `v4.1.0` | 26 | `v4.2.0` | **5 versioni** | `v5.0.0-alpha.0` (+10 v), `v5.4.0` (+12 v) |
| 33 | `home.spec.js` $\rightarrow$ **`home.cy.ts`** | **2019** | 2019-03-19 | `v2.4.4` | 65 | `v2.9.7` | **21 versioni** | `v2.10.0` (+3 v), `v2.14.3` (+19 v), `v2.23.0` (+49 v), `v4.2.0` (+38 v), `v5.4.0` (+22 v) |

---

## 3. Ciclo di Vita dei 46 Test nell'Era TypeScript (`v5.4.0` – `v8.14.1`)

| # | File di Test | Anno Nascita | Versione Nascita | N. Versioni Anno | 1ª Versione di Modifica | $\Delta$ Versioni alla 1ª Modifica | Versioni di Modifica Successive |
|---|---|---|---|---|---|---|---|
| 1 | **`example01.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v8.0.0` (+23 v), `v8.12.0` (+20 v) |
| 2 | **`example02.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v8.11.0` (+42 v), `v8.12.0` (+1 v) |
| 3 | **`example03.cy.ts`** | **2023** | `v5.4.0` | 32 | `v5.6.0` | **4 versioni** | `v6.0.0` (+4 v), `v6.4.0` (+8 v), `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.0.0` (+15 v), `v8.12.0` (+20 v) |
| 4 | **`example04.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v8.0.0` (+23 v), `v8.1.0` (+1 v), `v8.8.1` (+13 v), `v8.9.0` (+1 v), `v8.12.0` (+5 v) |
| 5 | **`example05.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.0.0` | **8 versioni** | `v6.4.0` (+8 v), `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.1.0` (+16 v), `v8.2.0` (+1 v), `v8.12.0` (+18 v) |
| 6 | **`example06.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v8.0.0` (+23 v), `v8.1.0` (+1 v), `v8.2.0` (+1 v), `v8.3.0` (+1 v), `v8.6.0` (+7 v), `v8.12.0` (+10 v) |
| 7 | **`example07.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v8.0.0` (+23 v), `v8.5.1` (+8 v), `v8.12.0` (+12 v) |
| 8 | **`example08.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v8.0.0` (+23 v), `v8.12.0` (+20 v) |
| 9 | **`example09.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v8.12.0` (+43 v) |
| 10 | **`example10.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.0.1` | **9 versioni** | `v6.5.0` (+8 v), `v8.10.2` (+41 v), `v8.12.0` (+2 v) |
| 11 | **`example11.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.1.0` (+13 v), `v8.12.0` (+30 v) |
| 12 | **`example12.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.0.1` | **9 versioni** | `v6.2.0` (+2 v), `v6.4.0` (+5 v), `v6.5.0` (+1 v), `v8.0.0` (+23 v), `v8.12.0` (+20 v) |
| 13 | **`example13.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v8.0.0` (+23 v), `v8.12.0` (+20 v) |
| 14 | **`example14.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.1.0` (+16 v), `v8.4.0` (+5 v), `v8.5.1` (+2 v), `v8.12.0` (+12 v) |
| 15 | **`example15.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 16 | **`example16.cy.ts`** | **2023** | `v5.4.0` | 32 | `v5.6.0` | **4 versioni** | `v6.4.0` (+12 v), `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.2.0` (+17 v), `v8.5.1` (+6 v), `v8.12.0` (+12 v) |
| 17 | **`example17.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v7.6.0` (+12 v), `v8.0.0` (+3 v), `v8.12.0` (+20 v) |
| 18 | **`example18.cy.ts`** | **2025** | `v8.12.0` | 10 | *Nessuna* | *Mai modificato* | - |
| 19 | **`example19.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.1.0` (+16 v), `v8.3.0` (+2 v), `v8.10.2` (+15 v), `v8.12.0` (+2 v) |
| 20 | **`example20.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 21 | **`example21.cy.ts`** | **2023** | `v5.4.0` | 32 | `v5.5.0` | **2 versioni** | `v6.4.0` (+14 v), `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v7.2.0` (+6 v), `v8.12.0` (+29 v), `v8.13.2` (+4 v), `v8.14.1` (+5 v) |
| 22 | **`example22.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.3.0` | **14 versioni** | `v6.4.0` (+2 v), `v6.5.0` (+1 v), `v8.12.0` (+43 v) |
| 23 | **`example23.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 24 | **`example24.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.0.0` | **8 versioni** | `v6.5.0` (+9 v), `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 25 | **`example25.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.1.0` | **10 versioni** | `v6.5.0` (+7 v), `v6.6.5` (+7 v), `v8.0.0` (+16 v), `v8.5.0` (+7 v), `v8.12.0` (+13 v) |
| 26 | **`example26.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.0.0` (+15 v), `v8.12.0` (+20 v) |
| 27 | **`example27.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 28 | **`example28.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.5.0` | **17 versioni** | `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 29 | **`example29.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.2.0` | **11 versioni** | `v6.2.1` (+1 v), `v6.5.0` (+5 v), `v7.0.0` (+8 v), `v8.12.0` (+35 v) |
| 30 | **`example30.cy.ts`** | **2023** | `v5.4.0` | 32 | `v5.5.0` | **2 versioni** | `v6.0.0` (+6 v), `v6.0.1` (+1 v), `v6.5.0` (+8 v), `v6.6.3` (+5 v), `v7.0.0` (+3 v), `v7.6.1` (+13 v), `v8.0.0` (+2 v), `v8.3.1` (+4 v), `v8.12.0` (+16 v) |
| 31 | **`example31.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.4.0` | **16 versioni** | `v6.5.0` (+1 v), `v7.0.0` (+8 v), `v8.1.0` (+16 v), `v8.12.0` (+19 v) |
| 32 | **`example32.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.0.0` | **8 versioni** | `v6.5.0` (+9 v), `v7.0.0` (+8 v), `v7.6.1` (+13 v), `v8.0.0` (+2 v), `v8.5.1` (+8 v), `v8.12.0` (+12 v), `v8.14.0` (+8 v) |
| 33 | **`example33.cy.ts`** | **2023** | `v5.4.0` | 32 | `v6.2.0` | **11 versioni** | `v6.5.0` (+6 v), `v7.0.0` (+8 v), `v8.5.1` (+23 v), `v8.12.0` (+12 v) |
| 34 | **`example34.cy.ts`** | **2023** | `v7.1.0` | 32 | `v8.12.0` | **30 versioni** | *Nessun'altra* |
| 35 | **`example35.cy.ts`** | **2024** | `v7.3.0` | 28 | `v7.6.1` | **6 versioni** | `v8.2.0` (+4 v), `v8.12.0` (+18 v) |
| 36 | **`example36.cy.ts`** | **2024** | `v8.1.0` | 28 | `v8.12.0` | **19 versioni** | *Nessun'altra* |
| 37 | **`example37.cy.ts`** | **2024** | `v8.2.0` | 28 | `v8.12.0` | **18 versioni** | *Nessun'altra* |
| 38 | **`example38.cy.ts`** | **2024** | `v8.5.0` | 28 | `v8.12.0` | **13 versioni** | *Nessun'altra* |
| 39 | **`example39.cy.ts`** | **2024** | `v8.5.0` | 28 | `v8.12.0` | **13 versioni** | *Nessun'altra* |
| 40 | **`example40.cy.ts`** | **2024** | `v8.5.0` | 28 | `v8.12.0` | **13 versioni** | `v8.14.0` (+8 v) |
| 41 | **`example41.cy.ts`** | **2024** | `v8.6.0` | 28 | `v8.6.1` | **1 versioni** | `v8.12.0` (+9 v) |
| 42 | **`example42.cy.ts`** | **2024** | `v8.9.0` | 28 | *Nessuna* | *Mai modificato* | - |
| 43 | **`example43.cy.ts`** | **2024** | `v8.11.0` | 28 | `v8.12.0` | **1 versioni** | `v8.13.2` (+4 v) |
| 44 | **`example44.cy.ts`** | **2025** | `v8.12.0` | 10 | *Nessuna* | *Mai modificato* | - |
| 45 | **`example45.cy.ts`** | **2025** | `v8.13.1` | 10 | `v8.13.2` | **1 versioni** | *Nessun'altra* |
| 46 | **`home.cy.ts`** | **2023** | `v5.4.0` | 32 | `v8.12.0` | **60 versioni** | `v8.13.2` (+4 v) |

---

## 4. Approfondimento: Il Caso di `example18.cy.ts` (2025) vs `example19.cy.ts` (2023)

1. **Perché `example19.cy.ts` è nato nel 2020 in JS (e 2023 in TS)**:
   - Fin dall'era JavaScript esistevano i test da 1 a 17 e poi da 19 a 33. **Il test 18 non è mai esistito fino al 2025** perché l'Esempio 18 della demo Angular era `grid-remote.component.ts` (collegato a un server remoto OData/GraphQL), privo di test E2E automatici locali.
2. **Perché `example18.cy.ts` risulta nato a gennaio 2025 (`v8.12.0`)**:
   - Nel commit `6ab4d1fb` (18 gennaio 2025, *«chore: remove Remote Example & replace with Import from CSV»*), l'autore ha rimosso l'esempio remoto non testabile e ha **rinominato** `example43.cy.ts` $\rightarrow$ `example18.cy.ts`.
   - Due giorni dopo (20 gennaio 2025, commit `d583887f`), lo slot 43 liberato è stato riassegnato creando un nuovo `example43.cy.ts` (`feat: add rowspan implementation`).

