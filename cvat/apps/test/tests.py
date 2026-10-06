from rest_framework.test import APITestCase
from rest_framework import status
from cvat.apps.engine.models import Task, Label, Job, Segment, LabeledShape, LabeledImage, ShapeType
from django.contrib.auth import get_user_model

class AnnotationAnalyticsTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test_user', password='password')
        self.unauthorized_user = get_user_model().objects.create_user(username='hacker_user', password='password')
        self.task = Task.objects.create(name='Test Task', owner=self.user)
        self.label1 = Label.objects.create(name='Car', task=self.task)
        self.label2 = Label.objects.create(name='Person', task=self.task)
        
        self.segment = Segment.objects.create(task=self.task, start_frame=0, stop_frame=10)
        self.job = Job.objects.create(segment=self.segment)
        
        # Create shapes (2 for Car, 1 for Person)
        LabeledShape.objects.create(job=self.job, label=self.label1, frame=0, type=ShapeType.RECTANGLE)
        LabeledShape.objects.create(job=self.job, label=self.label1, frame=1, type=ShapeType.RECTANGLE)
        LabeledShape.objects.create(job=self.job, label=self.label2, frame=0, type=ShapeType.RECTANGLE)

        # Create images (3 for Car, 0 for Person) - tests JOIN multiplication!
        LabeledImage.objects.create(job=self.job, label=self.label1, frame=0)
        LabeledImage.objects.create(job=self.job, label=self.label1, frame=1)
        LabeledImage.objects.create(job=self.job, label=self.label1, frame=2)

    def test_annotation_counts(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/test/tasks/{self.task.id}/annotation-counts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 2)
        
        data.sort(key=lambda x: x['label_name'])
        
        self.assertEqual(data[0]['label_name'], 'Car')
        # 2 shapes + 3 images = 5. If JOIN multiplication occurs without distinct=True, it will be much larger.
        self.assertEqual(data[0]['count'], 5)
        
        self.assertEqual(data[1]['label_name'], 'Person')
        self.assertEqual(data[1]['count'], 1)

    def test_unauthenticated(self):
        url = f'/api/test/tasks/{self.task.id}/annotation-counts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_access_task(self):
        # A normal authenticated user who does not own the task should get 403 Forbidden
        self.client.force_authenticate(user=self.unauthorized_user)
        url = f'/api/test/tasks/{self.task.id}/annotation-counts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

