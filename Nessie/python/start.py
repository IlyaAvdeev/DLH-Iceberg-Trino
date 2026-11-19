import os
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, LongType, TimestamptzType
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform
from pyiceberg.exceptions import NamespaceAlreadyExistsError
import pyarrow as pa
from datetime import datetime, timezone

catalog = load_catalog(
    "nessie",
    **{
        "type": "rest",
        "uri": "http://nessie:19120/iceberg/main",
        "s3.endpoint": "http://minio:9000",
        "s3.access-key-id": os.getenv("AWS_ACCESS_KEY_ID", "minioadmin"),
        "s3.secret-access-key": os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin"),
        "s3.path-style-access": "true",
        "s3.region": "us-east-1",
    },
)

try:
    catalog.create_namespace("analytics")
    print("Namespace 'analytics' created")
except NamespaceAlreadyExistsError:
    print("Namespace 'analytics' already exists")

try:
    schema = Schema(
        NestedField(field_id=1, name="event_id", field_type=LongType(), required=False),
        NestedField(field_id=2, name="event_type", field_type=StringType(), required=False),
        NestedField(field_id=3, name="timestamp", field_type=TimestamptzType(), required=False),
    )
    partition_spec = PartitionSpec(
        spec_id=0,
        fields=[
            PartitionField(
                source_id=3,
                field_id=1000,
                transform=DayTransform(),
                name="timestamp_day",
            )
        ],
    )
    catalog.create_table("analytics.events", schema=schema, partition_spec=partition_spec)
    print("Table 'analytics.events' created")
except Exception as e:
    if "already exists" in str(e).lower():
        print("Table 'analytics.events' already exists")
    else:
        raise

table = catalog.load_table("analytics.events")

data = pa.table({
    "event_id": pa.array([1, 2], type=pa.int64()),
    "event_type": pa.array(["click", "view"], type=pa.string()),
    "timestamp": pa.array(
        [
            datetime(2026, 7, 24, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 7, 24, 10, 1, tzinfo=timezone.utc),
        ],
        type=pa.timestamp("us", tz="UTC"),
    ),
})
table.append(data)
print("Data appended")

result = table.scan().to_arrow()
print(f"Rows: {result.num_rows}")
print(f"event_id: {result['event_id'].to_pylist()}")
print(f"event_type: {result['event_type'].to_pylist()}")
print(f"timestamp: {result['timestamp'].to_pylist()}")
