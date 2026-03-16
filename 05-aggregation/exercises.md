# Aggregation Exercises

10 challenges using `sample_mflix.movies`. Progressive difficulty.

---

## Exercise 1: Count by Genre
Count how many movies belong to each genre. Sort by count descending. Show top 5.

<details>
<summary>💡 Hint</summary>
Use `$unwind` on genres, then `$group` with `$sum: 1`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$unwind": "$genres"},
    {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}},
    {"$limit": 5}
]
```
</details>

---

## Exercise 2: Average Rating per Year
Find the average IMDb rating for each year (2000–2020). Which year had the highest average?

<details>
<summary>💡 Hint</summary>
`$match` for year range, `$group` by year with `$avg`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"year": {"$gte": 2000, "$lte": 2020}, "imdb.rating": {"$type": "double"}}},
    {"$group": {"_id": "$year", "avg_rating": {"$avg": "$imdb.rating"}, "count": {"$sum": 1}}},
    {"$sort": {"avg_rating": -1}},
    {"$limit": 5}
]
```
</details>

---

## Exercise 3: Top 5 Cast Members
Find the 5 actors who appear in the most movies. Show their name and movie count.

<details>
<summary>💡 Hint</summary>
`$unwind` the cast array, then `$group` and `$sort`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$unwind": "$cast"},
    {"$group": {"_id": "$cast", "movie_count": {"$sum": 1}}},
    {"$sort": {"movie_count": -1}},
    {"$limit": 5}
]
```
</details>

---

## Exercise 4: Movies Per Decade
Group movies by decade (1920s, 1930s, ..., 2010s). Show the count and average rating for each decade.

<details>
<summary>💡 Hint</summary>
Compute decade with `$multiply` and `$floor`: `floor(year / 10) * 10`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"year": {"$type": "int"}, "imdb.rating": {"$type": "double"}}},
    {"$group": {
        "_id": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]},
        "count": {"$sum": 1},
        "avg_rating": {"$avg": "$imdb.rating"}
    }},
    {"$sort": {"_id": 1}}
]
```
</details>

---

## Exercise 5: Runtime Distribution
Use `$bucket` to group movies into runtime ranges: 0-60, 60-90, 90-120, 120-150, 150-180, 180+. Show count per bucket.

<details>
<summary>💡 Hint</summary>
Use `$bucket` with `groupBy: "$runtime"` and `boundaries`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"runtime": {"$exists": True, "$type": "int"}}},
    {"$bucket": {
        "groupBy": "$runtime",
        "boundaries": [0, 60, 90, 120, 150, 180, 500],
        "default": "other",
        "output": {"count": {"$sum": 1}}
    }}
]
```
</details>

---

## Exercise 6: Multi-Genre Analysis with $facet
In a single query, get: (a) top 5 genres by count, (b) top 5 countries by count, (c) average rating overall.

<details>
<summary>💡 Hint</summary>
`$facet` with three named pipelines.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$facet": {
        "top_genres": [
            {"$unwind": "$genres"},
            {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ],
        "top_countries": [
            {"$unwind": "$countries"},
            {"$group": {"_id": "$countries", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ],
        "overall_stats": [
            {"$match": {"imdb.rating": {"$type": "double"}}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$imdb.rating"}, "total": {"$sum": 1}}}
        ]
    }}
]
```
</details>

---

## Exercise 7: Director + Actor Pairs
Find the most common director-actor pairs (which director works with which actor most often?).

<details>
<summary>💡 Hint</summary>
`$unwind` both directors and cast, then `$group` by the pair.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"directors": {"$exists": True}, "cast": {"$exists": True}}},
    {"$unwind": "$directors"},
    {"$unwind": "$cast"},
    {"$group": {
        "_id": {"director": "$directors", "actor": "$cast"},
        "collaborations": {"$sum": 1}
    }},
    {"$sort": {"collaborations": -1}},
    {"$limit": 10}
]
```
</details>

---

## Exercise 8: Yearly Trend
For each year from 2000–2020, calculate the number of movies AND the average runtime. Show the trend.

<details>
<summary>💡 Hint</summary>
`$group` by year with both `$sum` and `$avg` accumulators.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"year": {"$gte": 2000, "$lte": 2020}, "runtime": {"$type": "int"}}},
    {"$group": {
        "_id": "$year",
        "movie_count": {"$sum": 1},
        "avg_runtime": {"$avg": "$runtime"}
    }},
    {"$sort": {"_id": 1}}
]
```
</details>

---

## Exercise 9: $lookup with Comments
Find the 5 movies with the most comments. Show the movie title and comment count.

<details>
<summary>💡 Hint</summary>
`$lookup` from comments, `$addFields` to count, `$sort` and `$limit`.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$lookup": {
        "from": "comments",
        "localField": "_id",
        "foreignField": "movie_id",
        "as": "comments"
    }},
    {"$addFields": {"comment_count": {"$size": "$comments"}}},
    {"$sort": {"comment_count": -1}},
    {"$limit": 5},
    {"$project": {"title": 1, "comment_count": 1, "_id": 0}}
]
```
</details>

---

## Exercise 10: Language Diversity by Country
For each country, find how many different languages are used in their movies. Show countries with the most language diversity.

<details>
<summary>💡 Hint</summary>
`$unwind` countries, `$unwind` languages, `$group` with `$addToSet`, then compute size.
</details>

<details>
<summary>✅ Solution</summary>

```python
pipeline = [
    {"$match": {"countries": {"$exists": True}, "languages": {"$exists": True}}},
    {"$unwind": "$countries"},
    {"$unwind": "$languages"},
    {"$group": {
        "_id": "$countries",
        "unique_languages": {"$addToSet": "$languages"},
        "movie_count": {"$sum": 1}
    }},
    {"$addFields": {"language_count": {"$size": "$unique_languages"}}},
    {"$sort": {"language_count": -1}},
    {"$limit": 10},
    {"$project": {"_id": 1, "language_count": 1, "movie_count": 1}}
]
```
</details>

---

## 📌 Key Takeaways

1. **`$unwind` before `$group`** when you need to aggregate over array elements
2. **`$facet`** lets you run multiple independent aggregations in one round trip
3. **`$bucket`** is great for histograms and distribution analysis
4. **`$lookup`** should be used sparingly — it's expensive on large collections
5. Always `$match` as early as possible to reduce the data flowing through the pipeline
