# Objectives & Environment

## Environment Information

- **OS**: Windows with Docker Desktop / WSL2
- **Docker Version**: 29.8.2
- **Docker Compose Version**: v5.5.1
- **CPU**: 8 CPUs
- **RAM available to Docker**: 7.623 GiB
- **Starting CVAT SHA**: `8d7ae755c5b8de82e8711756b35c0207655ef1ae`

## Dataset

The public COCO 2017 validation dataset was used for realistic testing.

Because the local Docker environment had approximately 7.6 GiB of available memory, a 500-image subset of the validation dataset was used. A matching subset of `instances_val2017.json` was generated for those images.

Dataset conditions:

- **Images loaded into the CVAT task**: 500
- **COCO categories / CVAT labels**: 80
- **Source COCO annotation objects in subset JSON**: 3,541
- **Stored CVAT `LabeledShape` rows after import**: 3,953
- **Import configuration**: masks converted to polygons

The source COCO annotation-object count and the stored CVAT shape count are reported separately because the analytics endpoint measures the annotations as represented in CVAT's database after import.

## Measurable Objective MO-1

| Field | Entry |
|---|---|
| What is measured | Response time of the new annotation-counts endpoint |
| Endpoint | `/api/test/tasks/1/annotation-counts` |
| Method | Authenticated `curl` using `time_total` |
| Warm-up | 1 request excluded from the measured results |
| Measured runs | 5 warm requests |
| Target | Median of the 5 measured requests <= 250 ms |
| Conditions | Local Docker stack, 500-image COCO validation task, 80 labels, no intentionally active import/annotation operation |
| Excluded | Initial warm-up/cold-start request |

## Target Justification

A 250 ms median target provides a practical upper bound for a local warmed database aggregation request.

The measurement includes HTTP routing, Django middleware, CVAT permission checking, ORM/database execution, DRF serialization, and response handling.

The target was defined before measurement and was intended to verify that the implementation remained responsive without adding caching solely to satisfy the benchmark.

## Measurement Method

One authenticated warm-up request was executed first:

```text
Warm-up: 0.149071 seconds
```

The following five requests were then measured:

```text
Run 1: 0.129984 seconds
Run 2: 0.134093 seconds
Run 3: 0.126106 seconds
Run 4: 0.127199 seconds
Run 5: 0.131697 seconds
```

## Results

- **Median**: 129.984 ms
- **Minimum**: 126.106 ms
- **Maximum**: 134.093 ms
- **Spread (maximum - minimum)**: 7.987 ms
- **Target**: <= 250 ms median
- **Outcome**: PASS

The measured median was approximately 52% of the 250 ms target limit.

## Additional Verification

The backend test suite contained six tests and completed successfully:

```text
Found 6 test(s).
......
Ran 6 tests in 5.329s

OK
System check identified no issues (0 silenced).
```

The tests cover:

- annotation counts across annotation relationships
- unauthenticated access
- authenticated but unauthorized task access
- shape filtering
- tag filtering
- invalid annotation-type filtering

Manual HTTP security verification also produced:

```text
Unauthenticated request:
HTTP/1.1 401 Unauthorized
```

and:

```text
Authenticated user without permission:
HTTP/1.1 403 Forbidden

{"detail":"You do not have permission to view this task."}
```

The Requirement 7 validation check produced:

```text
HTTP/1.1 400 Bad Request

{"type":"Invalid annotation type. Use all, shape, track, tag, or interval."}
```

A real request using `type=shape` against the imported COCO task also returned per-label shape counts successfully.