# Appunti Ricevimenti — Tirocinio

Raccolta ordinata delle indicazioni ricevute dal professore durante i vari ricevimenti (accorpata da `ricevimento_1.txt`, `ricevimento_2.txt` e `ricevimento_3.txt`).

---

## Ricevimento 1 — Scelta e definizione dei possibili progetti

> Fonte: [ricevimento_1.txt](./ricevimento_1.txt)

Il professore ha presentato due possibili tracce di progetto:

### Opzione 1 — Nuovo progetto (`Prog1 NUOVO`)
- **Tema:** Realizzazione di un tool per l'analisi di repository legati a *skill AI* (`pydrillerdataset`, `gitskill`).
- **Cosa analizzare:** L'andamento del progetto nel tempo — commit, commenti alle commit, errori, code smells, ecc. (in parallelo).
- **Dataset di riferimento:**
  - [MSR 2027 Mining Challenge](https://2027.msrconf.org/track/msr-2027-mining-challenge)

### Opzione 2 — Prosecuzione di un progetto già avviato (`Prog2 CONTINUO DI UNO GIA' AVVIATO`)
- **Tema:** Analisi di test *end-to-end* (E2E).
- **Obiettivo:** Eseguire i test e verificare perché non sono cambiati nel tempo, valutando se reggono ancora o se si sono rotti.
- **Materiale e riferimenti:**
  - Articolo IEEE: <https://ieeexplore.ieee.org/document/11025750>
  - Dataset / record Zenodo: <https://zenodo.org/records/14234731>
  - PDF conferenza: <https://valeriapontillo.github.io/documents/conference/C4.pdf>

---

## Ricevimento 2 — Indicazioni operative sul progetto E2E

> Fonte: [ricevimento_2.txt](./ricevimento_2.txt)

- **Titolo ufficiale del progetto:** *Implementazione di un tool per l'analisi automatica di test e2e web in repository software*
- **Prossimo appuntamento:** Martedì 3

### Cosa ha richiesto il professore
1. **Selezione e scrematura iniziale (dai 472 progetti):**
   - Individuare i progetti Node con il maggior numero di test.
   - Guardare il numero di commit e identificare i test che cambiano più spesso (con tanti commit).
   - Iniziare a stilare una lista iniziale a partire dai 472 repository.
2. **Analisi del ciclo di vita dei test:**
   - Tracciare quando nasce un test e quante versioni dell'applicazione intercorrono tra la creazione/modifica di un test e la sua modifica successiva.
   - Se un test non funziona più, capire a partire da quale versione dell'applicazione smette di funzionare e se viene corretto nella versione successiva.
3. **Esecuzione riproducibile con Docker *(da valutare)*:**
   - Usare container (`Dockerfile`) e script per eseguire i test su una determinata versione.
   - *Nota:* da valutare se includerlo, perché potrebbe risultare troppo difficile.
4. **Primo test pratico:**
   - Iniziare con un paio di programmi campione, testarli e raccogliere i primi dati.

---

## Ricevimento 3

> Fonte: [ricevimento_3.txt](./ricevimento_3.txt)

> [!NOTE]
> Il file `ricevimento_3.txt` contiene attualmente una copia identica di `ricevimento_1.txt` (probabilmente copiata per errore). Se hai altri appunti per il terzo ricevimento, puoi aggiungerli qui sotto.

- *(Da completare con le note effettive del terzo ricevimento)*
