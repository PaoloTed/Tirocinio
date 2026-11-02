# Specifiche e Formalizzazione delle Metriche sul Ciclo di Vita dei Test E2E

Questo documento definisce formalmente le metriche matematiche, la tassonomia delle modifiche e gli algoritmi di estrazione per lo studio dell'**evoluzione e del ciclo di vita dei test E2E GUI**, in conformità con gli obiettivi concordati con il Prof. Luigi Libero Lucio Starace.

---

## 1. Modello Formale della Storia Git

Sia un repository software $R = \langle C, \prec \rangle$, dove:
* $C = \{c_1, c_2, \dots, c_N\}$ è l'insieme ordinato nel tempo dei commit totali dell'applicazione.
* $\prec$ è la relazione d'ordine topologico e cronologico sui commit ($c_i \prec c_j$ indica che $c_i$ precede $c_j$).
* $F = \{f_1, f_2, \dots, f_M\}$ è l'insieme dei file di test E2E GUI registrati in `tests_gui.csv`.
* Per ogni file di test $f \in F$, sia $C(f) \subseteq C$ il sottoinsieme dei commit che hanno introdotto o modificato $f$:
  $$C(f) = \{ c_{f, 1}, c_{f, 2}, \dots, c_{f, k} \} \quad \text{con } c_{f, 1} \prec c_{f, 2} \prec \dots \prec c_{f, k}$$

---

## 2. Metriche di Timeline e Ciclo di Vita

```text
       t_birth (Nascita)                Modifica 1                   Modifica 2                t0 (Snapshot)        HEAD (Oggi)
Commit:   c_{f,1} ---------------------> c_{f,2} ------------------> c_{f,3} -------------> c_snapshot ---------> c_head
             |                             |                            |                         |                    |
             |<--- Delta_first_mod ------->|<---- Delta_intermedio ---->|                         |<---- N_mod ------->|
                 (Commit app senza cambi)      (Commit app intermedi)                                 (Attività recente)
```

### 2.1 Commit di Nascita ($t_{\text{birth}}$)
Il commit e la data di prima introduzione del file di test nel repository:
$$t_{\text{birth}}(f) = c_{f, 1} = \min_{\prec} C(f)$$
* **Comando Git**:
  ```bash
  git log --diff-filter=A --format="%H|%ci" -- <test_path>
  ```
* **Output**: Hash del commit ($H_{\text{birth}}$) e timestamp ISO ($T_{\text{birth}}$).

---

### 2.2 Ritardo alla Prima Modifica ($\Delta_{\text{first\_mod}}$)
Rappresenta il numero di commit totali dell'applicazione intercorsi tra la nascita del test e la sua prima manutenzione successiva:
$$\Delta_{\text{first\_mod}}(f) = |\{ c \in C \mid c_{f, 1} \prec c \preceq c_{f, 2} \}|$$
* **Interpretazione scientifica**:
  * $\Delta_{\text{first\_mod}} \approx 0$: Il test co-evolve strettamente con l'applicazione fin dalla sua creazione.
  * $\Delta_{\text{first\_mod}} \gg 100$: Il test è rimasto congelato e non manutenuto per molte release/commit dell'applicazione prima che qualcuno lo aggiornasse.

---

### 2.3 Intervallo Medio tra Modifiche Consecutive ($\overline{\Delta}_{\text{mod}}$)
Misura la frequenza media di aggiornamento del test durante il suo intero ciclo di vita:
$$\overline{\Delta}_{\text{mod}}(f) = \frac{1}{k - 1} \sum_{i=1}^{k-1} |\{ c \in C \mid c_{f, i} \prec c \preceq c_{f, i+1} \}|$$

---

### 2.4 Modifiche Post-Snapshot ($N_{\text{mod}}$)
Numero di commit che hanno toccato il file di test nel periodo compreso tra lo snapshot del paper ($t_0$ = marzo 2024, `last_commit_sha`) e l'ultimo commit di oggi (HEAD):
$$N_{\text{mod}}(f) = |\{ c \in C(f) \mid c_{\text{snapshot}} \prec c \preceq \text{HEAD} \}|$$

* **Classificazione dello stato del test**:
  $$\text{Stato}(f) = \begin{cases} 
  \textbf{Cancellato/Migrato} & \text{se } f \notin \text{Tree}(\text{HEAD}) \\ 
  \textbf{Congelato (Dormant)} & \text{se } f \in \text{Tree}(\text{HEAD}) \land N_{\text{mod}}(f) = 0 \\ 
  \textbf{Mantenuto Attivo} & \text{se } f \in \text{Tree}(\text{HEAD}) \land N_{\text{mod}}(f) > 0 
  \end{cases}$$

---

### 2.5 Rapporto di Co-Evoluzione ($R_{\text{co-evol}}$)
Rapporto tra il numero di modifiche al test e il numero complessivo di commit dell'applicazione nello stesso intervallo temporale:
$$R_{\text{co-evol}}(f) = \frac{|C(f)|}{|C|} \times 100 \quad [\%]$$
* Nella letteratura sui test web GUI (Pontillo et al., *IST 2025*), questo valore ha una mediana molto bassa ($< 0.5\%$), a conferma che i test GUI cambiano raramente rispetto al codice sorgente.

---

## 3. Tassonomia delle Modifiche al Codice di Test (Diff Classification)

Quando viene rilevata una modifica $c_{f, i} \rightarrow c_{f, i+1}$, il diff unificato ($\Delta_{\text{code}}$) viene classificato tramite espressioni regolari (regex) ad alta precisione:

| Categoria Modifica | Significato Ingegneristico | Esempi di pattern (Regex) |
|---|---|---|
| **`cambio_selettori`** | Aggiornamento dei locatori DOM dell'interfaccia web (ID, classi, attributi di test, XPath). | `(?i)(#\|\.\|\[)[\w-]+\]?['"]\|getBy(Role\|Text\|TestId)\|By\.\w+\|data-test` |
| **`cambio_asserzioni`** | Modifica degli oracoli di test (regole di verifica, stati attesi, valori di ritorno). | `(?i)\b(assert\|expect\|should\|verify\|to\.equal\|toBe)\b` |
| **`cambio_wait`** | Inserimento o modifica di timeout e attese esplicite per contrastare la *flakiness*. | `\b(sleep\|wait\|timeout\|waitForSelector\|waitForLoadState)\b` |
| **`versione_dipendenza`** | Modifica a configurazioni del framework di test o versioni di libreria. | `"(version\|cypress\|playwright\|selenium)":\s*"\|version\s*=\s*"\d` |
| **`riformattazione`** | Modifica puramente sintattica o di formattazione (spazi, virgole, parentesi). | `^\s*[-+]\s*[{}();,]*\s*$` |
| **`riscrittura`** | Più di 4 righe cambiate con combinazione di molteplici logiche. | Ristrutturazione estesa della suite di test. |

---

## 4. Algoritmo Operativo per Singolo File di Test

1. **Estrazione Commit di Nascita**:
   ```bash
   git log --diff-filter=A --format="%H|%ad" --date=iso -- <test_path>
   ```
2. **Estrazione Cronologia delle Modifiche**:
   ```bash
   git log --format="%H|%ad|%s" --date=short -- <test_path>
   ```
3. **Calcolo dei Commit Applicativi Intermedi**:
   Per ciascuna coppia di commit consecutivi $c_1, c_2$:
   ```bash
   git rev-list --count c1..c2
   ```
4. **Ispezione e Classificazione del Diff**:
   ```bash
   git diff -U0 c1 c2 -- <test_path>
   ```
   Analisi riga per riga contro le regex della tassonomia.

