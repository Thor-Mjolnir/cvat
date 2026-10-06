# Annotation Analytics Plan

## Implementation Approach
1. **Backend Endpoint**: Create a new Django app `test`. Implement a DRF endpoint at `/api/test/tasks/<id>/annotation-counts`. The exact CVAT annotation relationships will be verified first. Database-side aggregation will be selected based on correctness and simplicity to avoid N+1 query problems and loading excessive Python objects.
2. **Security**: Reuse CVAT's existing permissions architecture (`PolicyEnforcer` and DRF `IsAuthenticated`) to refuse unauthenticated users and unauthorized task access.
3. **Frontend Integration**: Add a route `/tasks/:tid/annotation-analytics` in `cvat-ui/src/components/cvat-app.tsx`. Add a menu item in `actions-menu-items.tsx` to navigate there from the Task page.
4. **UI/Visualization**: Build `AnnotationAnalyticsPage` using React and `react-chartjs-2` (which is already in `cvat-ui/package.json`). Handle Loading, Empty (no annotations), and Error states gracefully.

## Order of Work
1. Create `test` Django app, register it in `settings`, and implement the API endpoint.
2. Manually verify endpoint security and data correctness against the DB.
3. Scaffold the React page, route, and menu item.
4. Implement data fetching and UI states (loading, empty, error).
5. Implement the Chart.js visualization.
6. Verify requirements 1-4 and 5 (auth).
7. Perform measurements for Objective.
8. (Time permitting) Implement additional grouping/filtering (e.g. by Job or Shape Type).
9. (Time permitting) Implement WebSocket live updates.
10. Finalize Decision Record in Plan.md and prepare Loom script.

## Approximate Time Allocation (8 Hours)
- Setup & Discovery: 1.5 hr
- Backend API & Permissions: 1.5 hr
- Frontend Integration & Graph: 2.0 hr
- Testing & Edge Cases: 1.0 hr
- Measurement & Documentation: 0.5 hr
- Advanced requirements (Filter/WS) & Polish: 1.0 hr
- Loom Recording & Submission prep: 0.5 hr

## Architecture Areas to Investigate
- Exact mechanism of CVAT's object-level permissions for tasks (`PolicyEnforcer` rules).
- Best way to aggregate counts for all types of annotations within a single Task efficiently.

## Deferred/Skipped
- WebSockets (Req 8-9) will be deferred until Requirements 1-7 are fully stable and proven.

## Risks
- Overcomplicating the DB query due to polymorphic annotations in CVAT's DB. I will ensure it remains a fast query or use straightforward multiple queries if ORM is too complex, as long as it avoids loading all instances into memory.

## Testing Strategy
- Manual testing against a task with the public COCO 2017 validation dataset.
- Verifying unauthenticated API calls (HTTP 401).
- Verifying cross-user unauthorized API calls (HTTP 403).
- React state verification for empty tasks and broken endpoints.

## Measurement Strategy
- Measure the median API response time of the annotation-counts endpoint over 5 runs under controlled local conditions, to ensure database queries scale well.
