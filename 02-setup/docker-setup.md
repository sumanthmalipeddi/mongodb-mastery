# Docker Setup for MongoDB

Run MongoDB locally with Docker — no installation, no cloud account needed.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- If you're not sure, open a terminal and run `docker --version` — if you see a version number, you're good

---

## Option A: One-Liner (Quick Start)

```bash
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=changeme \
  -v mongo_data:/data/db \
  mongo:latest
```

> **What does this do?** It downloads MongoDB, starts it in the background (`-d`), maps port 27017 so your code can connect, and saves data in a volume so it survives restarts.

After running, add this to your `.env` file:
```
MONGODB_URI=mongodb://admin:changeme@localhost:27017/
```

---

## Option B: Docker Compose (Recommended)

Docker Compose gives you MongoDB **and** a web-based GUI (Mongo Express) with one command.

### Step 1: Set up your credentials

```bash
# From the project root
cp .env.example .env
```

Open `.env` and set your credentials. The defaults work fine for local development:
```
MONGO_USERNAME=admin
MONGO_PASSWORD=changeme
ME_USERNAME=admin
ME_PASSWORD=changeme
MONGODB_URI=mongodb://admin:changeme@localhost:27017/
```

> **Important:** If you change the username/password here, the Docker Compose file will automatically use your new values.

### Step 2: Start the containers

```bash
cd 02-setup
docker compose up -d
```

### Step 3: Verify it's running

```bash
docker ps
```

You should see two containers running:

| Container | Port | What it does |
|-----------|------|-------------|
| `mongodb` | `localhost:27017` | The MongoDB database |
| `mongo-gui` | `localhost:8081` | Mongo Express — a web GUI to browse your data |

> **What is Mongo Express?** It's like phpMyAdmin but for MongoDB. You can browse databases, view documents, run queries — all from your browser. Great for beginners who want to see what's happening inside the database.

---

## Verify MongoDB is Working

### Option 1: Run the test script (easiest)

```bash
python 02-setup/connect-test.py
```

If you see a success message, you're connected!

### Option 2: Connect with mongosh (command line)

```bash
docker exec -it mongodb mongosh -u admin -p changeme
```

You should see the mongosh prompt:
```
test>
```

Try these commands to make sure it works:
```javascript
// Show all databases
show dbs

// Insert a test document
db.test.insertOne({ hello: "world" })

// Read it back
db.test.find()

// Clean up
db.test.drop()
```

### Option 3: Use Mongo Express (visual)

Open [http://localhost:8081](http://localhost:8081) in your browser.
- Username: the `ME_USERNAME` from your `.env` (default: `admin`)
- Password: the `ME_PASSWORD` from your `.env` (default: `changeme`)

You'll see a web interface to browse databases, collections, and documents visually.

---

## Loading Sample Data (Optional)

Unlike Atlas, Docker doesn't come with sample datasets pre-loaded. You have two options:

### Option A: Let the scripts create data
Just run the Python scripts in this repo — they create their own collections and insert sample data. No extra setup needed.

### Option B: Load sample_mflix manually
Some exercises use the `sample_mflix` database. To load it:

1. Download the sample data from [MongoDB's GitHub](https://github.com/neelabalan/mongodb-sample-dataset)
2. Use `mongoimport` to load it:

```bash
# Example: loading the movies collection
docker exec -i mongodb mongoimport \
  --uri "mongodb://admin:changeme@localhost:27017/sample_mflix?authSource=admin" \
  --collection movies \
  --file movies.json \
  --jsonArray
```

> **Don't worry about this now.** Start with the scripts — they'll tell you if they need sample_mflix.

---

## Stopping and Cleaning Up

```bash
# Stop containers (your data is preserved)
docker compose down

# Stop AND delete all data (fresh start)
docker compose down -v

# Remove everything including downloaded images
docker compose down -v --rmi all
```

> **When to use each:**
> - `docker compose down` — end of study session, data stays safe
> - `docker compose down -v` — want to start completely fresh
> - `docker compose down -v --rmi all` — done with MongoDB, free up disk space

---

## Troubleshooting

### "Port 27017 already in use"
Another MongoDB instance or service is using the port:
```bash
# Find what's using the port
lsof -i :27017

# Kill it (replace PID with the number from above)
kill -9 <PID>

# Or change the port in docker-compose.yml to 27018:27017
```

### "Mongo Express can't connect"
Mongo Express sometimes starts before MongoDB is ready. Wait 10 seconds and refresh your browser, or restart it:
```bash
docker compose restart mongo-gui
```

### "Authentication failed"
Make sure:
1. Your `.env` credentials match what you started Docker with
2. If you changed credentials, you need to remove the old data first:
```bash
docker compose down -v
docker compose up -d
```

### "Cannot connect to the Docker daemon"
Docker Desktop isn't running. Open Docker Desktop and wait for it to start, then try again.

---

## 📌 Key Takeaways

1. `docker compose up -d` starts MongoDB + GUI in seconds
2. All credentials are in your `.env` file — change them there, not in docker-compose.yml
3. Data persists in the `mongo_data` volume even after stopping containers
4. Use `docker compose down -v` to wipe data and start fresh
5. Mongo Express at `localhost:8081` gives you a visual database browser
6. Docker is great for local development; Atlas is better for production and sample data
