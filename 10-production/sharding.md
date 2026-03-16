# Sharding

## What is Sharding?

**Sharding** distributes data across multiple servers (shards). Each shard holds a subset of the data. Together, all shards hold the complete dataset.

```
Client
  │
  ▼
┌─────────┐
│ mongos   │  (Router — directs queries to the right shard)
└─────────┘
  │   │   │
  ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐
│Shard│ │Shard│ │Shard│
│ A   │ │ B   │ │ C   │
│A-H  │ │I-P  │ │Q-Z  │
└────┘ └────┘ └────┘
         │
     ┌────────┐
     │ Config  │  (Stores metadata: which data is on which shard)
     │ Servers │
     └────────┘
```

---

## When to Shard

✅ **Shard when:**
- Your dataset exceeds the storage capacity of a single server
- Write throughput exceeds what a single replica set can handle
- You need to geo-distribute data (zone sharding)

❌ **Don't shard when:**
- You can solve the problem with better indexes
- Your workload is read-heavy (use read replicas instead)
- Your data fits on a single server (even a big one)
- You're trying to fix slow queries (fix indexes/schema first)

📌 **Sharding adds significant complexity.** Exhaust other options first.

---

## Shard Key

The **shard key** determines how data is distributed across shards. This is the most critical decision in sharding.

### Good Shard Key Properties

| Property | Description |
|----------|-------------|
| **High cardinality** | Many unique values (not boolean or enum) |
| **Even distribution** | Data spreads evenly across shards |
| **Query isolation** | Common queries target one shard, not all |
| **Non-monotonic** | Not always increasing (avoids "hot shard") |

### Shard Key Examples

| Use Case | Good Key | Bad Key | Why |
|----------|----------|---------|-----|
| User data | `{user_id: "hashed"}` | `{country: 1}` | Country has low cardinality |
| Time-series | `{sensor_id: 1, timestamp: 1}` | `{timestamp: 1}` | Monotonic → hot shard |
| E-commerce | `{customer_id: "hashed"}` | `{status: 1}` | Only 3-4 values |

---

## Types of Sharding

### Ranged Sharding
Data is divided into ranges based on the shard key value.

```
Shard A: user_id 1-1000
Shard B: user_id 1001-2000
Shard C: user_id 2001-3000
```

✅ Good for range queries
❌ Can create "hot shards" if data isn't evenly distributed

### Hashed Sharding
A hash of the shard key determines placement. Ensures even distribution.

```javascript
sh.shardCollection("mydb.users", { user_id: "hashed" })
```

✅ Even distribution
❌ Range queries must hit all shards (scatter-gather)

### Zone Sharding
Assign data ranges to specific shards based on rules (e.g., geographic).

```
Zone "US": Shard A, Shard B  (users in North America)
Zone "EU": Shard C, Shard D  (users in Europe)
```

✅ Data locality for geo-distributed applications
❌ More complex to manage

---

## Architecture Components

| Component | Role | Count |
|-----------|------|-------|
| **mongos** | Query router — clients connect here | 2+ (for HA) |
| **Config Servers** | Store metadata and chunk mappings | 3 (replica set) |
| **Shards** | Store the actual data | 2+ (each is a replica set) |

---

## Chunks and Balancing

- Data is split into **chunks** (~128 MB each by default)
- The **balancer** automatically moves chunks between shards to maintain even distribution
- You can see chunk distribution with `sh.status()`

---

## Sharding in Atlas

Atlas makes sharding much easier:

1. Scale your cluster to M30 or higher
2. Select **"Shard your cluster"** in the Atlas UI
3. Choose the number of shards
4. Select a shard key for each collection

Atlas handles mongos routing, config servers, and balancing automatically.

---

## 📌 Key Takeaways

1. **Shard as a last resort** — try indexing, schema optimization, and read replicas first
2. **Shard key choice is permanent** and determines performance
3. **Hashed sharding** for even distribution; **ranged** for range queries
4. **Every shard is a replica set** — sharding doesn't replace replication
5. Atlas handles the infrastructure; you just choose the shard key
