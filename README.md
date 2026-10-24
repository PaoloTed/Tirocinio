# Tirocinio — Indice

Due proposte di tirocinio, una cartella ciascuna. La scelta va fatta **prima** del ricevimento di martedì 27 ottobre 2026.

| Cartella | Progetto | Guida | Orizzonte |
|---|---|---|---|
| [`01-AgentSkills-Mining/`](01-AgentSkills-Mining/) | Tool di analisi per Agent Skills (GitSkills · MSR 2027) | [Guida-Prog1-AgentSkills.md](01-AgentSkills-Mining/Guida-Prog1-AgentSkills.md) | 16 settimane, 26/10/2026 → 12/02/2027 |
| [`02-E2EGit-TestE2E/`](02-E2EGit-TestE2E/) | Esecuzione e manutenzione di test E2E (E2EGit, 100 repository) | [Guida-Prog2-E2EGit.md](02-E2EGit-TestE2E/Guida-Prog2-E2EGit.md) | 20 settimane, 26/10/2026 → 12/03/2027 |

I nomi delle cartelle dicono il contenuto, il prefisso numerico tiene l'ordine delle due proposte. Nei testi e nelle email i progetti restano "Prog1" e "Prog2", come li chiama il professore.

## Documenti condivisi (restano qui)

- [`ProgTirocinio.txt`](ProgTirocinio.txt) — la traccia originale del professore.
- [`analisitirociniomd.md`](analisitirociniomd.md) — l'analisi comparativa completa dei due progetti.

Sono alla radice perché riguardano entrambi i progetti: se li sposti in una delle due cartelle, perdi il confronto.

## Struttura di ogni cartella

```text
01-AgentSkills-Mining/
├─ Guida-Prog1-AgentSkills.md    piano di lavoro + calendario dei martedì
├─ docs/
│  ├─ letteratura/               paper già scaricati (PDF) + figure estratte
│  └─ verbali/                   un file per ogni ricevimento
├─ data/                         dataset (escluso da Git, pesante)
├─ src/                          codice
└─ results/                      output di analisi
```

La struttura di `02-E2EGit-TestE2E/` è identica, con `E2EGit.db` (2,27 GB) in `data/`.

## Cosa fare adesso

1. Leggi il §0 di entrambe le guide (2 minuti ciascuna).
2. Apri il §3 della guida che ti convince di più e leggi il paper già scaricato in `docs/letteratura/`. Nel progetto 02 c'è anche la traduzione italiana del paper E2EGit.
3. Prepara le domande del §13 (Prog2) o §11 (Prog1) per martedì 27/10.

## Nota sulle date

Le scadenze sono reali e verificate il 23/10/2026 sulle fonti ufficiali:

- **MSR 2027 Mining Challenge** (solo Prog1): abstract **18/12/2026**, paper **23/12/2026**, conferenza a Dublino 26–27/04/2027.
- **Prog2**: nessuna deadline esterna. Il rischio è opposto: senza scadenze intermedie il progetto slitta. I gate sono nelle settimane 4, 7 e 13.
