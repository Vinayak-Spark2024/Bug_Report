from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from projects.models import Project
from bug.models import Bug

User = get_user_model()

class BugTests(APITestCase):

    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(email='admin@test.com', password='admin123', username='admin', is_staff=True)
        self.manager_user = User.objects.create_user(email='manager@test.com', password='manager123',username='manager', is_staff=True)
        self.tester_user = User.objects.create_user(email='tester@test.com', password='tester123',username='tester',)
        self.team_lead_user = User.objects.create_user(email='teamlead@test.com', password='teamlead123', username='team_lead',)
        self.developer_users = [
            User.objects.create_user(email=f'dev{i}@test.com', password='dev123', username=f'dev{i}') for i in range(1, 4)
        ]

        # Create projects
        self.project1 = Project.objects.create(project_name="Project 1", project_duration=30, status='open')
        self.project2 = Project.objects.create(project_name="Project 2", project_duration=45, status='open')

        # Create bugs
        self.bugs = [
            Bug.objects.create(
                bug_type='error', created_by=self.tester_user, assigned_to=self.developer_users[0], 
                bug_description='Sample bug description', project=self.project1, 
                bug_priority='high', bug_severity='critical', status='open'
            ) for _ in range(5)
        ]

        # Get tokens
        self.admin_token = self.get_token(self.admin_user)
        self.manager_token = self.get_token(self.manager_user)
        self.tester_token = self.get_token(self.tester_user)
        self.team_lead_token = self.get_token(self.team_lead_user)
        self.developer_tokens = [self.get_token(dev) for dev in self.developer_users]

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    # Test Cases
    def test_create_bug_as_tester(self):
        url = reverse('bug-create')
        data = {
            "bug_type": "issue",
            "bug_description": "New bug",
            "project": self.project1.id,
            "bug_priority": "medium",
            "bug_severity": "major",
            "status": "open"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tester_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_bug_as_non_tester(self):
        url = reverse('bug-create')
        data = {
            "bug_type": "issue",
            "bug_description": "New bug by dev",
            "project": self.project1.id,
            "bug_priority": "low",
            "bug_severity": "minor",
            "status": "open"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_bugs_as_admin(self):
        url = reverse('bug-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_list_bugs_as_non_admin(self):
        url = reverse('bug-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tester_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_open_bugs_as_admin(self):
        url = reverse('admin-open-bugs')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(bug['status'] == 'open' for bug in response.data))

    def test_filter_closed_bugs_as_admin(self):
        url = reverse('admin-closed-bugs')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_update_bug_as_admin(self):
        url = reverse('admin-bug-update', args=[self.bugs[0].bug_id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bugs[0].refresh_from_db()
        self.assertEqual(self.bugs[0].status, 'closed')

    def test_update_bug_as_assigned_developer(self):
        url = reverse('user-bug-update', args=[self.bugs[0].bug_id])
        data = {"status": "in_progress"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bugs[0].refresh_from_db()
        self.assertEqual(self.bugs[0].status, 'in_progress')

    def test_update_bug_as_non_assigned_developer(self):
        non_assigned_bug = Bug.objects.create(
            bug_type='issue', created_by=self.tester_user, 
            bug_description='Non-assigned bug', project=self.project1, 
            bug_priority='medium', bug_severity='normal', status='open'
        )
        print(f'Non-assigned bug ID: {non_assigned_bug.bug_id}')  # Print bug ID for debugging
        url = reverse('user-bug-update', args=[non_assigned_bug.bug_id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[1])
        response = self.client.patch(url, data, format='json')
        print(response.data)  # Print response data for debugging
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_non_admin_user_cannot_update_bug(self):
        url = reverse('user-bug-update', args=[self.bugs[0].bug_id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tester_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_user_bugs(self):
        url = reverse('user-bugs')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_list_user_open_bugs(self):
        url = reverse('user-open-bugs')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(all(bug['status'] == 'open' for bug in response.data))

    def test_list_user_closed_bugs(self):
        url = reverse('user-closed-bugs')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_bug_with_invalid_data(self):
        url = reverse('bug-create')
        data = {
            "bug_type": "invalid_type",
            "bug_description": "",
            "project": self.project1.id,
            "bug_priority": "invalid_priority",
            "bug_severity": "invalid_severity",
            "status": "invalid_status"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tester_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_bug_with_missing_fields(self):
        url = reverse('bug-create')
        data = {
            "bug_type": "issue",
            "bug_description": "Incomplete data"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.tester_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_bug_as_manager(self):
        url = reverse('admin-bug-update', args=[self.bugs[0].bug_id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.manager_token)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bugs[0].refresh_from_db()
        self.assertEqual(self.bugs[0].status, 'closed')

    def test_delete_bug_as_admin(self):
        url = reverse('admin-bug-update', args=[self.bugs[0].bug_id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_bug_as_non_admin(self):
        url = reverse('admin-bug-update', args=[self.bugs[1].bug_id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.developer_tokens[0])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
