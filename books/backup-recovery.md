     1|# Backup & Recovery
     2|> Slug: backup-recovery
     3|
     4|---
     5|
     6|## Contents
     7|
     8|- Backup Architecture
     9|- Recovery Runbooks
    10|- Verifying Backup Health
    11|
    12|---
    13|
    14|### Backup Architecture
    15|
    16|Arda has a centralized backup system. **palantir** (a Debian machine on VLAN99) orchestrates all backups daily at 3 AM CDT and pushes everything to **Moria** (the Synology NAS on VLAN10).
    17|
    18|#### Why This Design
    19|
    20|- **palantir** can reach every machine on both VLANs — MikroTik and Zyxel on VLAN99, Rivendell and Moria on VLAN10
    21|- **Moria** has SHR RAID (survives single disk failure) and 5.7 TB free — it's the safest place to store data
    22|- Each machine also keeps local copies on palantir's disk (208 GB free, 30-day retention) as a second layer
    23|- A USB disk on Moria gets the most critical essentials for catastrophic scenarios
    24|
    25|#### The Data Flow
    26|
    27|```
    28|palantir (orchestrator, 192.168.99.21)
    29|  |
    30|  +-- SSH over VLAN99 --> MikroTik (192.168.99.1)
    31|  |     export config -> .rsc
    32|  |     local archive (30d) + rsync -> Moria
    33|  |
    34|  +-- HTTP over VLAN99 --> Zyxel (192.168.99.2)
    35|  |     download config -> .cfg
    36|  |     local archive (30d) + rsync -> Moria
    37|  |
    38|  +-- SSH over VLAN10 --> Rivendell (192.168.10.4)
    39|  |     docker exec mysqldump -> BookStack.sql.gz
    40|  |     rsync /mnt/work/ -> tar.gz (excludes .git, ollama, grafana plugins, unifi logs)
    41|  |     rsync unifi autobackup dir
    42|  |     local archive (30d) + rsync -> Moria
    43|  |
    44|  +-- tar /home/aule/ -> palantir backup
    45|  |     local archive (30d) + rsync -> Moria
    46|  |
    47|  +-- USB disk (/usbshare1/) if mounted
    48|        copy latest essentials
    49|```
    50|
    51|#### What Gets Backed Up and What Doesnt
    52|
    53|| Component | Backup Method | Size on Moria | Restore Method |
    54||-----------|--------------|---------------|----------------|
    55|| **Rivendell configs** | rsync all compose stacks + .env + configs -> tar.gz | ~960 MB | Extract, docker compose up -d |
    56|| **BookStack DB** | docker exec mysqldump | ~2.7 MB | mysql import |
    57|| **MikroTik config** | SSH /export -> .rsc | ~16 KB | /file import on MikroTik |
    58|| **Zyxel config** | manual via web UI -> .cfg | ~4 KB | Upload via web UI |
    59|| **UniFi backups** | rsync autobackup .unf files | ~15 MB | Restore via UniFi controller |
    60|| **Palantir home dir** | surgical tar (scripts, .ssh, configs) | varies | Extract on new machine |
    61|
    62|**NOT backed up (by design):**
    63|- Ollama models (~21 GB) -- just re-download with `ollama pull`
    64|- Docker container images -- `docker compose up -d` pulls fresh
    65|- Prometheus metrics history -- low value
    66|- Whisper/voice model files -- rebuild from Dockerfile
    67|
    68|#### Where Everything Lives on Moria
    69|
    70|```
    71|/volume1/backups/
    72|+-- network/
    73||   +-- mikrotik/mikrotik-YYYYMMDD.rsc
    74||   +-- zyxel/zyxel-YYYYMMDD.cfg
    75||   +-- unifi/autobackup/autobackup_*.unf
    76|+-- servers/
    77|    +-- rivendell/
    78|    |   +-- rivendell-configs-YYYYMMDD.tar.gz
    79|    |   +-- rivendell-bookstack-db-YYYYMMDD.sql.gz
    80|    +-- palantir/
    81|        +-- palantir-YYYYMMDD.tar.gz
    82|```
    83|
    84|Each run writes dated files with YYYYMMDD suffix. Moria keeps everything indefinitely. palantir prunes local copies over 30 days old.
    85|
    86|#### The Master Script
    87|
    88|A single script on palantir runs everything:
    89|
    90|**Location:** `/home/aule/scripts/backup-arda.sh`
    91|
    92|**Execution order:**
    93|1. Check Moria is reachable (aborts remote push if not, continues locally)
    94|2. Export MikroTik config to local + Moria
    95|3. Zyxel config: copy latest manually-backed-up .cfg -> Moria (no automated API on GS1900-24HP)
    96|4. Dump BookStack DB from Rivendell to local + Moria
    97|5. Rsync Rivendell /mnt/work/ -> tar.gz -> local + Moria
    98|6. Sync UniFi autobackups -> local + Moria
    99|7. Archive palantir home (surgical: scripts, .ssh, configs ONLY -- excludes backups/, caches, empty dirs) -> local + Moria
   100|8. Copy latest essentials to USB disk (if mounted)
   101|9. Prune local archives > 30 days old
   102|
   103|**Scheduled via crontab on palantir:**
   104|```
   105|0 3 * * * bash /home/aule/scripts/backup-arda.sh
   106|```
   107|
   108|**Version control:** Git repo at `/mnt/work/backups/scripts/` on Rivendell.
   109|
   110|#### Daily Health Check
   111|
   112|Every morning at 8AM CDT, Aule sends a backup health report to the Telegram Home channel and Discord #general. It looks like:
   113|
   114|All MikroTik configs on Moria
   115|All BookStack DB dumps on Moria
   116|All Rivendell configs on Moria (963 MB)
   117|All Palantir home on Moria
   118|
   119|Status: ALL GOOD
   120|
   121|If anything failed, the message says ISSUES FOUND and highlights what to check.
   122|
   123|#### Retention & Pruning
   124|
   125|- palantir (local): 30 days -- older archives auto-deleted
   126|- Moria: indefinite -- 5.7 TB free, disk management via DSM
   127|- USB: latest essential files only, no history
   128|
   129|---
   130|
   131|### Recovery Runbooks
   132|
   133|#### Rivendell SSD Dies (Full Rebuild)
   134|
   135|Worst case: Rivendells SSD is dead and needs a fresh Debian install. This restores every service.
   136|
   137|**Prerequisites:** Access to Moria's /volume1/backups/ either via SSH from palantir or the Synology web UI.
   138|
   139|**Steps:**
   140|
   141|1. Install Debian 12 on the new SSD with Docker
   142|
   143|   ```
   144|   apt update && apt install -y docker.io docker-compose-v2 git
   145|   ```
   146|
   147|2. Get the latest backup files from Moria
   148|
   149|   ```
   150|   # From the new machine or from palantir
   151|   scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-configs-latest.tar.gz .
   152|   scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-bookstack-db-latest.sql.gz .
   153|   ```
   154|
   155|3. Extract configs into place
   156|
   157|   ```
   158|   mkdir -p /mnt/work
   159|   tar -xzf rivendell-configs-latest.tar.gz -C /mnt/work/
   160|   ```
   161|
   162|4. Start each Docker stack
   163|
   164|   ```
   165|   cd /mnt/work/ai-stack && docker compose up -d
   166|   cd /mnt/work/network-stack && docker compose up -d
   167|   # Repeat for any other stacks under /mnt/work/
   168|   ```
   169|
   170|5. Restore BookStack database
   171|
   172|   ```
   173|   gunzip < rivendell-bookstack-db-latest.sql.gz | docker exec -i bookstack_db mysql -u root -p"$DB_PASSWORD" bookstackapp
   174|   ```
   175|
   176|6. Restore UniFi via its controller UI at https://newip:8443
   177|   - System Settings -> Backup -> Restore
   178|   - Pick the .unf file from /volume1/backups/network/unifi/autobackup/
   179|
   180|7. Re-establish the backup chain from palantir
   181|
   182|   ```
   183|   ssh aule@192.168.99.21
   184|   ssh-copy-id -i ~/.ssh/id_rivendell aule@192.168.10.4
   185|   ssh aule@192.168.10.4 "echo ok" # verify
   186|   ```
   187|
   188|#### palantir Dies (Debian Rebuild)
   189|
   190|Whats lost: the backup scripts (in git), SSH keys to MikroTik/Moria/Rivendell, the crontab, and local 30-day archive cache (Moria still has the long-term copies).
   191|
   192|**Steps:**
   193|
   194|1. Install Debian + XFCE on the new palantir
   195|2. Grab scripts from the git repo on Rivendell
   196|
   197|   ```
   198|   # From palantir, if SSH to Rivendell is possible (use password if needed)
   199|   scp -r aule@192.168.10.4:/mnt/work/backups/scripts /home/aule/
   200|   ```
   201|   Or read each file individually:
   202|   ```
   203|   ssh aule@192.168.10.4 "cat /mnt/work/backups/scripts/backup-arda.sh" > /home/aule/scripts/backup-arda.sh
   204|   # Repeat for backup-mikrotik.sh, backup-rivendell.sh, backup-palantir.sh
   205|   chmod +x /home/aule/scripts/*.sh
   206|   ```
   207|
   208|3. Regenerate SSH keys. The authorized keys on each target machine need to be updated:
   209|
   210|   ```
   211|   ssh-keygen -t ed25519 -f ~/.ssh/id_moria
   212|   ssh-keygen -t ed25519 -f ~/.ssh/id_mikrotik
   213|   ssh-keygen -t ed25519 -f ~/.ssh/id_rivendell
   214|   ```
   215|
   216|   **MikroTik** - add the new key:
   217|   ```
   218|   ssh-copy-id -i ~/.ssh/id_mikrotik admin@192.168.99.1
   219|   ```
   220|
   221|   **Rivendell** - add the new key:
   222|   ```
   223|   ssh-copy-id -i ~/.ssh/id_rivendell aule@192.168.10.4
   224|   ```
   225|
   226|   **Moria** - Synology DSM, no ssh-copy-id. Use the web UI:
   227|   - Go to Control Panel > File Services > SSH keys
   228|   - Or paste into `/volume1/homes/aule/.ssh/authorized_keys` via File Station
   229|
   230|4. Set up SSH config
   231|
   232|   ```
   233|   cat > ~/.ssh/config << 'EOF'
   234|   Host mikrotik
   235|       HostName 192.168.99.1
   236|       User admin
   237|       IdentityFile ~/.ssh/id_mikrotik
   238|   Host moria
   239|       HostName 192.168.10.6
   240|       User aule
   241|       IdentityFile ~/.ssh/id_moria
   242|   Host rivendell
   243|       HostName 192.168.10.4
   244|       User aule
   245|       IdentityFile ~/.ssh/id_rivendell
   246|   EOF
   247|   ```
   248|
   249|5. Set up crontab
   250|
   251|   ```
   252|   crontab -e
   253|   # add: 0 3 * * * bash /home/aule/scripts/backup-arda.sh
   254|   ```
   255|
   256|6. Re-authorize Aules (Hermes) health check access
   257|
   258|   ```
   259|   # From Rivendell:
   260|   ssh-copy-id -i /opt/data/.ssh/id_ed25519_hermes aule@192.168.99.21
   261|   ```
   262|
   263|#### Moria Dies (NAS Failure)
   264|
   265|This is the worst single point of failure. Mitigations:
   266|
   267|- palantir retains the last 30 days of archives on local disk
   268|- The USB essentials disk has the latest configs and DB dumps
   269|- The backup script detects Moria unreachable and continues locally (harmlessly failing the rsync step)
   270|
   271|If Moria dies:
   272|1. Fix or replace the NAS hardware first
   273|2. Re-restore from palantir local archives once Moria is back
   274|3. Run a manual backup to repopulate: `bash /home/aule/scripts/backup-arda.sh`
   275|
   276|#### MikroTik Dies (Full Hardware Replacement)
   277|
   278|1. Get latest config from Moria or palantir:
   279|
   280|   ```
   281|   # From palantir:
   282|   scp moria:/volume1/backups/network/mikrotik/mikrotik-20260522.rsc .
   283|   # Or local copy:
   284|   cp /home/aule/backups/mikrotik/latest/mikrotik-latest.rsc .
   285|   ```
   286|
   287|2. Upload to new MikroTik:
   288|
   289|   ```
   290|   scp mikrotik-latest.rsc admin@192.168.88.1:/
   291|   ```
   292|
   293|3. On the MikroTik:
   294|
   295|   ```
   296|   /file import mikrotik-latest.rsc
   297|   ```
   298|
   299|#### BookStack Data Loss (Accidental Delete)
   300|
   301|Restore just the database:
   302|
   303|```
   304|# On Rivendell:
   305|scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-bookstack-db-20260522.sql.gz /tmp/
   306|gunzip < /tmp/rivendell-bookstack-db-20260522.sql.gz | docker exec -i bookstack_db mysql -u root -p"$DB_PASSWORD" bookstackapp
   307|```
   308|
   309|---
   310|
   311|### Verifying Backup Health
   312|
   313|#### Quick Check
   314|
   315|If youre in the Telegram or Discord home channel, wait for the daily 8AM CDT backup report from Aule. If nothing appears by 8:15 AM, something may be wrong -- ask Dan.
   316|
   317|#### Check via SSH to palantir
   318|
   319|**Is the latest backup log clean?**
   320|
   321|```
   322|ssh aule@192.168.99.21
   323|cat /home/aule/logs/backup/backup-arda-$(date +%Y%m%d).log | grep -E "Duration|COMPLETE|FAILED|WARNING"
   324|```
   325|
   326|Expected: Duration < 10 minutes, "COMPLETE" at end, no FAILED entries.
   327|
   328|**Is data on Moria?**
   329|
   330|```
   331|ssh -i ~/.ssh/id_moria aule@192.168.10.6 \
   332|  "find /volume1/backups/ -name \"*$(date +%Y%m%d)*\" -type f"
   333|```
   334|
   335|You should see files from today in every backup category.
   336|
   337|**Disk space check:**
   338|
   339|```
   340|df -h /home/aule          # palantir local -- should have >60% free
   341|ssh moria "df -h /volume1" # Moria -- 5.7 TB total
   342|```
   343|
   344|#### Check via Aule
   345|
   346|Ask me directly:
   347|- "Aule, check the backup health"
   348|- "Aule, did the backup run last night?"
   349|
   350|I will SSH through the chain and report full status.
   351|
   352|#### Failure Symptoms Quick Reference
   353|
   354|| Log Entry | Likely Cause | Fix |
   355||-----------|-------------|-----|
   356|| MikroTik export FAILED | MikroTik down or SSH key expired | Check MikroTik, re-auth SSH key |
   357|| Zyxel download FAILED | HTTP endpoint changed | Non-critical -- switch works without backup |
   358|| BookStack DB dump FAILED | BookStack container not running | Run `docker restart bookstack_db` on Rivendell |
   359|| Moria push FAILED | NAS unreachable or SSH broken | Check Moria, re-auth id_moria key |
   360|| USB disk not found | USB not mounted at /usbshare1/ | Plug in USB or ignore |
   361|| Rivendell unreachable | Host down or SSH broken | Fix Rivendell first |
   362|| Palantir archive FAILED | Disk full | `df -h /home/aule`, free space |
   363|
   364|---
   365|