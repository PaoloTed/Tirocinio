# Guida Rapida: Comandi Docker e Gestione Spazio

Questa guida riassume i comandi da terminale per:
1. **Eseguire i test multi-versione**
2. **Monitorare lo spazio occupato su disco** da Docker e dai file temporanei
3. **Ripulire selettivamente o totalmente lo spazio**

---

## 1. Come Far Partire i Test E2E

### Esecuzione multi-versione in parallelo (con schede terminale e log salvati):
Posizionati nella root del progetto o usa il percorso assoluto:

```bash
# Esempio su blocco v5.4.0 - v6.2.0
bash /home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid/docker/esegui_test_docker.sh v5.4.0 v5.4.1 v5.5.0 v5.5.1 v5.6.0 v5.6.1 v5.6.3 v5.6.4 v6.0.0 v6.0.1 v6.1.0 v6.2.0
```

### Esecuzione su una singola versione specifica:
```bash
bash /home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid/docker/esegui_test_docker.sh v5.4.0
```

*I log di esecuzione vengono salvati automaticamente in:*  
`repositories/angular-slickgrid/results/logs/test_<versione>.txt`

---

## 2. Come Vedere Quanto Spazio Occupano i Container e le Immagini

### Riepilogo rapido dello spazio usato da Docker:
```bash
docker system df
```
Mostra una tabella riassuntiva di:
- **Images**: spazio occupato dalle immagini Docker (e quanto è riutilizzabile).
- **Containers**: spazio occupato dai container (layer scrivibili).
- **Local Volumes**: spazio occupato da volumi persistenti.
- **Build Cache**: spazio occupato dalla cache di build di BuildKit.

### Dettaglio approfondito (singole immagini e singoli container con dimensioni):
```bash
docker system df -v
```

### Lista di tutte le immagini con dimensione:
```bash
docker images
```
Per filtrare solo le immagini di questo progetto:
```bash
docker images 'slickgrid-e2e*'
```

### Lista dei container (anche terminati) con dimensione su disco:
```bash
docker ps -a --size
```

### Verificare lo spazio temporaneo dei worktree in `/tmp`:
```bash
du -sh /tmp/slickgrid-wt-* 2>/dev/null || echo "Nessun worktree presente in /tmp"
```

---

## 3. Come Ripulire lo Spazio su Disco

Scegli il livello di pulizia in base a cosa vuoi liberare:

### Livello 1: Pulizia normale post-test (Consigliata dopo ogni sessione)
Rimuove i container terminati, le cartelle temporanee in `/tmp` e la cache di build temporanea:
```bash
# 1. Rimuove container terminati
docker container prune -f

# 2. Pulisce i file temporanei dei git worktree in /tmp
rm -rf /tmp/slickgrid-wt-*
git -C /home/paolo/Scrivania/Universita/Tirocinio/02-E2EGit-TestE2E/repositories/angular-slickgrid/repo worktree prune

# 3. Pulisce immagini "dangling" (layer orfani senza tag)
docker image prune -f
```

---

### Livello 2: Eliminare solo le immagini generate dei test (Senza toccare le immagini base di sistema)
Se vuoi cancellare solo le immagini create per le versioni testate (`slickgrid-e2e:*`), mantenendo l'immagine di base Node/Cypress per non doverla riscaricare:
```bash
docker rmi $(docker images 'slickgrid-e2e*' -q)
```

---

### Livello 3: Pulizia della cache del builder di Docker
Se Docker accumula giga di cache di build:
```bash
docker builder prune -f
```
Per forzare la rimozione di tutta la build cache (anche quella non orfana):
```bash
docker builder prune -a -f
```

---

### Livello 4: Pulizia Totale ("Reset Completo" di Docker)
> [!WARNING]
> Questo comando rimuove **tutti** i container fermi, tutte le reti non usate, tutte le immagini non usate e tutta la build cache, liberando tutti i Gigabyte occupati da Docker.

```bash
docker system prune -a --volumes -f
```

