# MongoDB Atlas Setup (Free Tier)

Step-by-step guide to getting MongoDB Atlas running in about 5 minutes.

---

## Step 1: Create an Account

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Click **"Try Free"**
3. Sign up with email or Google/GitHub account
4. Verify your email address

---

## Step 2: Deploy a Free Cluster

1. After login, you'll see the **"Deploy your cluster"** screen
2. Select **M0 Free** tier (bottom option)
3. Choose a cloud provider: **AWS**, **GCP**, or **Azure** (all work fine)
4. Choose the region **closest to you** for lowest latency
5. Cluster name: keep the default `Cluster0` or rename it
6. Click **"Create Deployment"**

📌 The cluster takes 1-3 minutes to provision. You'll see a spinner, then a green "Active" status.

---

## Step 3: Create a Database User

You should be prompted to create a user immediately after cluster creation. If not:

1. Go to **Security** → **Database Access** in the left sidebar
2. Click **"Add New Database User"**
3. Authentication: **Password**
4. Enter a username and password (save these — you'll need them for the connection string)
5. Database User Privileges: **"Read and write to any database"**
6. Click **"Add User"**

⚠️ **Don't use special characters** in the password (`@`, `:`, `/`, `%`) — they cause issues in connection strings. Stick to letters and numbers.

---

## Step 4: Whitelist Your IP Address

1. Go to **Security** → **Network Access**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for development) or **"Add Current IP Address"**
4. Click **"Confirm"**

⚠️ "Allow Access from Anywhere" (`0.0.0.0/0`) is fine for learning but **not for production**.

---

## Step 5: Get Your Connection String

1. Go to **Deployment** → **Database** in the left sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Drivers"**
4. Select **Python** and version **3.12 or later**
5. Copy the connection string — it looks like:

```
mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/
```

6. Replace `<password>` with your actual password
7. Paste it into your `.env` file:

```bash
cp .env.example .env
# Edit .env and paste your connection string
```

---

## Step 6: Load Sample Data

Atlas provides free sample datasets perfect for learning:

1. Go to **Deployment** → **Database**
2. Click the **"..."** menu on your cluster
3. Click **"Load Sample Dataset"**
4. Wait 2-3 minutes for data to load

This gives you several databases including:

| Database | Description | Great For |
|----------|-------------|-----------|
| `sample_mflix` | Movies, comments, users | CRUD, aggregation exercises |
| `sample_airbnb` | Listings and reviews | Geospatial queries |
| `sample_analytics` | Customer accounts | Schema design study |
| `sample_restaurants` | NYC restaurants | Text search, geospatial |
| `sample_training` | Various collections | General practice |

📌 **We use `sample_mflix` throughout this repository** — make sure it's loaded.

---

## Step 7: Verify with Atlas UI

1. Go to **Deployment** → **Database**
2. Click **"Browse Collections"**
3. You should see the sample databases in the left panel
4. Click on `sample_mflix` → `movies` to browse documents

---

## Troubleshooting

### "Connection timed out"
- Check **Network Access** — is your IP whitelisted?
- If on a VPN, whitelist that IP too (or use `0.0.0.0/0`)

### "Authentication failed"
- Verify username/password in **Database Access**
- Make sure you replaced `<password>` in the connection string
- No special characters in password

### "dnspython must be installed"
```bash
pip install dnspython
```
The `mongodb+srv://` protocol requires this package.

### "ServerSelectionTimeoutError"
- Cluster might still be provisioning — wait a minute
- Check if the cluster is paused (M0 clusters pause after 60 days of inactivity)

---

## 📌 Key Takeaways

1. Atlas M0 free tier gives you **512 MB** — plenty for learning
2. Always **whitelist your IP** before trying to connect
3. **Load sample data** to follow along with exercises in this repo
4. Keep your connection string in `.env` and never commit it to Git
5. The `sample_mflix` database is used throughout this repository
