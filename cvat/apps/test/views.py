from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from cvat.apps.engine.models import Task, Label
from cvat.apps.iam.permissions import get_iam_context
from cvat.apps.engine.permissions import TaskPermission

class AnnotationAnalyticsView(APIView):
    # Use existing authentication and authorization logic from DRF & CVAT
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        # 1. Fetch Task
        task = get_object_or_404(Task, pk=task_id)

        # 2. Enforce CVAT's object-level permissions (refuse unauthorized access)
        iam_context = get_iam_context(request, task)
        perm = TaskPermission.create_scope_view(request, task, iam_context)
        if not perm.check_access().allow:
            raise PermissionDenied("You do not have permission to view this task.")

        # 3. Aggregate Annotation Counts per Label from the Database
        # A Task has Labels. Each Label can be used by LabeledImage, LabeledShape, etc.
        # We want to restrict the counts to ONLY annotations within this specific task
        # (in case the label is a project-level label).
        labels = task.get_labels().annotate(
            images_count=Count('labeledimage', distinct=True, filter=Q(labeledimage__job__segment__task_id=task_id)),
            shapes_count=Count('labeledshape', distinct=True, filter=Q(labeledshape__job__segment__task_id=task_id)),
            tracks_count=Count('labeledtrack', distinct=True, filter=Q(labeledtrack__job__segment__task_id=task_id)),
            intervals_count=Count('labeledinterval', distinct=True, filter=Q(labeledinterval__job__segment__task_id=task_id))
        ).values('id', 'name', 'images_count', 'shapes_count', 'tracks_count', 'intervals_count')

        # 4. Build Response
        data = []
        for label in labels:
            total = (
                label['images_count'] + 
                label['shapes_count'] + 
                label['tracks_count'] + 
                label['intervals_count']
            )
            data.append({
                'label_id': label['id'],
                'label_name': label['name'],
                'count': total
            })

        # Sort the data by label name for consistent UI rendering
        data.sort(key=lambda x: x['label_name'])
        
        return Response(data)
