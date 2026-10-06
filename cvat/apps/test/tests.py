from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from cvat.apps.engine.models import (
    Job,
    Label,
    LabeledImage,
    LabeledShape,
    Segment,
    ShapeType,
    Task,
)


class AnnotationAnalyticsTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="password",
        )
        self.unauthorized_user = get_user_model().objects.create_user(
            username="hacker_user",
            password="password",
        )

        self.task = Task.objects.create(
            name="Test Task",
            owner=self.user,
        )

        self.label1 = Label.objects.create(
            name="Car",
            task=self.task,
        )
        self.label2 = Label.objects.create(
            name="Person",
            task=self.task,
        )

        self.segment = Segment.objects.create(
            task=self.task,
            start_frame=0,
            stop_frame=10,
        )
        self.job = Job.objects.create(segment=self.segment)

        # Create shapes:
        # Car = 2
        # Person = 1
        LabeledShape.objects.create(
            job=self.job,
            label=self.label1,
            frame=0,
            type=ShapeType.RECTANGLE,
        )
        LabeledShape.objects.create(
            job=self.job,
            label=self.label1,
            frame=1,
            type=ShapeType.RECTANGLE,
        )
        LabeledShape.objects.create(
            job=self.job,
            label=self.label2,
            frame=0,
            type=ShapeType.RECTANGLE,
        )

        # LabeledImage represents tag annotations.
        # Car = 3 tags
        # Person = 0 tags
        #
        # Having both shapes and tags for Car also verifies that
        # distinct=True prevents JOIN multiplication.
        LabeledImage.objects.create(
            job=self.job,
            label=self.label1,
            frame=0,
        )
        LabeledImage.objects.create(
            job=self.job,
            label=self.label1,
            frame=1,
        )
        LabeledImage.objects.create(
            job=self.job,
            label=self.label1,
            frame=2,
        )

    def test_annotation_counts(self):
        self.client.force_authenticate(user=self.user)

        url = f"/api/test/tasks/{self.task.id}/annotation-counts"
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        self.assertEqual(len(data), 2)

        data.sort(key=lambda item: item["label_name"])

        # Car = 2 shapes + 3 tags = 5
        self.assertEqual(data[0]["label_name"], "Car")
        self.assertEqual(data[0]["count"], 5)

        # Person = 1 shape
        self.assertEqual(data[1]["label_name"], "Person")
        self.assertEqual(data[1]["count"], 1)

    def test_unauthenticated(self):
        url = f"/api/test/tasks/{self.task.id}/annotation-counts"

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthorized_user_cannot_access_task(self):
        self.client.force_authenticate(
            user=self.unauthorized_user,
        )

        url = f"/api/test/tasks/{self.task.id}/annotation-counts"

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_filter_by_shape(self):
        self.client.force_authenticate(user=self.user)

        url = (
            f"/api/test/tasks/{self.task.id}/"
            "annotation-counts?type=shape"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = {
            item["label_name"]: item["count"]
            for item in response.json()
        }

        self.assertEqual(data["Car"], 2)
        self.assertEqual(data["Person"], 1)

    def test_filter_by_tag(self):
        self.client.force_authenticate(user=self.user)

        url = (
            f"/api/test/tasks/{self.task.id}/"
            "annotation-counts?type=tag"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = {
            item["label_name"]: item["count"]
            for item in response.json()
        }

        self.assertEqual(data["Car"], 3)
        self.assertEqual(data["Person"], 0)

    def test_invalid_annotation_type(self):
        self.client.force_authenticate(user=self.user)

        url = (
            f"/api/test/tasks/{self.task.id}/"
            "annotation-counts?type=invalid"
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("type", response.json())