https://bigdataschool.ru/blog/events/3-trino-iceberg-s3/

https://habr.com/ru/companies/selectel/articles/1022920/
https://habr.com/ru/companies/selectel/articles/1071768/
https://habr.com/ru/companies/selectel/articles/1082852/

Залогиниться в ghcr.io

```sh
echo "PAT_с_грануляцией_для_скачивания_публичных_репозиториев" | docker login ghcr.io -u USERNAME --password-stdin
```

```sh
docker exec -it nessie-trino-1 trino --catalog iceberg --schema analytics
```

```sql
SHOW CATALOGS;

SELECT * FROM iceberg.analytics.events;

INSERT INTO iceberg.analytics.events VALUES (3, 'click', TIMESTAMP '2026-09-06 16:10:00 UTC');

SELECT snapshot_id, committed_at, operation, summary FROM iceberg.analytics."events$snapshots";

SELECT * FROM iceberg.analytics.events FOR VERSION AS OF 6335359114163657760;

SELECT * FROM iceberg.analytics.events FOR TIMESTAMP AS OF TIMESTAMP '2026-08-15 00:00:00';
```