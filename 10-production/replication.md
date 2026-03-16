# Replication

## What is Replication?

Replication maintains **identical copies** of your data on multiple servers. A **replica set** is a group of MongoDB servers that maintain the same data set.

```
Client
  │
  ▼
┌─────────┐    replicates    ┌───────────┐
│ PRIMARY  │ ──────────────► │ SECONDARY │
│ (reads + │                 │ (reads)   │
│  writes) │                 └───────────┘
└─────────┘    replicates    ┌───────────┐
               ──────────────► │ SECONDARY │
                              │ (reads)   │
                              └───────────┘
```

## Why Replicate?

1. **High availability** — If the primary fails, a secondary becomes the new primary
2. **Data redundancy** — Multiple copies prevent data loss
3. **Read scaling** — Read from secondaries to distribute load
4. **Disaster recovery** — Copies in different data centers

---

## Replica Set Architecture

### Members

| Role | Description | Votes | Data |
|------|-------------|-------|------|
| **Primary** | Receives all writes | Yes | Yes |
| **Secondary** | Replicates from primary, can serve reads | Yes | Yes |
| **Arbiter** | Only votes in elections, no data | Yes | No |
| **Hidden** | Not visible to clients, used for reporting/backup | Yes | Yes |
| **Delayed** | Replays oplog with a delay (rolling backup) | Yes | Yes |

📌 **Best practice:** 3 data-bearing members minimum. Avoid arbiters if possible.

### How Replication Works

1. Writes go to the **primary**
2. Primary records the operation in the **oplog** (operations log)
3. Secondaries **tail the oplog** and replay operations
4. Replication is asynchronous by default (secondaries may lag slightly)

---

## Elections

When the primary becomes unavailable, the remaining members hold an **election**:

1. Secondaries detect the primary is unreachable (heartbeat timeout: 10s)
2. An eligible secondary calls for an election
3. Members vote based on priority, data freshness, and connectivity
4. The winner becomes the new primary
5. Typically completes in **10-12 seconds**

📌 Your application sees a brief write interruption during elections. Use `retryWrites: true`.

---

## Read Preference

Controls which members your application reads from.

| Mode | Description | Use Case |
|------|-------------|----------|
| `primary` | Always read from primary (default) | Consistency-critical reads |
| `primaryPreferred` | Primary if available, else secondary | Most applications |
| `secondary` | Only read from secondaries | Analytics, reporting |
| `secondaryPreferred` | Secondary if available, else primary | Read-heavy workloads |
| `nearest` | Read from the member with lowest latency | Geo-distributed apps |

```python
from pymongo import ReadPreference

# Read from secondary
collection.with_options(read_preference=ReadPreference.SECONDARY).find({})
```

⚠️ Reads from secondaries may return **stale data** (replication lag).

---

## Write Concern

Controls how many members must acknowledge a write before it's considered successful.

| Write Concern | Description | Durability | Speed |
|--------------|-------------|------------|-------|
| `w: 0` | Don't wait for acknowledgment | None | Fastest |
| `w: 1` | Wait for primary only (default) | Primary | Fast |
| `w: "majority"` | Wait for majority of members | Strong | Slower |
| `w: 3` | Wait for 3 specific members | Strongest | Slowest |

```python
# Write with majority concern
collection.insert_one(doc, write_concern=WriteConcern(w="majority"))
```

📌 **Production recommendation:** `w: "majority"` for important data.

---

## Read Concern

Controls the consistency level of data returned by reads.

| Read Concern | Description |
|-------------|-------------|
| `local` | Returns most recent data on the queried member (default) |
| `available` | Same as local for replica sets |
| `majority` | Only returns data acknowledged by a majority |
| `linearizable` | Strongest — reflects all successful majority writes |
| `snapshot` | For multi-document transactions |

---

## Setting Up a Replica Set (Self-Managed)

```bash
# Start 3 MongoDB instances
mongod --replSet rs0 --port 27017 --dbpath /data/db1
mongod --replSet rs0 --port 27018 --dbpath /data/db2
mongod --replSet rs0 --port 27019 --dbpath /data/db3

# Connect to one and initiate
mongosh --port 27017

rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },
    { _id: 1, host: "localhost:27018" },
    { _id: 2, host: "localhost:27019" }
  ]
})

rs.status()  // Check replica set status
```

### In Atlas

Atlas automatically configures replica sets. Every Atlas cluster (even free M0) is a replica set.

---

## 📌 Key Takeaways

1. **Always use replica sets in production** — never a standalone server
2. **Elections are automatic** — your app just needs retry logic
3. **Write concern `majority`** ensures data isn't lost if the primary fails
4. **Read preference** lets you trade consistency for performance
5. Atlas handles replica set management automatically
