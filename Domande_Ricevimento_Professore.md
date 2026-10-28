# Domande e Punti da Discutere al Ricevimento con il Professore
**Progetto di riferimento**: Prog2 — Esecuzione e manutenzione di test E2E sul dataset E2EGit (`02-E2EGit-TestE2E`)  
**Stato preliminare**: Dataset `E2EGit.db` (v3) già scaricato, ispezionato e convertito nei 5 file CSV operativi (`repos_gui.csv`, `tests_gui.csv`, `tests_perf.csv`, `repos_url.csv`, `repos_commit.csv`). Letti il paper *E2EGit* (MSR 2025, C4) e i lavori correlati del gruppo (*C5*, *J8*, *PT-LINTR / C14*).

---

## 💬 Come introdurre il colloquio (in 30 secondi)
> *"Buongiorno Professore. Ho studiato il paper E2EGit (`C4`) insieme ai vostri lavori successivi sui test Web GUI (`J8` su Information and Software Technology e `C16` sulle migrazioni di framework), e ho già estratto ed esplorato le tabelle da `E2EGit.db` verificando gli 8.601 file di test GUI su 472 repository e gli SHA di snapshot in `last_commit_sha` (marzo 2024). Ho visto che in `J8` avete scoperto che i test GUI subiscono pochissime modifiche dopo la creazione (mediana di 3 modifiche su oltre 1.180 commit dell'app) lasciando aperta la domanda se restino stabili o vengano abbandonati. Prima di partire, vorrei allinearmi con lei su cosa è già stato fatto e su come impostare l'esecuzione e il riuso dei vostri dataset."*

---

## 1. Recupero del lavoro già avviato e Riuso dei Dataset del Gruppo (`J8` e `C16`)
Poiché il progetto è indicato in `ProgTirocinio.txt` come continuazione di un'attività esistente e si collega direttamente a `J8` e `C16`:

1. **Repository già eseguiti e risultati pregressi**: Quali repository (dei 472 GUI o degli 84 di performance) sono già stati presi in esame o eseguiti da chi ha lavorato prima di me? Esiste un file/database con gli esiti dei test già raccolti, i log di build o la lista dei repository scartati perché non eseguibili (`setup_failed`)?
2. **Pipeline e script esistenti**: Esiste già una pipeline di orchestrazione (script Python, Dockerfile, configurazioni per browser headless) che posso riusare ed estendere, oppure devo progettarla da zero?
3. **Passaggio di consegne**: C'è un dottorando, assegnista o ex-tirocinante che ha seguito finora il lavoro con cui posso fare una call di 20 minuti per farmi spiegare i problemi pratici già incontrati?
4. **Riuso dei dati e degli script di `J8` ([Zenodo 15882798](https://zenodo.org/records/15882798))**:
   - Nel paper **`J8`** (*Investigating the Adoption and Maintenance of Web GUI Testing*, IST 2025/2026) avete già calcolato per i file di test le metriche di sopravvivenza e modifica (`SV_Day`, `SV_Mod`, `SV_AC`, Tabella 8 e 10) e avete usato delle espressioni regolari per contare le modifiche a **selettori** e **asserzioni** (Tabella 11 e 12), individuando già i test con `0 modifiche`. Posso usare direttamente i dati e gli script dell'appendice di `J8` (`https://zenodo.org/records/15882798`) per selezionare i test "non cambiati" da eseguire?
5. **Riuso di `E2EGitExtended.db` e delle migrazioni di `C16` ([Zenodo 19741349](https://doi.org/10.5281/zenodo.19741349))**:
   - Nel paper **`C16`** (*Exploring the Socio-Technical Motivations Behind the Adoption and Migration of Web GUI Testing Frameworks*, SEAA 2026) avete pubblicato su Zenodo (`https://doi.org/10.5281/zenodo.19741349`, repo `squidslab/wgt-shift`) il database esteso **`E2EGitExtended.db`** e avete mappato i **97 repository (su 472)** che hanno cambiato framework (156 eventi di migrazione, principalmente da Cypress/Puppeteer verso Playwright). Mi conviene usare `E2EGitExtended.db` come base invece del solo `E2EGit.db` (`v3`, Zenodo `14234731`), così da sapere già quali repository hanno migrato framework e quali hanno mantenuto lo stesso?

---

## 2. Il dilemma del Commit: Snapshot del DB (`t₀`) vs Ultimo Commit (`HEAD` / `t₁`)
Nel database (`repos_commit.csv`), la colonna `last_commit_sha` fotografa i repository a **marzo 2024** (`t₀`). Da una prima verifica storica fatta con Git su un piccolo campione di repository (es. `10up/elasticpress`, `Agenta-AI/agenta`), è emerso che tra marzo 2024 e oggi **circa due terzi dei file di test elencati in `tests_gui.csv` sono stati cancellati, spostati o sostituiti da altri framework** (es. da Cypress a Playwright).

6. **Su quale commit dobbiamo eseguire i test?**
   - **Opzione A — Esecuzione su `last_commit_sha` (`t₀`, marzo 2024)**: Garantisce che i file elencati in `tests_gui.csv` (`test_path_rel`) esistano tutti esattamente come descritti nel paper, ma le dipendenze e i container sono vecchi di oltre due anni.
   - **Opzione B — Esecuzione sull'ultimo commit attuale (`HEAD` / `t₁`)**: Testa lo stato attuale del progetto e verifica se i test "reggono ancora oggi", ma richiede prima di filtrare i test cancellati o seguire i file rinominati (`git log --follow`).
   - **Opzione C — Approccio doppio (Storia Git da `t₀` a `HEAD` + Esecuzione)**: Usiamo la storia Git leggera (`git clone --filter=blob:none`) su tutti i 472 repository da `last_commit_sha` a `HEAD` per misurare quanti test sono spariti, rimasti congelati o modificati, ed eseguiamo i test (a `t₀`, a `HEAD`, o ad entrambi i punti) sui repository in cui i test sono sopravvissuti. **Quale di queste opzioni risponde meglio alla sua idea di ricerca?**
7. **Significato esatto di *"verificare perché non sono cambiati"* (collegamento con `J8` pag. 26–27 e pag. 35–36)**:
   - In **`J8`** avete osservato un *"initial burst of activity in creating web GUI test files, followed by little or no long-term maintenance"* (con una mediana di `SV_Mod = 3` modifiche in `673` giorni e `1.182` commit dell'app), chiedendovi se i test non modificati siano **stabili ("reggono")** o **abbandonati ("rotti/neglected")**. L'obiettivo del mio tirocinio è proprio fare quella **validazione dinamica (esecuzione a runtime)** citata nelle conclusioni di `J8` (pag. 35–38) per distinguere i test fermi che passano ancora da quelli rotti/obsoleti?

---

## 3. Perimetro dei Repository e Stratificazione del Campione
Il dataset contiene **472 repository GUI** (distribuite secondo `J8` e `C16` in: **197 Playwright**, **187 Cypress**, **87 Selenium**, **20 Puppeteer**; linguaggi: **283 TypeScript**, **130 JavaScript**, **72 Java**, **10 Python**) e **84 repository di performance** (410 ThreadGroup/TaskSet in JMeter/Locust), con 13 repository in comune.

8. **Focus solo su GUI testing o anche Performance?**: Poiché i test di performance (JMeter/Locust) sono già stati oggetto di *C5* (ICSME 2025) e *PT-LINTR* (*C14*, ICSME 2026), il mio lavoro deve concentrarsi **esclusivamente sui test E2E GUI** (proseguendo il filone di `J8` e `C16`) o deve includere anche la parte di performance?
9. **Dimensione del campione e soglia di eseguibilità (Gate GO/NO-GO)**: L'obiettivo di eseguire un campione (es. 100 repository) è un requisito rigido o un target iniziale? Come evidenziato anche nelle *Threats to Validity* di `J8` (pag. 36, *"low success rate in compiling past snapshots and the high cost of environment reconstruction"*), se da un test pilota su 10–15 repository emergesse che l'eseguibilità reale è bassa (es. < 40–50%), è preferibile **ridurre il numero di repository ma analizzarli in profondità**, oppure **sostituire i repo che non partono** pescando da una lista di riserva?
10. **Criteri di selezione dei repository (Escludere o includere i 97 repo migrati di `C16`?)**:
    - In `J8` (Fig. 3, pag. 13) e `C16` (pag. 6) mostrate che **375 repository su 472 hanno mantenuto un solo framework** per tutta la loro storia (78 Selenium, 146 Cypress, 133 Playwright, 18 Puppeteer), mentre **97 repository (21%) hanno cambiato framework**. Per il nostro studio sull'esecuzione, conviene selezionare il campione **solo tra i 375 repository "stabili" (che non hanno cambiato framework)** o includere anche quelli migrati?

---

## 4. Infrastruttura, Ambiente di Esecuzione e "Time-box"
Eseguire test E2E GUI richiede un browser (headless), il build dell'applicazione web e spesso servizi accessori (DB, cache), oltre a circa 150–250 GB di spazio disco.

11. **Macchina da laboratorio / Server**: Il laboratorio mette a disposizione una macchina server o una VM (con Docker e spazio disco adeguato) dove poter lanciare i batch di esecuzione anche di notte, oppure devo organizzarmi in locale sul mio PC per l'esecuzione e usare il cloud solo per le analisi dati?
12. **Regola del Time-box sui progetti complessi**: Molti progetti web reali falliscono in fase di setup perché richiedono configurazioni manuali o servizi esterni non documentati. È d'accordo se fissiamo una regola di **time-box rigido** (es. massimo 45–60 minuti di tentativi di setup per repository), superato il quale il repository viene classificato come `setup_failed` (documentando la causa tecnica del blocco) e si passa al successivo?

---

## 5. Tassonomia dei Risultati, Flakiness e Metodologia Scientifica
Per trasformare l'esecuzione dei test in un lavoro solido (ed eventualmente pubblicabile):

13. **Tassonomia dei fallimenti e collegamento con `J8` e `C16`**:
    - In **`J8`** (Tabella 6, pag. 21–22) avete dimostrato che il **72% delle issue aperte automaticamente dalla CI** sui test GUI riguarda **Flakiness o Lentezza** (`flaky-e2e`, `slow-e2e`) e che oltre il 40–53% viene chiuso per inattività (ignorato dagli sviluppatori); e in **`C16`** (Tabella 1 e Fig. 2, pag. 9–10) mostrate che **Reliability & Stability (`M5`, 20.5%)** e **Manutenibilità (`M7`, 15.4%)** sono le prime cause di abbandono/migrazione (*Priority Inversion*).
    - Posso usare queste evidenze di `J8` e `C16` per strutturare la nostra tassonomia degli esiti (distinguendo tra: *test di facciata/generico*, *test obsoleto per mancato aggiornamento di selettori/asserzioni*, *regressione genuina*, *test flaky*, *test disabilitato con `.skip`/`@Ignore`*)?
14. **Gestione della Flakiness a runtime**: Per distinguere un test realmente rotto/obsoleto da un test *flaky* (instabile), quante volte conviene rieseguire le suite che presentano fallimenti (es. 3 ripetizioni, come nel caso di `pinterest/gestalt` citato in `C16` a pag. 11)?
15. **Validazione manuale (Doppia codifica)**: Per la classificazione qualitativa dei casi studio ("perché il test non è cambiato / perché si è rotto"), prevede che facciamo una doppia annotazione indipendente (con calcolo del *Cohen's kappa*) insieme a un dottorando o collega del gruppo (come fatto in `J8` e `C16`)?

---

## 6. Eventuale domanda sul Prog1 (Solo se devi ancora confermare la scelta tra Prog1 e Prog2)
*(Se hai già scelto Prog2 salta questa sezione; se invece il ricevimento serve anche a decidere tra i due progetti presenti in `ProgTirocinio.txt`, puoi aggiungere queste due domande)*:

16. **Confronto operativo tra Prog1 (`GitSkills` / MSR 2027) e Prog2 (`E2EGit`)**: Nel `ProgTirocinio.txt` per il Prog1 è indicato *"parallelo"* con la MSR 2027 Mining Challenge. La scadenza della challenge o gli obiettivi del gruppo rendono uno dei due progetti più urgente o più adatto a una tesi/pubblicazione nei prossimi mesi?
17. **Definizione degli "smell" in Prog1**: Nel caso del Prog1 sui file `SKILL.md`, avete già una lista di metriche o *bad practice* da rilevare, oppure la definizione stessa della tassonomia di smell farebbe parte del tirocinio?

---

## 🗺️ Diagramma della Metodologia Proposta (da mostrare o discutere col Professore)

![Diagramma della Metodologia Prog2 E2EGit](./diagramma_metodologia.svg)


---

## 7. Organizzazione, Scadenze e Ricevimenti
18. **Cadenza degli aggiornamenti**: Le va bene se le invio un breve resoconto settimanale via email (con i numeri di avanzamento, eventuali blocchi e una domanda puntuale) prima del ricevimento settimanale/bisettimanale?
19. **Primo obiettivo per la prossima settimana**: Per il prossimo incontro, oltre a recuperare gli eventuali artefatti del lavoro precedente e i replication package di `J8` (`zenodo.15882798`) e `C16` (`zenodo.19741349`), preferisce che le porti **l'analisi della storia Git dei test rimasti invariati** oppure un **primo test pilota di esecuzione Docker su 5–10 repository**?

---

## 📚 Tabella di Riferimento Rapido dei Paper e Dataset del Gruppo (da avere sotto mano)

| Sigla Paper | Titolo e Venue | Link PDF / Dataset Zenodo | Cosa contiene di utile per il tuo progetto |
|---|---|---|---|
| **`C4`** | *E2EGit: A Dataset of End-to-End Web Tests in Open Source Projects* (MSR 2025) | • [PDF locale](./02-E2EGit-TestE2E/docs/letteratura/E2EGit_MSR2025_C4.pdf)<br>• [Zenodo 14234731](https://zenodo.org/records/14234731) (`v3` / `v5` `14988988`) | Il database base **`E2EGit.db`** con i **472 repo GUI** (8.601 file, 43.670 test), gli **84 repo Performance** (410 ThreadGroup) e `last_commit_sha` (marzo 2024). |
| **`J8`** | *Investigating the Adoption and Maintenance of Web GUI Testing: Insights from GitHub Repositories* (IST 2025/2026) | • [PDF locale](./02-E2EGit-TestE2E/docs/letteratura/WebGUITesting_Maintenance_IST2025_J8.pdf)<br>• [Zenodo 15882798](https://zenodo.org/records/15882798) | **Origine del tuo tirocinio**: dimostra che i test GUI cambiano pochissimo (mediana `SV_Mod = 3` modifiche in `673` giorni e `1.182` commit dell'app), analizza le modifiche a selettori/asserzioni e mostra che il 72% delle issue CI aperte riguarda flakiness/lentezza. Chiede nelle conclusioni (pag. 35–38) un'analisi dinamica (esecuzione a runtime) per capire se i test fermi sono stabili o abbandonati. |
| **`C16`** | *Exploring the Socio-Technical Motivations Behind the Adoption and Migration of Web GUI Testing Frameworks* (SEAA 2026) | • [PDF locale](./02-E2EGit-TestE2E/docs/letteratura/WebGUITesting_Migration_C16.pdf)<br>• [Zenodo 19741349](https://doi.org/10.5281/zenodo.19741349) (`squidslab/wgt-shift`) | Fornisce il database esteso **`E2EGitExtended.db`**, mappa i **97 repo su 472 (21%) che hanno migrato framework** (156 migrazioni, soprattutto verso Playwright) vs i **375 repo rimasti sullo stesso framework**, e introduce le 8 motivazioni (`M1–M8`) e la *Priority Inversion* (si adotta per facilità d'uso `M3`, si abbandona/migra per Flakiness `M5` e Manutenibilità `M7`). |
| **`C5`** | *Performance Testing in Open-Source Web Projects: Adoption, Maintenance, and a Change Taxonomy* (ICSME 2025) | • [PDF locale](./02-E2EGit-TestE2E/docs/letteratura/PerformanceTesting_Maintenance_ICSME2025_C5.pdf) | Studio gemello di `J8` ma sugli 84 repository di performance (JMeter/Locust), con una tassonomia dei cambiamenti ai test. |


