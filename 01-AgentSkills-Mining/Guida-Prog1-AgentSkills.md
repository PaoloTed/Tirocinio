# Prog1 — Tool di analisi per Agent Skills (GitSkills · MSR 2027)

### Guida operativa, piano di lavoro e calendario degli aggiornamenti al professore

**Versione** 1.0 — 23 ottobre 2026
**Documenti di partenza** `ProgTirocinio.txt`, `analisitirociniomd.md`
**Orizzonte** 16 settimane: lun 26/10/2026 → ven 12/02/2027 (+ eventuale sprint MSR 2027, deadline 18 e 23 dicembre 2026)
**Carico ipotizzato** 20–25 ore/settimana. Se lavori a tempo pieno (40 h), comprimi le fasi di ~40%; se lavori 10 h, raddoppia le settimane e rinuncia al binario Challenge.

---

## 0. In 60 secondi

- **Cosa devi produrre**: un tool Python che, dato un repository (o il dataset GitSkills), estrae metriche di processo e di prodotto sulle `SKILL.md`, le salva in un database e le rende leggibili in una dashboard; più una relazione di tirocinio e, se il professore è d'accordo, un paper di 4 pagine per la Mining Challenge.
- **La cosa più urgente**: decidere **se punti alla submission MSR 2027**. La scadenza è il **23 dicembre 2026** (abstract il **18 dicembre**): da lunedì 26 ottobre hai **8 settimane e mezzo**, non 16. Questo va deciso al primo ricevimento (martedì 27 ottobre) o al massimo il 3 novembre.
- **La trappola**: scaricare subito il database da 44,4 GB e iniziare a "esplorare". Si perde una settimana e non si produce nulla. Il primo contatto con i dati va fatto sul campione su GitHub e sul mirror Parquet.
- **La regola d'oro**: entro la settimana 5 devi avere **numeri veri su almeno 200 repository**. Se non li hai, il binario Challenge si chiude e resti sul tirocinio base.

---

## 1. Cosa c'è dentro questo progetto (lettura onesta)

| Voce | Valutazione |
|---|---|
| **Natura** | Costruzione di tool + studio empirico esplorativo su un dataset nuovo |
| **Competenze che acquisisci** | Python, PyDriller, SQL/DuckDB, parsing YAML, analisi testuale, Streamlit |
| **Difficoltà tecnica** | Media. Non c'è nulla di algoritmicamente difficile: è ingegneria dei dati |
| **Difficoltà scientifica** | Alta. Le metriche non esistono, le devi definire e difendere |
| **Rischio principale** | Perdersi nell'esplorazione e arrivare alla settimana 10 senza una domanda di ricerca |
| **Rischio secondario** | Metriche "inventate" senza validazione → risultati non credibili al professore |
| **Segnale di buon fit** | Ti piace fare pipeline, contare cose, e sai stare dentro un perimetro |
| **Segnale di cattivo fit** | Ti annoia definire metriche e preferisci eseguire/debuggare sistemi reali → Prog2 |

**Nota di realismo**: la parte "code smells sulle skill" è la più affascinante e la più rischiosa. Non esiste letteratura: qualunque euristica tu proponga, il professore ti chiederà "come fai a sapere che è un problema?". La risposta si costruisce con **validazione manuale su un campione** (30–50 skill lette a mano). Metti questa attività nel piano, non alla fine.

---

## 2. Mappa dei link: cosa contiene ognuno e cosa devi farci

Stato di verifica: ✅ consultato il 23/10/2026 · ⚠️ accesso parziale · ➖ non ancora verificato

| # | Link | Cosa contiene (verificato) | Cosa devi fare concretamente | Entro |
|---|---|---|---|---|
| 1 | ✅ [CFP MSR 2027 Mining Challenge](https://2027.msrconf.org/track/msr-2027-mining-challenge) | Bando completo: due dataset (GitSkills e SpecMine), 5 aree di domande di ricerca, regole di sottomissione, date, policy open science | Leggilo **tutto** una volta (30 min). Salva la pagina in PDF in `docs/letteratura/`. Estrai: (a) le 5 aree di RQ, (b) il formato 4+1 pagine, (c) le date. È il documento che definisce il "successo" del progetto | Ven 30/10 |
| 2 | ✅ [Preprint GitSkills — arXiv:2608.10906](https://arxiv.org/abs/2608.10906) | Paper di 3 pagine sulla costruzione del dataset: schema delle 4 tabelle, pipeline di raccolta, limiti | Leggilo 2 volte: la prima veloce (20 min), la seconda con la scheda di lettura (§3) in mano. Scarica il PDF e l'HTML sperimentale. **È la fonte primaria per capire il dato** | Mar 27/10 |
| 3 | ✅ [Dataset GitSkills — Zenodo](https://doi.org/10.5281/zenodo.21875637) | Un unico file SQLite `agent_skills_release.db` da **44,4 GB** (md5 `b058631fb1926efac6e82a4706646742`), v1.0.0, 10/08/2026, licenza CC-BY-4.0 | **Non scaricarlo ora.** Aprilo solo quando hai una query pronta e spazio disco verificato (≥120 GB liberi). Quando lo scarichi: `curl -L -C -` + verifica md5 | Sett. 4–5 |
| 4 | ✅ [Mirror Parquet — Hugging Face](https://huggingface.co/datasets/mvaccargiu/gitskills) | Stesse tabelle in Parquet, partizionate; la **dataset card contiene il dizionario colonna-per-colonna** che il paper non ha | Leggi la dataset card (20 min) e annota i nomi esatti delle colonne in `docs/02_dataset.md`. Poi leggi i Parquet con DuckDB, senza scaricare il DB | Mar 3/11 |
| 5 | ✅ [Campione GitSkills — GitHub](https://github.com/giuseppedestefanis/gitskills-sample) | Sottoinsieme del dataset, pensato per iniziare | `git clone`, apri con `sqlite3`/DuckDB, conta le righe, leggi 20 `SKILL.md` intere a mano | Lun 26/10 |
| 6 | ✅ [Documentazione PyDriller](https://pydriller.readthedocs.io/en/latest/) | API per il mining Git: `Repository`, `Commit`, `ModifiedFile`, metriche di processo | Leggi Tutorial + Repository + Commit + ModifiedFile (2 h). Poi scrivi `spike_pydriller.py` che stampa i commit che toccano una `SKILL.md` | Mer 4/11 |
| 7 | ✅ [PyDriller su GitHub](https://github.com/ishepard/pydriller) | Codice sorgente, issue, changelog. Ultima versione su PyPI: **2.12** (11/09/2026) | Consultalo solo per bug. Pinna `pydriller==2.12` nel `requirements.txt` | — |
| 8 | ✅ [Lizard](https://github.com/terryyin/lizard) | Analizzatore multi-linguaggio, dipendenza di PyDriller | Serve **solo** se decidi di misurare gli script allegati alle skill. Altrimenti ignoralo | Sett. 3, se serve |
| 9 | ➖ Specifica `SKILL.md` (Anthropic, ott. 2025) | Formato: cartella + `SKILL.md` con front-matter YAML (campi tipici `name`, `description`) + corpo | Cercala sul sito Anthropic e archiviala: ti serve per giustificare le metriche sul front-matter. **Chiedi al professore se ha un riferimento canonico** | Entro il 27/10 |
| 10 | ✅ [SpecMine — arXiv:2608.25202](https://arxiv.org/abs/2608.25202) | Secondo dataset della challenge: artefatti di Spec-Driven Development | **Solo** se il professore propone di combinare i due dataset (il bando lo permette). Leggi l'abstract, non di più | Sett. 2 (decisione) |

### Cosa NON fare con questi link

- ❌ Non scaricare il DB da 44 GB "per curiosità": se lo fai prima di avere una query, resti 40 minuti a guardare tabelle.
- ❌ Non leggere il CFP dopo il paper: il CFP ti dice quali domande interessano ai revisori, il paper ti dice com'è fatto il dato. In quest'ordine.
- ❌ Non citare SpecMine nel paper se non lo usi: i revisori della challenge se ne accorgono.

---

## 3. Scheda di lettura (template da compilare per ogni fonte)

Crea `docs/letteratura/schede/<nome>.md` per ognuna delle fonti 1, 2, 4, 9 e per i paper che leggerai dopo. Senza scheda, il paper "l'hai letto" ma non lo sai usare.

```markdown
# <Titolo>
- Riferimento (DOI/URL):
- Tipo: paper / dataset / bando / specifica
- Domanda che pone:
- Unità di analisi (file? repo? contenuto distinto?):
- Dati usati e periodo di raccolta:
- Metodo in 3 righe:
- Risultati chiave (max 3, con numeri):
- Definizioni riutilizzabili per me:
- Limiti dichiarati dagli autori:
- 3 idee che mi danno:
- Dove lo citerò:
```

**Tempo realistico**: 40 min per scheda fatta bene. 5 schede = mezza giornata. È il miglior investimento delle prime due settimane.

---

## 4. Setup tecnico (mezza giornata, da fare lunedì 26/10)

### 4.1 Struttura del progetto

```text
Prog1/                             <- radice del progetto (cartella 01-AgentSkills-Mining)
├─ docs/
│  ├─ 00_decisioni.md              <- registro delle decisioni (obbligatorio)
│  ├─ 01_dominio.md
│  ├─ 02_dataset.md
│  ├─ 03_metriche.md
│  ├─ letteratura/                 <- PDF (già presente il preprint GitSkills) + schede/
│  └─ verbali/2026-10-27.md        <- uno per ogni incontro
├─ sql/                            <- query salvate e versionate
├─ src/
│  ├─ extract_git.py
│  ├─ parse_skill.py
│  ├─ store.py
│  └─ cli.py
├─ notebooks/
├─ data/                           <- gitignored (DB, parquet, repo clonati)
├─ results/
├─ requirements.txt
└─ README.md
```

**Già scaricato**: `docs/letteratura/GitSkills_arXiv_2608.10906.pdf` (3 pagine, v3 dell'11/09/2026). È il preprint che devi leggere in settimana 1; il PDF sul sito arXiv è esattamente la versione citata dal bando. Il CFP della challenge invece è una pagina web: salvala in PDF con `Ctrl+P` → "Salva come PDF" in `docs/letteratura/`, perché il bando può cambiare e tu devi poter dimostrare a quale versione ti sei allineato.

### 4.2 Comandi (PowerShell, dalla cartella `01-AgentSkills-Mining`)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "pydriller==2.12" duckdb pandas pyarrow python-frontmatter pyyaml streamlit
pip freeze > requirements.txt
```

Verifica:

```powershell
python -c "import pydriller, duckdb; print(pydriller.__version__ if hasattr(pydriller,'__version__') else 'ok')"
```

### 4.3 Spazio disco

```powershell
Get-PSDrive C | Select-Object Used,Free
```

Servono **≥120 GB liberi** se scarichi il DB (44 GB compresso/spacchettato + indici + risultati). Se hai meno spazio, resta su Parquet/Hugging Face per tutto il tirocinio: è una scelta legittima e va detta al professore.

### 4.3-bis Dove eseguire: PC locale o Google Colab

| Ambiente | Va bene per | Non va bene per |
|---|---|---|
| **PC locale** | pipeline, DB locale, dashboard Streamlit, consegna del tool | analisi su dataset intero se hai <120 GB |
| **Google Colab** | analisi esplorativa sul **mirror Parquet** (DuckDB/pandas/grafici), notebook da condividere col professore | scaricare il **DB da 44 GB** a ogni sessione; pipeline di consegna (serve un artefatto riproducibile) |
| **Server di laboratorio** | dataset intero, job lunghi | — (da chiedere al professore) |

Regola pratica: **Colab è un ambiente di analisi, non di produzione**. Il deliverable deve girare con `python -m src.cli run` sulla macchina di chi valuta, altrimenti non è riproducibile. Su Colab lavora sui Parquet di Hugging Face, non sul file SQLite: il DB da 44 GB richiede ore di download e una sessione che scade prima di aver finito.

### 4.4 Il primo script (30 righe, da scrivere davvero)

```python
# src/extract_git.py — spike iniziale
from pydriller import Repository

def commit_che_toccano_skill(repo_path: str, path_glob: str = "SKILL.md"):
    for commit in Repository(repo_path, filepath=path_glob).traverse_commits():
        for mf in commit.modified_files:
            yield {
                "hash": commit.hash,
                "data": commit.author_date.date().isoformat(),
                "autore": commit.author.name,
                "file": mf.new_path or mf.old_path,
                "n_added": mf.added_lines,
                "n_deleted": mf.deleted_lines,
                "msg": commit.msg,
            }
```

Se questo gira su 3 repository clonati a mano, hai superato lo scoglio tecnico principale del progetto.

---

## 5. Piano di lavoro — 16 settimane

Legenda: **D** = deliverable verificabile · **G** = gate (decisione che blocca il resto)

### Fase 0 — Dominio e dataset (sett. 1–2, 26/10 → 6/11)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 1 | 26–30/10 | Capire il fenomeno e il dato | Setup repo e venv · clone del campione · lettura di **20 `SKILL.md` intere** (non 200: 20 lette davvero) · scheda del preprint · scheda del CFP · 3 RQ candidate | **D**: `docs/01_dominio.md` (2 pagine), scheda preprint, 3 RQ · **G0** scelta progetto |
| 2 | 2–6/11 | Avere i numeri del dataset | Dataset card HF · conteggi di sanità (righe per tabella, repo distinti, distribuzione per `location class`, % di hash duplicati, distribuzione stars) · definizione dell'unità di analisi (**contenuto distinto** vs **occorrenza**) · scelta RQ | **D**: `docs/02_dataset.md` con numeri riprodotti + `sql/01_sanity.sql` · **G1** RQ scelta |

**Nota metodologica importante.** Il dataset ha due livelli: 3.797.117 occorrenze (file) e 1.877.981 contenuti distinti. **Ogni analisi deve dichiarare su quale livello lavora.** Se conti gli smell per occorrenza, stai misurando la popolarità delle copie, non la qualità delle skill. Scrivilo nel documento: è il tipo di distinzione che il professore apprezza.

### Fase 1 — Metriche (sett. 3–4, 9/11 → 20/11)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 3 | 9–13/11 | Definire 8–10 metriche difendibili | Per ognuna: definizione operativa, query/regola di calcolo, motivazione, falsi positivi attesi. Famiglie: **processo** (n. commit sulla skill, età ultima modifica, n. autori, lunghezza messaggi), **prodotto** (righe/parole, front-matter valido, n. sezioni, presenza di esempi, presenza di script), **riuso** (n. copie, similarità), **rischio** (comandi eseguibili, URL, percorsi assoluti, credenziali) | **D**: `docs/03_metriche.md` + estrazione su campione stratificato di **500 repo** → `results/metriche_v0.parquet` |
| 4 | 16–20/11 | Pipeline end-to-end | `extract_git.py` + `parse_skill.py` + `store.py` (DuckDB: le query analitiche su Parquet sono molto più veloci che su SQLite) · un comando solo per rifare tutto | **D**: pipeline che gira su 50 repo con `python -m src.cli run --sample 50` · **G1b** metriche congelate |

**Campione stratificato**: non 500 repo a caso. Stratifica per età del repo, popolarità (stars), lingua principale e `location class`. Scrivi i criteri prima di estrarre e conserva il seed: la riproducibilità si gioca qui.

### Fase 2 — Numeri veri (sett. 5, 23–27/11)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 5 | 23–27/11 | Risultati su ≥200 repo + validazione manuale | Analisi esplorativa (distribuzioni, correlazioni) · **lettura manuale di 30–50 skill** per etichettare a mano presenza/assenza del fenomeno · precisione/richiamo delle euristiche · 2 figure | **D**: `results/report_v1.md` + figura 1 e 2 · **G2 = GO/NO-GO Challenge** |

**G2 è il gate più importante del progetto.** Criterio esplicito: hai almeno una tabella con numeri stabili e una figura che racconta qualcosa di non ovvio? Se sì → si scrive il paper. Se no → si chiude il binario Challenge, si continua il tirocinio con più calma e si spiega al professore *perché* (non è un fallimento: è un risultato).

### Fase 3 — Sprint challenge (sett. 6–8, 30/11 → 23/12)

| Sett. | Date | Obiettivo | Attività | D / G |
|---|---|---|---|---|
| 6 | 30/11–4/12 | Draft sezioni 1–3 | Introduzione (0,75 pag), Related work (0,5), Metodo (1 pag). Riusa le schede di lettura per il related | **D**: `paper/draft.md` con §1–3 |
| 7 | 7–11/12 | Draft completo | Risultati (1,25 pag) + minacce alla validità (0,25) + conclusioni (0,25). **8/12 è festivo: niente ricevimento**, si lavora e si manda l'email | **D**: draft completo 4 pagine in template IEEE |
| 8 | 14–18/12 | Freeze e submission | Correzione bozze · anonimizzazione (double-blind: niente nomi, niente link al tuo GitHub personale) · abstract entro **ven 18/12** · paper entro **mer 23/12** su HotCRP | **D**: abstract inviato · **D**: paper inviato |

### Fase 4 — Estensione e chiusura tirocinio (sett. 9–16, 4/01 → 12/02)

| Sett. | Date | Obiettivo | Attività | D |
|---|---|---|---|---|
| 9–10 | 21/12 → 1/01 | Bassa intensità (festivi) | Solo lavoro leggero: riordino del repo, pulizia query, note per la relazione. Nessuna decisione di design | — |
| 11 | 4–8/01 | Retrospettiva e piano B | Cosa ha funzionato, cosa no · decidere l'estensione (dataset intero o campione più grande) | `docs/04_retrospettiva.md` |
| 12 | 11–15/01 | Estensione del campione | Da 500 a 5.000 repo (o query aggregate sul DB completo per le metriche che non richiedono testo) | `results/metriche_v2.parquet` |
| 13 | 18–22/01 | Analisi per coorti | Skill per mese di creazione: cambia la struttura? cambia la lingua? cambia la lunghezza? | `notebooks/03_coorti.ipynb` |
| 14 | 25–29/01 | Dashboard | Streamlit: timeline commit di un repo, metriche per skill, flag di smell | `src/dashboard.py` |
| 15 | 1–5/02 | Relazione: scheletro + risultati | Scrivi mentre i numeri sono freschi. 20–30 pagine | `docs/relazione/bozza.md` |
| 16 | 8–12/02 | Consegna | Revisione finale, README, rilascio del tool su GitHub con licenza | Relazione + repo pubblico |

---

## 6. Calendario dei martedì (ricevimento, mattina)

**Regola operativa**: l'email parte **lunedì entro le 18:00**; il ricevimento è di 10 minuti, non di 40. Il martedì non si "racconta" cosa hai fatto: si **mostra** un artefatto e si chiede **una decisione**.

| # | Data | Cosa porti | Decisione che chiedi | Note |
|---|---|---|---|---|
| 1 | **mar 27/10** | Scelta del progetto dichiarata · scheda del preprint · 3 RQ candidate · campione già aperto | (a) le RQ vanno bene? (b) **puntiamo alla challenge MSR 2027?** (c) formato e scadenza della relazione di tirocinio (d) posso avere accesso a storage per il DB da 44 GB? | Primo incontro: porta anche le domande di §11 |
| 2 | **mar 3/11** | Numeri del dataset riprodotti · unità di analisi definita · query salvate | (a) confermi il campione stratificato da 500? (b) quale metrica interessa di più al gruppo? | |
| 3 | **mar 10/11** | `03_metriche.md` stampato (2 copie) | Quali 3 metriche taglieresti? Le mie euristiche di "smell" sono difendibili? | Vai con le definizioni, non con le slide |
| 4 | **mar 17/11** | Pipeline che gira su 50 repo (demo dal vivo, 2 min) | Posso congelare le metriche e passare alla scala? | Se la demo si rompe, hai comunque il log |
| 5 | **mar 24/11** | Report v1 + 2 figure + validazione manuale | **GO / NO-GO** sulla submission del 23/12 | Porta anche il piano B |
| 6 | **mar 1/12** | Draft §1–3 | Il framing della domanda di ricerca funziona per i revisori MSR? | |
| 7 | **mar 8/12** | *Nessun ricevimento (Immacolata)* | — | Manda comunque l'email con il draft completo; chiedi commenti entro l'11/12 |
| 8 | **mar 15/12** | Draft completo 4 pagine | Ultime correzioni · conferma della submission · come firmare/affiliazione · eventuale ordine autori | Ultimo incontro utile prima della deadline |
| — | **ven 18/12** | Abstract su HotCRP | — | Scadenza dura, AoE |
| — | **mer 23/12** | Paper su HotCRP | — | Scadenza dura, AoE. Non contare sul ricevimento del 22/12 |
| 9 | **mar 22/12** | *Sospensione natalizia (presunta)* | — | Email facoltativa di 3 righe |
| 10 | **mar 29/12** | *Sospensione natalizia (presunta)* | — | — |
| 11 | **mar 5/01** | Retrospettiva del binario Challenge | Come impostiamo le ultime 6 settimane? Cosa va nella relazione e cosa no? | Verifica prima se il ricevimento riprende |
| 12 | **mar 12/01** | Numeri estesi (5.000 repo) | Il campione allargato conferma o smentisce i risultati del campione piccolo? | |
| 13 | **mar 19/01** | Analisi per coorti | Quale storia raccontiamo nella relazione? | |
| 14 | **mar 26/01** | Dashboard v1 | La dashboard serve alla relazione o è un di più? | |
| 15 | **mar 2/02** | Scheletro della relazione + indice | Va bene questa struttura? Cosa vuole vedere assolutamente? | |
| 16 | **mar 9/02** | Bozza avanzata della relazione | Revisione finale e data di consegna | |

**Se un martedì salta** (festivo, impegni): l'email parte lo stesso. Il silenzio, in un tirocinio, viene letto come stallo.

---

## 7. Come si scrive l'aggiornamento (template)

### 7.1 Email del lunedì (max 120 parole)

```text
Oggetto: [Tirocinio][Prog1] Settimana 3 — <Nome>

Buongiorno Prof. <Cognome>,
aggiornamento breve prima del ricevimento di domani.

Fatto: pipeline di estrazione completata su 50 repository; 8 metriche implementate.
Numeri: 12.480 skill distinte, 31% senza front-matter valido, mediana 42 righe.
Blocco: il parsing del front-matter fallisce sull'8% dei file (YAML non valido).
Mi serve una decisione: (a) tratto i file non parsabili come categoria a sé o li escludo?
(b) confermo il passaggio a 500 repository o resto su 50 per la validazione?

Grazie,
<Nome>
```

**Le tre cose che non devono mai mancare**: un numero, un blocco, una domanda chiusa (con opzioni, non "come procedo?").

### 7.2 Agenda dei 10 minuti in presenza

| Min | Cosa |
|---|---|
| 0–2 | Mostra l'artefatto (tabella, figura, demo). Non raccontare: fai vedere |
| 2–5 | I numeri che contano, in ordine di importanza |
| 5–9 | Le 2–3 domande, in ordine di importanza decrescente. Annota le risposte *mentre parla* |
| 9–10 | Conferma il prossimo passo e la data. "Quindi per martedì 10 le porto X" |

### 7.3 Verbale (entro 2 ore dall'incontro)

`docs/verbali/2026-10-27.md`:

```markdown
# 2026-10-27 — Ricevimento
Presenti:
## Decisioni
1. ...
## Azioni
- [ ] <azione> — entro <data>
## Domande aperte
- ...
## Prossimo incontro: 2026-11-03
```

Se ci sono state decisioni che cambiano il piano, manda un **recap di 3 righe** entro sera ("confermo quanto deciso: ..."). Evita le incomprensioni più costose del tirocinio.

### 7.4 Quando scrivere fuori dal martedì

Solo in tre casi:

1. **Blocco** che ti impedisce il deliverable settimanale da più di 48 ore (es. non hai accesso al dataset).
2. **Decisione critica con scadenza** (GO/NO-GO challenge, abstract del 18/12).
3. **Problema etico o sui dati** (dati personali, licenze, uso di repository privati).

Tutto il resto si mette in coda per il martedì. Non mandare più di 2–3 email fuori cadenza in tutto il tirocinio.

---

## 8. Il taglio minimo pubblicabile (per il paper da 4 pagine)

Se vai alla challenge, il paper ha **4 pagine + 1 di riferimenti**. Non ci sta tutto: ci sta **una** domanda di ricerca. Struttura consigliata:

| Sezione | Pagine | Contenuto |
|---|---|---|
| Introduzione | 0,75 | Il fenomeno (skill in linguaggio naturale, nessun registry, copia diretta) + la domanda + il contributo in 3 punti |
| Lavoro correlato | 0,5 | Dataset GitSkills, studi su cloni e riuso del codice, letteratura su qualità di artefatti NL. Poche citazioni, scelte bene |
| Metodo | 1,0 | Dataset e versione, unità di analisi, definizione operativa della metrica, campione, validazione manuale |
| Risultati | 1,25 | 1 tabella + 2 figure. Numeri assoluti e percentuali. Un risultato non ovvio |
| Minacce alla validità | 0,25 | Costrutto (la metrica misura davvero la qualità?), esterno (campione), riproducibilità |
| Conclusioni | 0,25 | Cosa abbiamo imparato + 2 righe di lavoro futuro |
| Etica | — | Paragrafo breve prima delle conclusioni, richiesto dal bando |

**Shortlist di domande di ricerca** (scegline **una**):

| RQ | Domanda | Costo | Rischio | Giudizio |
|---|---|---|---|---|
| A | **Divergenza delle copie**: quando una skill viene copiata e poi modificata, cosa cambia? Le copie divergenti aggiungono comandi eseguibili o accessi di rete assenti nell'originale? | Medio | Basso-medio | **Raccomandata**. È la RQ 5.2 del bando, ha impatto (supply chain senza registry) ed è misurabile con hash + diff testuale |
| B | **Qualità della `description`**: quali proprietà della descrizione (lunghezza, specificità, presenza di trigger) si associano a più copie e più manutenzione? | Basso | Medio | Buona per un paper veloce, ma "description di qualità" è difficile da definire senza arbitrarietà |
| C | **Manutenzione e abbandono**: età, churn, skill orfane; il tempo tra creazione e ultima modifica | Basso | Basso | Facile ma poco sorprendente: rischio "descrittivo" |
| D | **Metriche classiche sulle skill**: dimensione, churn, età, clone coverage — come si distribuiscono rispetto al codice? | Basso | Basso | Va bene come sezione di un paper più grande, non come paper intero |
| E | **Multilinguismo**: in quali lingue sono scritte le skill e cambia la struttura? | Basso | Medio | Originale, ma richiede language detection affidabile |

Se scegli A, il disegno è: prendi i contenuti con molte occorrenze (alto riuso), confronta ogni occorrenza con il rappresentante del gruppo (hash diverso = copia modificata), calcola similarità e diff; cerca nei diff l'aggiunta di pattern di rischio (`curl|bash`, `rm -rf`, URL, percorsi assoluti, token). Valida a mano su 30 casi. Questa è una pipeline da ~150 righe di Python, non da 3.000.

---

## 9. Cosa guarda il professore quando valuta

1. **Se sai dire cosa hai misurato e perché** (definizioni operative, non aggettivi).
2. **Se i numeri sono riproducibili** (query salvate, seed, versione del dataset).
3. **Se hai validato a mano** almeno un campione.
4. **Se hai rispettato il perimetro** (una RQ fatta bene > cinque abbozzate).
5. **Se sai scrivere**: la relazione non è un diario, è un argomento.

---

## 10. Rischi e contromisure

| Rischio | Probabilità | Impatto | Contromisura |
|---|---|---|---|
| Perdersi nell'esplorazione del dataset | Alta | Alto | Gate G2 il 24/11: senza numeri, niente challenge |
| Metriche arbitrarie, non difendibili | Alta | Medio | Validazione manuale su 30–50 skill + dichiarazione dei falsi positivi |
| DB da 44 GB ingestibile (spazio/tempo) | Media | Medio | Resta su Parquet/HF; il DB intero serve solo per query aggregate |
| PyDriller troppo lento su migliaia di repo | Media | Medio | Usa le commit history già nel dataset (458.548) invece di clonare tutto |
| Deadline 23/12 | Certa | Alto | Freeze il 15/12; se il 24/11 il gate è rosso, si rinuncia subito |
| Il professore cambia idea sullo scope | Media | Medio | Verbale scritto dopo ogni incontro + registro decisioni |

---

## 11. Domande da portare al primo incontro (27/10)

1. Il progetto deve restare un tool interno o puntiamo alla submission MSR 2027 (abstract 18/12, paper 23/12)?
2. Le metriche le definisco io o c'è una lista che il gruppo si aspetta?
3. C'è una versione del dataset da usare come riferimento (la v1.0.0 di agosto 2026)?
4. Posso avere accesso a storage/macchina per il DB da 44 GB, o resto su Hugging Face?
5. Chi altro nel gruppo lavora su GitSkills? Posso parlargli?
6. La relazione di tirocinio ha un formato e una lunghezza attesi? Qual è la scadenza per i CFU?
7. Va bene se pubblico il tool su GitHub con licenza MIT/Apache?
8. Ci sono vincoli di riservatezza o embargo sui dati?
9. Le va bene questa cadenza: email il lunedì sera + 10 minuti al ricevimento del martedì?
10. Se il lavoro produce un paper, come preferisce essere citato e chi sono gli autori?

---

## 12. Checklist master

**Settimana 1**
- [ ] Repo e struttura cartelle creati, venv funzionante
- [ ] Campione clonato e aperto
- [ ] 20 `SKILL.md` lette a mano
- [ ] Scheda del preprint compilata
- [ ] Scheda del CFP compilata
- [ ] 3 RQ candidate scritte
- [ ] Email del lunedì inviata
- [ ] Verbale del primo incontro scritto

**Settimana 2**
- [ ] Dataset card HF letta, colonne annotate
- [ ] 6 conteggi di sanità riprodotti
- [ ] Unità di analisi dichiarata (contenuto vs occorrenza)
- [ ] RQ scelta
- [ ] `docs/00_decisioni.md` aggiornato

**Gate G2 (24/11)**
- [ ] Numeri su ≥200 repo
- [ ] 2 figure
- [ ] Validazione manuale su ≥30 skill
- [ ] Decisione GO/NO-GO scritta nel verbale

**Prima della submission**
- [ ] Template IEEE (`\documentclass[10pt,conference]{IEEEtran}`)
- [ ] 4 pagine + 1 di riferimenti, senza sforare
- [ ] Doppio anonimato: nessun nome, nessun link identificativo
- [ ] Dataset citato con versione e DOI
- [ ] Paragrafo etico
- [ ] Abstract caricato entro il 18/12
- [ ] PDF caricato su HotCRP entro il 23/12

---

## 13. Registro delle decisioni

Compila `docs/00_decisioni.md` con questa tabella. Serve a te tra due mesi, e al professore per capire perché il piano è cambiato.

| Data | Decisione | Motivazione | Chi | Impatto |
|---|---|---|---|---|
| 2026-10-23 | Preparare le guide per entrambi i progetti prima di scegliere | Confronto informato | Paolo | — |
| | | | | |

---

*Guida redatta il 23 ottobre 2026. Informazioni su dataset, preprint e bando verificate alla stessa data sulle fonti ufficiali. Le date dei ricevimenti sono ipotizzate settimanali al martedì mattina e vanno confermate con il professore.*
