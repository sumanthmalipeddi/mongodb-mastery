# Backup & Monitoring

---

## Backup Strategies

### 1. mongodump / mongorestore (Self-Managed)

```bash
# Full backup
mongodump --uri="mongodb://admin:pass@localhost:27017" --out=/backup/2025-01-15

# Backup a specific database
mongodump --uri="..." --db=myapp --out=/backup/myapp

# Restore
mongorestore --uri="..." /backup/2025-01-15

# Restore a specific database
mongorestore --uri="..." --db=myapp /backup/myapp/myapp
```

⚠️ `mongodump` creates a logical backup. For large databases, filesystem snapshots are faster.

### 2. Filesystem Snapshots

```bash
# Lock writes, take snapshot, unlock
mongosh --eval "db.fsyncLock()"
# Take LVM/EBS/disk snapshot
mongosh --eval "db.fsyncUnlock()"
```

✅ Fast for large databases
⚠️ Requires consistent snapshot of data files AND journal

### 3. Atlas Continuous Backup

Atlas provides automated backups:

| Tier | Backup Type |
|------|-------------|
| M0 (Free) | No backups |
| M2/M5 | Daily snapshots |
| M10+ | Continuous backup with point-in-time recovery |

**Point-in-time recovery** lets you restore to any second within the retention window (typically 1-7 days).

### Backup Best Practices

- Test restores regularly — a backup you can't restore is worthless
- Store backups in a different region/account
- Encrypt backup data
- Automate backup verification

---

## Monitoring

### Key Metrics to Watch

| Metric | What It Tells You | Warning Sign |
|--------|-------------------|--------------|
| **Connections** | Active client connections | Approaching `maxConnections` |
| **Opcounters** | Operations/second (insert, query, update, delete) | Sudden spikes or drops |
| **Replication Lag** | How far secondaries are behind primary | > 10 seconds |
| **Cache Usage** | WiredTiger cache utilization | > 80% consistently |
| **Disk I/O** | Read/write throughput | Sustained high I/O |
| **Page Faults** | Data not in memory, read from disk | High rate = need more RAM |
| **Queue Length** | Operations waiting to execute | > 0 consistently |
| **Tickets Available** | Concurrent operation slots | Approaching 0 |
| **Disk Space** | Storage utilization | > 80% |
| **Scan/Return Ratio** | Docs examined vs returned | >> 1 means missing indexes |

### Atlas Monitoring Dashboard

Atlas provides a built-in monitoring dashboard showing:

1. **Real-time Performance Panel** — Operations, connections, network
2. **Metrics** — Historical graphs for all key metrics
3. **Performance Advisor** — Suggests missing indexes based on slow queries
4. **Real-Time Performance Panel** — See currently running operations

### mongostat (Self-Managed)

```bash
mongostat --uri="mongodb://admin:pass@localhost:27017" --rowcount=10
```

Shows per-second statistics: inserts, queries, updates, deletes, connections, memory.

### mongotop (Self-Managed)

```bash
mongotop --uri="mongodb://admin:pass@localhost:27017" 5
```

Shows which collections are getting the most read/write activity.

---

## Alerting

### Atlas Alerts

Set up alerts for:
- Connections > 80% of limit
- Replication lag > 10 seconds
- Disk usage > 80%
- CPU > 90% for 5 minutes
- No primary available (election happening)
- Slow queries > threshold

Atlas can alert via: Email, Slack, PagerDuty, Webhooks, SMS.

### Custom Monitoring

```python
# Simple monitoring script
from pymongo import MongoClient

client = MongoClient(uri)
status = client.admin.command("serverStatus")

# Check connections
current = status["connections"]["current"]
available = status["connections"]["available"]
print(f"Connections: {current}/{current + available}")

# Check opcounters
ops = status["opcounters"]
print(f"Operations: insert={ops['insert']}, query={ops['query']}, "
      f"update={ops['update']}, delete={ops['delete']}")

# Check replication lag
rs_status = client.admin.command("replSetGetStatus")
for member in rs_status["members"]:
    if member.get("optimeDate") and member["stateStr"] == "SECONDARY":
        lag = (rs_status["date"] - member["optimeDate"]).total_seconds()
        print(f"Replication lag ({member['name']}): {lag}s")
```

---

## Performance Advisor (Atlas)

Atlas Performance Advisor automatically:
- Identifies slow queries (> 100ms)
- Suggests indexes to create
- Shows which queries would benefit most
- Estimates the performance improvement

📌 Check Performance Advisor weekly and create suggested indexes.

---

## Log Analysis

```bash
# MongoDB logs slow queries automatically (default: > 100ms)
# Find slow queries in the log:
grep "COMMAND" /var/log/mongodb/mongod.log | grep -E "[0-9]{4}ms"

# Change slow query threshold
db.setProfilingLevel(1, { slowms: 50 })  # Log queries slower than 50ms

# Query the profiler
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

---

## 📌 Key Takeaways

1. **Test your restores** — a backup is only as good as your ability to restore it
2. **Atlas M10+** provides continuous backup with point-in-time recovery
3. **Monitor proactively** — set up alerts before problems occur
4. **Key metrics:** connections, replication lag, cache usage, disk space
5. **Performance Advisor** is free on Atlas and suggests missing indexes
6. **Profile slow queries** to find optimization opportunities
