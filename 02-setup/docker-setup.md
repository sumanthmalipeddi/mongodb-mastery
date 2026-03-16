# Docker Setup for MongoDB

Run MongoDB locally with Docker — no installation, no cloud account needed.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

---

## Option A: One-Liner (Quick Start)

```bash
docker run -d --name mongodb -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret123 \
  -v mongo_data:/data/db \
  mongo:latest
```

Connection string for `.env`:
```
MONGODB_URI=mongodb://admin:secret123@localhost:27017/
```

---

## Option B: Docker Compose (Recommended)

Docker Compose gives you MongoDB **and** a web-based GUI (Mongo Express) with one command.

```bash
cd 02-setup
docker compose up -d
```

This starts:
- **MongoDB** on `localhost:27017`
- **Mongo Express** (GUI) on `localhost:8081` (login: admin / admin123)

See [docker-compose.yml](docker-compose.yml) for the full configuration.

---

## Verify MongoDB is Running

### Check container status:
```bash
docker ps
```

You should see `mongodb` and `mongo-gui` containers with status "Up".

### Connect with mongosh:
```bash
docker exec -it mongodb mongosh -u admin -p secret123
```

You should see the mongosh prompt:
```
test>
```

Try a quick command:
```javascript
show dbs
db.test.insertOne({ hello: "world" })
db.test.find()
```

### Connect with Mongo Express:

Open [http://localhost:8081](http://localhost:8081) in your browser.
- Username: `admin`
- Password: `admin123`

You'll see a web interface to browse databases, collections, and documents.

---

## Update Your .env File

```bash
# In the project root
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URI=mongodb://admin:secret123@localhost:27017/
```

---

## Loading Sample Data (Optional)

Unlike Atlas, Docker doesn't come with sample datasets. To load `sample_mflix`:

1. Download the sample data from [MongoDB's GitHub](https://github.com/neelabalan/mongodb-sample-dataset)
2. Use `mongoimport` to load it:

```bash
# Example: loading the movies collection
docker exec -i mongodb mongoimport \
  --uri "mongodb://admin:secret123@localhost:27017/sample_mflix?authSource=admin" \
  --collection movies \
  --file movies.json \
  --jsonArray
```

Alternatively, the scripts in this repo will create their own collections when you run them.

---

## Stopping and Cleaning Up

### Stop containers (data preserved):
```bash
docker compose down
```

### Stop and remove data:
```bash
docker compose down -v
```

### Remove everything:
```bash
docker compose down -v --rmi all
```

---

## Troubleshooting

### "Port 27017 already in use"
Another MongoDB instance or service is using the port:
```bash
lsof -i :27017
# Kill the process or change the port in docker-compose.yml
```

### "Mongo Express can't connect"
Mongo Express may start before MongoDB is ready. Wait 10 seconds and refresh, or restart:
```bash
docker compose restart mongo-express
```

### "Authentication failed"
Make sure you're using `admin` as the authentication database:
```
mongodb://admin:secret123@localhost:27017/?authSource=admin
```

---

## 📌 Key Takeaways

1. `docker compose up -d` starts MongoDB + GUI in seconds
2. Data persists in the `mongo_data` volume even after stopping containers
3. Use `docker compose down -v` to wipe data and start fresh
4. Mongo Express at `localhost:8081` gives you a visual database browser
5. Docker is great for local development; Atlas is better for production and sample data
