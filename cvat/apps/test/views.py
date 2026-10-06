from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import Task
from cvat.apps.engine.permissions import TaskPermission
from cvat.apps.iam.permissions import get_iam_context


class AnnotationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        # Fetch task
        task = get_object_or_404(Task, pk=task_id)

        # Enforce CVAT's existing object-level permissions
        iam_context = get_iam_context(request, task)
        perm = TaskPermission.create_scope_view(request, task, iam_context)
        if not perm.check_access().allow:
            raise PermissionDenied("You do not have permission to view this task.")

        # Optional annotation type filter
        annotation_type = request.query_params.get("type", "all").lower()

        valid_types = {"all", "shape", "track", "tag", "interval"}
        if annotation_type not in valid_types:
            raise ValidationError(
                {
                    "type": (
                        "Invalid annotation type. "
                        "Use all, shape, track, tag, or interval."
                    )
                }
            )

        # Aggregate annotation counts per label from the database.
        # distinct=True prevents multiplication caused by joining multiple
        # annotation relationships in the same query.
        labels = task.get_labels().annotate(
            tags_count=Count(
                "labeledimage",
                distinct=True,
                filter=Q(labeledimage__job__segment__task_id=task_id),
            ),
            shapes_count=Count(
                "labeledshape",
                distinct=True,
                filter=Q(labeledshape__job__segment__task_id=task_id),
            ),
            tracks_count=Count(
                "labeledtrack",
                distinct=True,
                filter=Q(labeledtrack__job__segment__task_id=task_id),
            ),
            intervals_count=Count(
                "labeledinterval",
                distinct=True,
                filter=Q(labeledinterval__job__segment__task_id=task_id),
            ),
        ).values(
            "id",
            "name",
            "tags_count",
            "shapes_count",
            "tracks_count",
            "intervals_count",
        )

        count_field = {
            "shape": "shapes_count",
            "track": "tracks_count",
            "tag": "tags_count",
            "interval": "intervals_count",
        }

        data = []

        for label in labels:
            if annotation_type == "all":
                count = (
                    label["tags_count"]
                    + label["shapes_count"]
                    + label["tracks_count"]
                    + label["intervals_count"]
                )
            else:
                count = label[count_field[annotation_type]]

            data.append(
                {
                    "label_id": label["id"],
                    "label_name": label["name"],
                    "count": count,
                }
            )

        data.sort(key=lambda item: item["label_name"])

        return Response(data)