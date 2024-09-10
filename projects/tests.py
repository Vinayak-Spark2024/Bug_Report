from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from projects.models import Project
from accounts.models import CustomUser, Department, Role

class ProjectTests(APITestCase):

    def setUp(self):
        # Create departments
        self.department_python = Department.objects.create(name="python")
        self.department_java = Department.objects.create(name="java")

        # Create roles
        self.role_tester = Role.objects.create(name="tester")
        self.role_manager = Role.objects.create(name="manager")
        self.role_developer = Role.objects.create(name="developer")
        self.role_team_lead = Role.objects.create(name="team_lead")

        # Create users
        self.users = []
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=f'python_user_{i}', 
                email=f'python_user_{i}@example.com',
                password='password123',
                department=self.department_python,
                role=self.role_developer
            )
            self.users.append(user)

        # Create an additional user in a different department
        self.additional_users = []
        for i in range(4):
            user = CustomUser.objects.create_user(
                username=f'java_user_{i}', 
                email=f'java_user_{i}@example.com',
                password='password123',
                department=self.department_java,
                role=self.role_manager
            )
            self.additional_users.append(user)

        # Create an admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='admin123',
            department=self.department_python,
            role=self.role_manager,
            is_staff=True
        )

        # Create projects
        self.projects = []
        for i in range(4):
            project = Project.objects.create(
                project_name=f'Project_{i+1}',
                project_duration=10,
                status='open'
            )
            # Assign all users to each project
            project.users.set(self.users + self.additional_users)
            self.projects.append(project)


    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


    def test_create_project_as_admin(self):
        url = reverse('project-create')
        data = {
            "project_name": "New Project",
            "project_duration": 12,
            "status": "open",
            "users": [user.id for user in self.users]  # Assign users to the new project
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(project_name="New Project").exists())


    def test_create_project_as_non_admin(self):
        url = reverse('project-create')
        data = {
            "project_name": "Unauthorized Project",
            "project_duration": 8,
            "status": "open",
            "users": [user.id for user in self.users]  # Assign users to the new project
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))  # Non-admin user
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_list_projects_as_admin(self):
        url = reverse('project-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)


    def test_list_projects_as_non_admin(self):
        url = reverse('project-list')  # Ensure the URL is correct
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for one of the correct project names, e.g., 'Project_1'
        project_names = [project['project_name'] for project in response.data]
        self.assertIn('Project_1', project_names)  # Ensure this matches your setup

    def test_retrieve_project(self):
        url = reverse('project-update', args=[self.projects[0].id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], self.projects[0].project_name)

    def test_update_project_as_non_admin(self):
        url = reverse('project-update', args=[self.projects[0].id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_project_view(self):
        url = reverse('project-user-view')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_user_cannot_see_other_user_projects(self):
        url = reverse('project-user-view')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.additional_users[0]))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_update_project_as_admin(self):
        url = reverse('project-update', args=[self.projects[0].id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        data = {'status': 'closed'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.data['status'], 'closed')


    def test_delete_project_as_admin(self):
        url = reverse('project-update', args=[self.projects[0].id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertFalse(Project.objects.filter(id=self.projects[0].id).exists())

    def test_delete_project_as_admin(self):
        url = reverse('project-update', args=[self.projects[0].id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.delete(url)
        
        # Expecting 405 Method Not Allowed instead of 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        # Check that the project still exists
        self.assertTrue(Project.objects.filter(id=self.projects[0].id).exists())

    def test_non_admin_user_cannot_update_project(self):
        url = reverse('project-update', args=[self.projects[0].id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.patch(url, data, format='json')
        
        # Expecting 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Ensure the status hasn't changed
        self.projects[0].refresh_from_db()
        self.assertEqual(self.projects[0].status, 'open')

    def test_admin_can_update_project_name(self):
        url = reverse('project-update', args=[self.projects[0].id])
        data = {"project_name": "Updated Project Name"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], 'Updated Project Name')

    def test_non_admin_cannot_update_project_name(self):
        url = reverse('project-update', args=[self.projects[0].id])
        data = {"project_name": "Unauthorized Project Name"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_add_users_to_project(self):
        url = reverse('project-update', args=[self.projects[0].id])
        new_user = CustomUser.objects.create_user(
            username='new_user', email='new_user@example.com', password='password123',
            department=self.department_python, role=self.role_developer
        )
        data = {"users": [user.id for user in self.users] + [new_user.id]}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(new_user.id, response.data['users'])

    def test_non_admin_cannot_add_users_to_project(self):
        url = reverse('project-update', args=[self.projects[0].id])
        new_user = CustomUser.objects.create_user(
            username='new_user', email='new_user@example.com', password='password123',
            department=self.department_python, role=self.role_developer
        )
        data = {"users": [user.id for user in self.users] + [new_user.id]}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_non_existent_project(self):
        url = reverse('project-update', args=[9999])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_project_without_name(self):
        url = reverse('project-create')
        data = {
            "project_duration": 12,
            "status": "open",
            "users": [user.id for user in self.users]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_with_existing_name(self):
        url = reverse('project-create')
        data = {
            "project_name": "Project_1",
            "project_duration": 12,
            "status": "open",
            "users": [user.id for user in self.users]
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_view_own_projects(self):
        url = reverse('project-user-view')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.users[0]))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_names = [project['project_name'] for project in response.data]
        self.assertIn('Project_1', project_names)
