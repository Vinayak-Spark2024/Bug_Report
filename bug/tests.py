
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from bug.models import Bug
from projects.models import Project
from accounts.models import  Department, Role

from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class BugTests(APITestCase):

    def setUp(self):
        # Create departments
        python_dept = Department.objects.create(name='python')
        java_dept = Department.objects.create(name='java')
        manager_role = Role.objects.create(name='manager')
        tester_role = Role.objects.create(name='tester')
        team_lead_role = Role.objects.create(name='team_lead')
        developer_role = Role.objects.create(name='developer')

        # Create users
        self.users = {
            'python_manager': User.objects.create_user(
                email='python_manager@example.com', username='python_manager', password='password',
                department=python_dept, role=manager_role
            ),
            'python_tester': User.objects.create_user(
                email='python_tester@example.com', username='python_tester', password='password',
                department=python_dept, role=tester_role
            ),
            'python_team_lead': User.objects.create_user(
                email='python_team_lead@example.com', username='python_team_lead', password='password',
                department=python_dept, role=team_lead_role
            ),
            'python_developer1': User.objects.create_user(
                email='python_developer1@example.com', username='python_developer1', password='password',
                department=python_dept, role=developer_role
            ),
            'python_developer2': User.objects.create_user(
                email='python_developer2@example.com', username='python_developer2', password='password',
                department=python_dept, role=developer_role
            ),
            'java_manager': User.objects.create_user(
                email='java_manager@example.com', username='java_manager', password='password',
                department=java_dept, role=manager_role
            ),
            'java_tester': User.objects.create_user(
                email='java_tester@example.com', username='java_tester', password='password',
                department=java_dept, role=tester_role
            ),
            'java_team_lead': User.objects.create_user(
                email='java_team_lead@example.com', username='java_team_lead', password='password',
                department=java_dept, role=team_lead_role
            ),
            'java_developer1': User.objects.create_user(
                email='java_developer1@example.com', username='java_developer1', password='password',
                department=java_dept, role=developer_role
            ),
            'java_developer2': User.objects.create_user(
                email='java_developer2@example.com', username='java_developer2', password='password',
                department=java_dept, role=developer_role
            )
        }

        # Create projects
        self.project1 = Project.objects.create(
            project_name="Python Project",
            project_duration=12,  # Assuming duration is in months
            status='open'
        )
        self.project2 = Project.objects.create(
            project_name="Java Project",
            project_duration=6,   # Assuming duration is in months
            status='open'
        )

        # Assign users to projects
        self.project1.users.set([
            self.users['python_manager'],
            self.users['python_tester'],
            self.users['python_team_lead'],
            self.users['python_developer1'],
            self.users['python_developer2']
        ])
        
        self.project2.users.set([
            self.users['java_manager'],
            self.users['java_tester'],
            self.users['java_team_lead'],
            self.users['java_developer1'],
            self.users['java_developer2']
        ])

        # Create bugs
        self.bug1 = Bug.objects.create(
            bug_type='error',
            created_by=self.users['python_tester'],
            assigned_to=self.users['python_developer1'],
            bug_description='Bug in Python Project',
            project=self.project1,
            bug_priority='high',
            bug_severity='critical',
            status='open',
            is_current_project=True,
        )

        self.bug2 = Bug.objects.create(
            bug_type='issue',
            created_by=self.users['java_tester'],
            assigned_to=self.users['java_developer1'],
            bug_description='Bug in Java Project',
            project=self.project2,
            bug_priority='medium',
            bug_severity='major',
            status='open',
            is_current_project=True,
        )

        # Additional bugs
        self.bug3 = Bug.objects.create(
            bug_type='error',
            created_by=self.users['python_team_lead'],
            assigned_to=self.users['python_developer2'],
            bug_description='Second bug in Python Project',
            project=self.project1,
            bug_priority='low',
            bug_severity='minor',
            status='open',
            is_current_project=True,
        )

        self.bug4 = Bug.objects.create(
            bug_type='issue',
            created_by=self.users['java_team_lead'],
            assigned_to=self.users['java_developer2'],
            bug_description='Second bug in Java Project',
            project=self.project2,
            bug_priority='high',
            bug_severity='critical',
            status='open',
            is_current_project=True,
        )

        self.bug5 = Bug.objects.create(
            bug_type='error',
            created_by=self.users['python_manager'],
            assigned_to=self.users['python_developer1'],
            bug_description='Third bug in Python Project',
            project=self.project1,
            bug_priority='medium',
            bug_severity='major',
            status='open',
            is_current_project=True,
        )

    def get_token_for_user(self, email, password):
        refresh = RefreshToken.for_user(User.objects.get(email=email))
        return str(refresh.access_token)

    # Test cases for creating a bug
    def test_bug_create_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('bug-create')
        data = {
            'bug_type': 'issue',
            'bug_description': 'New issue in Python Project',
            'project': self.project1.id,
            'bug_priority': 'medium',
            'bug_severity': 'minor',
            'status': 'open'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bug.objects.count(), 6)  # Updated expectation

    def test_bug_create_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('bug-create')
        data = {
            'bug_type': 'issue',
            'bug_description': 'New issue in Python Project',
            'project': self.project1.id,
            'bug_priority': 'medium',
            'bug_severity': 'minor',
            'status': 'open'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bug.objects.count(), 6)  # Updated expectation

    def test_bug_create_without_project(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('bug-create')
        data = {
            'bug_type': 'issue',
            'bug_description': 'New issue without project',
            'bug_priority': 'medium',
            'bug_severity': 'minor',
            'status': 'open'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bug.objects.count(), 5)  # No new bug created

    # Test cases for listing bugs
    def test_bug_list_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('bug-list')
        response = self.client.get(url)
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # Updated expectation

    def test_bug_list_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('bug-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test cases for listing bugs by status
    def test_bug_list_status_open_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('admin-status-bugs', kwargs={'status': 'open'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # All 5 bugs are 'open'

    
    def test_bug_list_status_closed_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.bug_closed = Bug.objects.create(
            bug_type='issue',
            created_by=self.users['java_developer2'],
            assigned_to=self.users['java_team_lead'],
            bug_description='A closed bug in Java Project',
            project=self.project2,
            bug_priority='medium',
            bug_severity='major',
            status='closed',  # Closed status
            is_current_project=True,
        )
        url = reverse('admin-status-bugs', kwargs={'status': 'closed'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        bug_ids = [bug['id'] for bug in response.data]
        self.assertIn(self.bug_closed.id, bug_ids)

    def test_bug_list_status_open_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('user-status-bugs', kwargs={'status': 'open'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_bug_list_status_closed_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('user-status-bugs', kwargs={'status': 'closed'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No bugs are 'closed'

    def test_bug_list_status_in_progress_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('user-status-bugs', kwargs={'status': 'in_progress'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) 

    # Test cases for retrieving a bug
    def test_bug_retrieve_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('admin-bug-update', kwargs={'pk': self.bug1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bug_description'], 'Bug in Python Project')

    def test_bug_retrieve_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('user-bug-update', kwargs={'pk': self.bug4.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Expecting 403, not 404


    # Test cases for updating a bug
    def test_bug_update_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('admin-bug-update', kwargs={'pk': self.bug1.id})
        data = {'bug_description': 'Updated description for Python Project'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bug1.refresh_from_db()
        self.assertEqual(self.bug1.bug_description, 'Updated description for Python Project')


    # Test cases for deleting a bug
    def test_bug_delete_admin(self):
        token = self.get_token_for_user('python_manager@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('admin-bug-update', kwargs={'pk': self.bug1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Bug.objects.filter(id=self.bug1.id).exists())

    def test_bug_delete_regular_user(self):
        token = self.get_token_for_user('python_developer1@example.com', 'password')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        url = reverse('user-bug-update', kwargs={'pk': self.bug1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue(Bug.objects.filter(id=self.bug1.id).exists())
