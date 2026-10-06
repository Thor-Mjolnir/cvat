# Objectives & Environment

## Environment Information
- **OS**: Windows (Docker Desktop/WSL2)
- **Docker Version**: 29.8.2
- **CPU**: 8 CPUs
- **RAM**: 7.623 GiB Docker memory
- **Starting CVAT SHA**: 8d7ae755c5b8de82e8711756b35c0207655ef1ae
- **Dataset Image Count**: [Pending until import]

## Objectives

| ID | Field | Entry |
|----|-------|-------|
| MO-1 | What is measured | Time for the new annotation-counts endpoint to return the response. |
| | How | Authenticated `curl` extracting `time_total`. 1 warm-up request, followed by 5 measured warm requests. |
| | Target | Median of 5 runs at or below 250 ms. |
| | Conditions | Local Docker stack, public COCO 2017 validation dataset loaded in a task, no other active operations. |
| | Not included | First cold-start run (handled by the warm-up request). |

*Justification*: A 250ms target for a local, warmed-up database aggregation request provides a reasonable bound for an efficient query using database-side grouping, accounting for Django middleware and DRF serialization overhead, without requiring overly complex caching logic.
