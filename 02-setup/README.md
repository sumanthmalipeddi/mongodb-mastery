# 02 — Setting Up MongoDB

> **Goal:** Get MongoDB running so you can start writing queries.

You have two options — pick whichever fits your workflow:

| Option | Best For | Time | Cost |
|--------|----------|------|------|
| [MongoDB Atlas](atlas-setup.md) | Cloud-hosted, zero install, free tier | 5 min | Free (M0 tier) |
| [Docker](docker-setup.md) | Local development, full control, offline work | 2 min | Free |

---

## Quick Comparison

### Atlas (Cloud)
- ✅ No installation required
- ✅ Free 512 MB cluster (M0)
- ✅ Pre-loaded sample datasets (sample_mflix, etc.)
- ✅ Built-in monitoring, backups, and vector search
- ⚠️ Requires internet connection
- ⚠️ Slight latency for local development

### Docker (Local)
- ✅ Works offline
- ✅ Zero latency
- ✅ Full control over configuration
- ✅ Includes Mongo Express GUI
- ⚠️ No sample datasets pre-loaded (you'd load them manually)
- ⚠️ Requires Docker installed

---

## 📂 Files in This Section

| File | Description |
|------|-------------|
| [atlas-setup.md](atlas-setup.md) | Step-by-step Atlas free tier setup |
| [docker-setup.md](docker-setup.md) | Docker and Docker Compose setup |
| [docker-compose.yml](docker-compose.yml) | Ready-to-use Compose file |
| [connect-test.py](connect-test.py) | Python script to verify your connection |

---

## 📌 Key Takeaways

1. **Atlas** is easiest for getting started — free tier is generous for learning
2. **Docker** is best for local development and offline work
3. Use `connect-test.py` to verify your setup before moving on
4. Both options work with all the code in this repository

---

**Next:** [03-crud-operations/](../03-crud-operations/) — Start querying MongoDB
