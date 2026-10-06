# Annotation Analytics Plan

## Implementation Approach

1. **Backend Endpoint**: Create a new Django app `test`. Implement a DRF endpoint at `/api/test/tasks/<id>/annotation-counts`. The exact CVAT annotation relationships will be verified first. Database-side aggregation will be selected based on correctness and simplicity to avoid N+1 query problems and loading excessive Python objects.

2. **Security**: Reuse CVAT's existing permissions architecture and DRF `IsAuthenticated` to refuse unauthenticated users and unauthorized task access.

3. **Frontend Integration**: Add a route `/tasks/:tid/annotation-analytics` in `cvat-ui/src/components/cvat-app.tsx`. Add a menu item in `actions-menu-items.tsx` to navigate there from the Task page.

4. **UI / Visualization**: Build `AnnotationAnalyticsPage` using React and `react-chartjs-2`, which is already available in the CVAT UI dependencies. Handle loading, empty-data, and failed-request states gracefully.

## Order of Work

1. Create the `test` Django app, register it in settings, and implement the API endpoint.
2. Verify endpoint security and data correctness against the database.
3. Scaffold the React page, route, and task menu item.
4. Implement data fetching and loading, empty, and error states.
5. Implement the Chart.js visualization.
6. Verify Requirements 1-5, including authentication and authorization.
7. Measure the API against the performance objective.
8. If time permits, implement an additional useful filter/grouping.
9. If time permits, investigate and implement WebSocket live updates and reconnection.
10. Finalize the decision record, Definition of Done, and recording preparation.

## Approximate Time Allocation

- Setup and discovery: 1.5 hours
- Backend API and permissions: 1.5 hours
- Frontend integration and graph: 2 hours
- Testing and edge cases: 1 hour
- Measurement and documentation: 0.5 hour
- Advanced requirements and polish: 1 hour
- Recording and submission preparation: 0.5 hour

## Architecture Areas to Investigate

- CVAT's existing object-level permission mechanism for tasks.
- CVAT's annotation database relationships.
- Efficient aggregation across the different annotation models without loading all annotations into Python.
- Existing realtime or WebSocket infrastructure that could be reused for Requirements 8-9.

## Risks

The main backend risk is that CVAT stores several annotation representations separately. Combining these relationships in one ORM aggregation can produce row multiplication when multiple one-to-many relationships are joined.

The implementation therefore needs to preserve correctness while avoiding N+1 queries or loading every annotation into application memory.

Another risk is introducing a new realtime architecture solely for Requirements 8-9 if CVAT does not already provide an application-level WebSocket mechanism that can be safely extended.

## Testing Strategy

- Automated API tests for annotation counts.
- Automated test for unauthenticated access.
- Automated test for authenticated but unauthorized task access.
- Automated tests for the additional annotation-type filter.
- Manual testing against a task containing a 500-image subset of the public COCO 2017 validation dataset.
- Manual verification of the empty-data UI.
- Manual verification of the failed-request UI.
- Direct HTTP verification of 401, 403, and invalid-filter responses.

## Measurement Strategy

Measure the response time of the annotation-counts endpoint using authenticated `curl` requests.

Use one warm-up request followed by five measured requests. Report the raw values, median, minimum, maximum, and spread.

The target defined before measurement is a median response time of at most 250 ms under the documented local conditions.

---

# Implementation Outcome

Requirements 1-7 were completed and verified.

The backend endpoint returns annotation counts grouped by CVAT label using database-side aggregation. The frontend calls this endpoint and displays the results using a Chart.js bar chart.

The UI includes explicit loading, empty-data, and failed-request states. The empty-data state and failed-request state were manually verified.

Authentication and authorization were also verified. An unauthenticated request returned HTTP 401, while an authenticated user without access to the task received HTTP 403.

The performance objective was measured using one warm-up request and five measured requests. The measured median was 129.984 ms against the pre-defined target of at most 250 ms.

Requirement 7 was implemented as an optional annotation-type filter. The API accepts:

- `type=all`
- `type=shape`
- `type=track`
- `type=tag`
- `type=interval`

Omitting `type` preserves the original behavior and counts all supported annotation types.

Requirements 8 and 9 were not implemented. Repository investigation found the Python `websockets` dependency and a webpack development WebSocket URL, but no existing application-level WebSocket consumer or frontend realtime implementation in the inspected CVAT paths.

Adding a new WebSocket framework or standalone realtime service late in the assessment would introduce authentication, task authorization, routing, event publication, deployment, frontend lifecycle, and reconnection complexity. I chose to preserve the correctness and stability of Requirements 1-7 rather than introduce a partially working realtime implementation.

## Decision Record

### Decision 1: Database-Side Aggregation

**Chosen approach**

Use Django ORM aggregation over the task's labels with filtered `Count(..., distinct=True)` expressions for CVAT's annotation relationships:

- `LabeledImage`
- `LabeledShape`
- `LabeledTrack`
- `LabeledInterval`

The API then combines the relevant counts for each label.

**Rejected approach**

Fetch every annotation into Python and count annotations there, or issue separate queries for every individual label.

**Reason**

Database-side aggregation avoids loading all annotation instances into application memory and avoids an N+1 query pattern.

`distinct=True` is important because joining multiple one-to-many annotation relationships in the same query can otherwise multiply rows and produce incorrect counts.

**Cost / what I would reconsider**

Multiple `DISTINCT` joins may create larger intermediate database results for very large tasks.

If performance degraded at significantly larger scale, I would investigate pre-aggregating the individual annotation tables with subqueries or separate grouped queries and combining those results.

### Decision 2: Reuse CVAT Authorization

**Chosen approach**

Use DRF `IsAuthenticated` together with CVAT's existing `TaskPermission.create_scope_view(...)` permission flow.

**Rejected approach**

Implement custom authorization based only on fields such as task owner or assignee.

**Reason**

CVAT already defines task-access rules. Reimplementing those rules specifically for this endpoint could cause the analytics endpoint to behave differently from the rest of CVAT.

**Cost**

The endpoint is coupled to CVAT's IAM and task-permission infrastructure instead of being a completely standalone Django endpoint.

### Decision 3: Annotation-Type Filter

**Chosen approach**

Use annotation type as the additional Requirement 7 filter.

Supported values are `all`, `shape`, `track`, `tag`, and `interval`.

**Reason**

CVAT can represent annotations in different forms. Filtering by annotation type allows users to inspect the class distribution for a particular annotation representation while keeping the original all-annotations view available.

Invalid filter values return HTTP 400 rather than silently falling back to another behavior.

### Decision 4: WebSocket Requirements

**Chosen approach**

Stop after completing and validating Requirements 1-7 and explicitly document Requirements 8-9 as unfinished.

**Rejected approach**

Introduce Django Channels or a separate WebSocket service during the remaining assessment time.

**Reason**

Repository investigation did not identify an existing application-level WebSocket implementation that could be extended with a small isolated change.

A correct implementation would require authenticated and task-authorized subscriptions, annotation-change event publication, proxy routing, frontend connection lifecycle handling, and reconnection/state recovery.

**Cost**

The analytics page does not automatically receive annotation changes while it remains open. It fetches current analytics data when the page is loaded.

## Deferred / Unfinished

- **Requirement 8**: WebSocket live annotation updates — not implemented.
- **Requirement 9**: WebSocket reconnection and state recovery — not implemented because Requirement 8 was not implemented.

These items are intentionally declared unfinished rather than represented as complete without a reliable implementation.