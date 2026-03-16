# 10 — Production MongoDB

> **Goal:** Understand what it takes to run MongoDB in production — replication, sharding, security, and monitoring.

---

## Production Readiness Checklist

- [ ] **Replication** — Replica set with at least 3 members
- [ ] **Authentication** — Database users with least-privilege roles
- [ ] **Network security** — IP whitelisting, VPC peering, or private endpoints
- [ ] **Encryption** — TLS in transit, encryption at rest
- [ ] **Backups** — Automated backups with point-in-time recovery
- [ ] **Monitoring** — Alerts for key metrics (connections, opcounters, disk usage)
- [ ] **Indexes** — All frequent queries covered by indexes
- [ ] **Connection pooling** — Appropriate pool sizes for your workload
- [ ] **Error handling** — Retry logic for transient failures

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [replication.md](replication.md) | Replica sets, elections, read/write concerns |
| [sharding.md](sharding.md) | Horizontal scaling, shard keys, architecture |
| [security.md](security.md) | Auth, encryption, network security |
| [backup_monitoring.md](backup_monitoring.md) | Backups, monitoring, alerting |

---

## 📌 Key Takeaways

1. **Never run a single MongoDB server in production** — always use replica sets
2. **Security is layered** — authentication + authorization + encryption + network
3. **Monitor before you need to** — set up alerts early
4. **Atlas handles most of this automatically** — but understand the concepts
5. **Shard only when necessary** — it adds significant complexity

---

**Next:** [resources/](../resources/) — Study plan, cheatsheets, interview prep
