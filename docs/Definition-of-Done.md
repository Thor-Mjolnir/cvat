# Definition of Done

| Done | Criterion | Evidence |
|---|---|---|
| [x] | Documents (Plan, Objectives, DoD) committed before feature code | Documentation commit `f353f111b` precedes backend feature commit `0304c0037` |
| [x] | Req 1: Backend API returns annotation counts grouped by class/label | `/api/test/tasks/<id>/annotation-counts`; verified by automated tests and against the 500-image COCO task |
| [x] | Req 2: Frontend integration calls the backend endpoint | `AnnotationAnalyticsPage` requests `/api/test/tasks/${tid}/annotation-counts` |
| [x] | Req 3: Counts shown as a graph | Chart.js / `react-chartjs-2` bar chart manually verified with imported COCO data |
| [x] | Req 4: Cleanly handles empty data state | Empty task manually verified; page displayed `No annotation data found for this task.` |
| [x] | Req 4: Cleanly handles failed request state | Invalid task `99999` manually verified; page displayed `Failed to load analytics` |
| [x] | Req 5: Endpoint refuses unauthenticated requests | Direct HTTP request returned `401 Unauthorized` |
| [x] | Req 5: Endpoint refuses unauthorized task access | Authenticated user without Task 1 access returned `403 Forbidden` with `You do not have permission to view this task.` |
| [x] | Req 6: Objective MO-1 measured with 5 runs and median/spread recorded | Median 129.984 ms; min 126.106 ms; max 134.093 ms; spread 7.987 ms; target <= 250 ms |
| [x] | Req 7: Additional filter/grouping implemented | Optional `type=shape`, `track`, `tag`, `interval`, or `all`; real COCO shape-filter request verified; invalid type returns HTTP 400 |
| [ ] | Req 8: WebSocket live updates as annotations change | Not implemented; see `Plan.md` decision record |
| [ ] | Req 9: Page recovers state when connection drops | Not implemented because WebSocket live updates were not implemented |
| [x] | Req 10: Decision record added to Plan.md | Database aggregation, authorization, filter, and WebSocket decisions documented |
| [x] | Unfinished work declared | Requirements 8-9 explicitly documented as unfinished |
| [x] | Incremental logical Git commits created | Documentation, backend API, frontend page, and filter/tests were committed separately |
| [x] | Machine specs, dataset size, and starting CVAT commit SHA recorded | See `Objectives.md` |
| [ ] | Loom recording <= 5 minutes covering K1-K4 completed | Pending final recording |

## Automated Test Evidence

The backend annotation analytics test suite completed successfully:

```text
Found 6 test(s).
......
Ran 6 tests in 5.329s

OK
System check identified no issues (0 silenced).
```

The automated suite covers:

- aggregate annotation counts
- unauthenticated access
- authenticated but unauthorized task access
- shape filtering
- tag filtering
- invalid annotation-type filtering

## Manual API Evidence

### Unauthenticated access

```text
HTTP/1.1 401 Unauthorized
```

### Authenticated but unauthorized access

```text
HTTP/1.1 403 Forbidden

{"detail":"You do not have permission to view this task."}
```

### Invalid annotation-type filter

```text
HTTP/1.1 400 Bad Request

{"type":"Invalid annotation type. Use all, shape, track, tag, or interval."}
```

### Real COCO filter verification

An authenticated request to:

```text
/api/test/tasks/1/annotation-counts?type=shape
```

successfully returned per-label shape counts for the imported COCO task, including zero-count labels.

## UI Verification

The following states were manually verified:

- Analytics page loads data from the backend.
- Imported COCO annotation counts render as a bar graph.
- A task with no annotations displays `No annotation data found for this task.`
- A failed request using task ID `99999` displays `Failed to load analytics`.

## Performance Evidence

The performance target was a median response time of at most 250 ms.

Measured requests:

```text
Run 1: 0.129984 seconds
Run 2: 0.134093 seconds
Run 3: 0.126106 seconds
Run 4: 0.127199 seconds
Run 5: 0.131697 seconds
```

Results:

- Median: 129.984 ms
- Minimum: 126.106 ms
- Maximum: 134.093 ms
- Spread: 7.987 ms
- Target: <= 250 ms
- Outcome: PASS

Full measurement conditions and environment information are recorded in `Objectives.md`.

## Unfinished Work

Requirements 8 and 9 are intentionally unfinished.

Repository investigation found the Python `websockets` dependency and a webpack development WebSocket URL, but no existing application-level WebSocket consumer or frontend realtime implementation in the inspected CVAT paths.

Implementing a new authenticated WebSocket architecture late in the assessment was judged higher risk than preserving the correctness and stability of Requirements 1-7.

The analytics page therefore currently fetches its analytics when the page is loaded rather than receiving annotation changes live.

The rationale and trade-offs are recorded in the decision record in `Plan.md`.

## Recording

The final Loom recording is still pending.

It will demonstrate the feature and cover the required K1-K4 questions before this item is marked complete.