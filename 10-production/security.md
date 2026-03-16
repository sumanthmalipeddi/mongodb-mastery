# Security

## Security Layers

MongoDB security follows a defense-in-depth approach:

```
Network Security  →  Authentication  →  Authorization  →  Encryption
(Who can reach)     (Who are you)      (What can you do)  (Protect data)
```

---

## Authentication

### SCRAM (Default)
Salted Challenge Response Authentication Mechanism. Username/password based.

```javascript
// Create a user
db.createUser({
  user: "appUser",
  pwd: "securePassword123",
  roles: [{ role: "readWrite", db: "myapp" }]
})
```

### X.509 Certificates
TLS certificate-based authentication. Used for:
- Client-to-server authentication
- Internal replica set member authentication

### LDAP / Active Directory
Centralized authentication for enterprise environments.

### AWS IAM / Azure AD / GCP
Cloud-native authentication supported in Atlas.

---

## Authorization (Roles)

MongoDB uses Role-Based Access Control (RBAC).

### Built-in Roles

| Role | Scope | Permissions |
|------|-------|-------------|
| `read` | Database | Read all collections |
| `readWrite` | Database | Read + write all collections |
| `dbAdmin` | Database | Schema management, indexing, stats |
| `userAdmin` | Database | Create/modify users and roles |
| `clusterAdmin` | Cluster | Manage replica sets, sharding |
| `root` | All | Superuser (avoid in production) |
| `readAnyDatabase` | All DBs | Read all databases |
| `readWriteAnyDatabase` | All DBs | Read + write all databases |

### Principle of Least Privilege

```javascript
// Application user — only needs readWrite on its database
db.createUser({
  user: "myapp",
  pwd: "...",
  roles: [{ role: "readWrite", db: "myapp_production" }]
})

// Analytics user — read-only
db.createUser({
  user: "analyst",
  pwd: "...",
  roles: [{ role: "read", db: "myapp_production" }]
})

// Backup user
db.createUser({
  user: "backup",
  pwd: "...",
  roles: [{ role: "backup" }, { role: "restore" }]
})
```

---

## Network Security

### IP Whitelisting (Atlas)
- Only allow connections from specific IP addresses
- Use CIDR notation: `10.0.0.0/24`
- `0.0.0.0/0` allows all IPs — **never in production**

### VPC Peering
Connect your Atlas cluster directly to your AWS/GCP/Azure VPC. Traffic never crosses the public internet.

### Private Endpoints
AWS PrivateLink / Azure Private Link — the most secure option. Traffic stays within the cloud provider's network.

### Firewall Rules (Self-Managed)
```bash
# Only allow MongoDB port from app servers
iptables -A INPUT -p tcp --dport 27017 -s 10.0.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 27017 -j DROP
```

---

## Encryption

### In Transit (TLS/SSL)
All connections should use TLS.

```python
# PyMongo with TLS (Atlas uses TLS by default)
client = MongoClient(
    uri,
    tls=True,
    tlsCAFile="/path/to/ca-cert.pem"
)
```

Atlas enforces TLS on all connections automatically.

### At Rest
Encrypts data files on disk.
- **Atlas:** Enabled by default (AES-256)
- **Enterprise:** MongoDB Encrypted Storage Engine
- **Community:** Use OS-level disk encryption (LUKS, BitLocker)

### Client-Side Field Level Encryption (CSFLE)
Encrypt specific fields before they reach the server. Not even database admins can read encrypted fields.

```python
# Conceptual — fields are encrypted before leaving the driver
{
  "name": "Alice",                           # Plain text
  "ssn": Binary("encrypted_data..."),        # Encrypted — server can't read
  "credit_card": Binary("encrypted_data...") # Encrypted
}
```

---

## Security Checklist for Production

- [ ] Enable authentication (`--auth` flag or Atlas)
- [ ] Create application-specific users with minimal roles
- [ ] Never use `root` role for applications
- [ ] Enable TLS for all connections
- [ ] Whitelist specific IP addresses (not `0.0.0.0/0`)
- [ ] Use VPC peering or private endpoints for production
- [ ] Enable encryption at rest
- [ ] Consider CSFLE for sensitive fields (PII, payment data)
- [ ] Enable audit logging (Enterprise/Atlas)
- [ ] Rotate credentials regularly
- [ ] Keep MongoDB version updated
- [ ] Disable unused features and ports

---

## Atlas Security Features

| Feature | Tier |
|---------|------|
| TLS encryption in transit | All tiers (including free) |
| Encryption at rest | All tiers |
| IP whitelisting | All tiers |
| Database users + RBAC | All tiers |
| VPC peering | M10+ |
| Private endpoints | M10+ |
| LDAP integration | M10+ |
| Auditing | M10+ |
| Client-side field level encryption | M10+ |

---

## 📌 Key Takeaways

1. **Authentication + Authorization + Encryption** — all three are required
2. **Least privilege** — each user/app gets only the permissions it needs
3. **Never expose MongoDB to the public internet** without IP whitelisting
4. **TLS everywhere** — Atlas enforces this by default
5. **Atlas handles most security automatically** on paid tiers
