# CRUD Exercises

Practice exercises using the `sample_mflix.movies` collection. Load sample data in Atlas first.

---

## Exercise 1: Find a Specific Movie
Find the document for the movie "The Godfather".

<details>
<summary>💡 Hint</summary>
Use `find_one` with a title filter.
</details>

<details>
<summary>✅ Solution</summary>

```python
movie = db.movies.find_one({"title": "The Godfather"})
print(movie)
```
</details>

---

## Exercise 2: Count Movies by Rating
How many movies are rated "PG-13"?

<details>
<summary>💡 Hint</summary>
Use `count_documents`.
</details>

<details>
<summary>✅ Solution</summary>

```python
count = db.movies.count_documents({"rated": "PG-13"})
print(f"PG-13 movies: {count}")
```
</details>

---

## Exercise 3: Find Movies from a Decade
Find all movies released between 1990 and 1999 (inclusive). Show only title and year.

<details>
<summary>💡 Hint</summary>
Use `$gte` and `$lte` with a projection.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"year": {"$gte": 1990, "$lte": 1999}},
    {"title": 1, "year": 1, "_id": 0}
)
for movie in cursor:
    print(movie)
```
</details>

---

## Exercise 4: Top Rated Movies
Find the 10 highest-rated movies (by IMDb rating) with at least 50,000 votes. Show title, rating, and votes.

<details>
<summary>💡 Hint</summary>
Use dot notation `imdb.rating` and `imdb.votes`, then `.sort()` and `.limit()`.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"imdb.votes": {"$gte": 50000}},
    {"title": 1, "imdb.rating": 1, "imdb.votes": 1, "_id": 0}
).sort("imdb.rating", -1).limit(10)

for movie in cursor:
    print(f"{movie['title']} — {movie['imdb']['rating']} ({movie['imdb']['votes']} votes)")
```
</details>

---

## Exercise 5: Genre Search
Find all movies that are BOTH "Sci-Fi" AND "Action".

<details>
<summary>💡 Hint</summary>
Use `$all` on the genres array.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"genres": {"$all": ["Sci-Fi", "Action"]}},
    {"title": 1, "genres": 1, "_id": 0}
)
for movie in cursor:
    print(f"{movie['title']} — {movie['genres']}")
```
</details>

---

## Exercise 6: Regex Title Search
Find all movies whose title starts with "Star" (case-insensitive).

<details>
<summary>💡 Hint</summary>
Use `$regex` with `$options: "i"` and the `^` anchor.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"title": {"$regex": "^Star", "$options": "i"}},
    {"title": 1, "year": 1, "_id": 0}
).sort("year", 1)

for movie in cursor:
    print(f"{movie['title']} ({movie.get('year', 'N/A')})")
```
</details>

---

## Exercise 7: Movies Without a Field
Find movies that do NOT have a `poster` field.

<details>
<summary>💡 Hint</summary>
Use `$exists: False`.
</details>

<details>
<summary>✅ Solution</summary>

```python
count = db.movies.count_documents({"poster": {"$exists": False}})
print(f"Movies without poster: {count}")
```
</details>

---

## Exercise 8: OR Query
Find movies that are either rated "G" OR have an IMDb rating of 9.0 or higher.

<details>
<summary>💡 Hint</summary>
Use `$or` with an array of conditions.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"$or": [
        {"rated": "G"},
        {"imdb.rating": {"$gte": 9.0}}
    ]},
    {"title": 1, "rated": 1, "imdb.rating": 1, "_id": 0}
).limit(10)

for movie in cursor:
    print(movie)
```
</details>

---

## Exercise 9: Pagination
Implement pagination: get page 3 of movies from year 2000, with 10 movies per page. Sort by title.

<details>
<summary>💡 Hint</summary>
Page 3 means skip the first 20 results (2 pages × 10 per page).
</details>

<details>
<summary>✅ Solution</summary>

```python
page = 3
per_page = 10
skip_count = (page - 1) * per_page

cursor = db.movies.find(
    {"year": 2000},
    {"title": 1, "_id": 0}
).sort("title", 1).skip(skip_count).limit(per_page)

for movie in cursor:
    print(movie["title"])
```
</details>

---

## Exercise 10: Distinct Languages
What are all the unique languages in movies from 2015 or later?

<details>
<summary>💡 Hint</summary>
Use `distinct` with a filter.
</details>

<details>
<summary>✅ Solution</summary>

```python
languages = db.movies.distinct("languages", {"year": {"$gte": 2015}})
print(f"Languages: {sorted(languages)}")
print(f"Count: {len(languages)}")
```
</details>

---

## Exercise 11: Update a Movie's Rating
Add a field `my_rating: 10` to "The Shawshank Redemption".

<details>
<summary>💡 Hint</summary>
Use `update_one` with `$set`.
</details>

<details>
<summary>✅ Solution</summary>

```python
result = db.movies.update_one(
    {"title": "The Shawshank Redemption"},
    {"$set": {"my_rating": 10}}
)
print(f"Modified: {result.modified_count}")
```
</details>

---

## Exercise 12: Bulk Tag Update
Add the tag "classic" to all movies released before 1970 with an IMDb rating above 7.0.

<details>
<summary>💡 Hint</summary>
Use `update_many` with `$set`. Combine conditions in the filter.
</details>

<details>
<summary>✅ Solution</summary>

```python
result = db.movies.update_many(
    {"year": {"$lt": 1970}, "imdb.rating": {"$gt": 7.0}},
    {"$set": {"classic": True}}
)
print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
```
</details>

---

## Exercise 13: Array with Exact Size
Find movies with exactly 5 genres.

<details>
<summary>💡 Hint</summary>
Use `$size` on the genres array.
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {"genres": {"$size": 5}},
    {"title": 1, "genres": 1, "_id": 0}
)
for movie in cursor:
    print(f"{movie['title']} — {movie['genres']}")
```
</details>

---

## Exercise 14: Complex Multi-Condition Query
Find Drama movies from the 2010s (2010–2019) with IMDb rating ≥ 8.0, at least 100,000 votes, that are NOT rated "R". Sort by rating descending, show top 10.

<details>
<summary>💡 Hint</summary>
Combine multiple conditions in one filter dict. Use `$ne` for "not rated R".
</details>

<details>
<summary>✅ Solution</summary>

```python
cursor = db.movies.find(
    {
        "genres": "Drama",
        "year": {"$gte": 2010, "$lte": 2019},
        "imdb.rating": {"$gte": 8.0},
        "imdb.votes": {"$gte": 100000},
        "rated": {"$ne": "R"}
    },
    {"title": 1, "year": 1, "imdb.rating": 1, "rated": 1, "_id": 0}
).sort("imdb.rating", -1).limit(10)

for movie in cursor:
    print(f"{movie['title']} ({movie['year']}) — {movie['imdb']['rating']} [{movie.get('rated', 'N/A')}]")
```
</details>

---

## Exercise 15: Find and Count by Director
Find how many movies each of these directors has: "Steven Spielberg", "Martin Scorsese", "Christopher Nolan".

<details>
<summary>💡 Hint</summary>
Use `count_documents` with a filter on the `directors` array for each director.
</details>

<details>
<summary>✅ Solution</summary>

```python
directors = ["Steven Spielberg", "Martin Scorsese", "Christopher Nolan"]

for director in directors:
    count = db.movies.count_documents({"directors": director})
    print(f"{director}: {count} movies")
```
</details>

---

## 📌 Key Takeaways

1. **Comparison operators** (`$gt`, `$lt`, `$in`, `$ne`) replace SQL's `>`, `<`, `IN`, `!=`
2. **Dot notation** (`imdb.rating`) lets you query nested fields
3. **Array queries** are first-class — `$all`, `$size`, `$elemMatch`
4. **`$regex`** replaces SQL's `LIKE` operator
5. **Projection** controls which fields are returned (like SQL's `SELECT a, b`)
6. **Chain** `.sort()`, `.limit()`, `.skip()` for pagination and ordering
