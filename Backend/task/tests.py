from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Todo


class TaskAPITests(APITestCase):

    def setUp(self):
        # 1. Create a test user and authenticate the test client
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.client.force_authenticate(user=self.user)

        # 2. Create an initial sample task
        self.todo = Todo.objects.create(
            user=self.user,
            title='Sample Task',
            description='Testing initial task',
            is_completed=False
        )

        # 3. Generate URLs using the basename='task' from the router
        self.list_url = reverse('task-list')
        self.detail_url = reverse('task-detail', kwargs={'pk': self.todo.pk})

    def test_get_task(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_task(self):
        data = {
            'title': 'New Automated Task',
            'description': 'Created via APITestCase',
            'due_date': '2026-11-20T18:00:00Z'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 2)
        self.assertEqual(Todo.objects.get(id=response.data['id']).title, 'New Automated Task')

    def test_update_todo(self):
        data = {'is_completed': True}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_completed)

    def test_delete_todo(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Todo.objects.count(), 0)

    def test_unauthenticated_access_blocked(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)