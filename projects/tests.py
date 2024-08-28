from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, Department, Role
from projects.models import Project
from rest_framework_simplejwt.tokens import RefreshToken

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
        # Assert that the non-admin user can see their own projects
        project_names = [project['project_name'] for project in response.data]
        self.assertIn('Project_1', project_names)  # Example project that the user is associated with
        self.assertNotIn('Project_2', project_names)

    def test_list_projects_as_non_admin(self):
        url = reverse('project-user-view')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.non_admin_token)
        response = self.client.get(url)
        
        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the non-admin user can see their own project
        project_names = [project['project_name'] for project in response.data]
        self.assertIn('Project A', project_names)
        self.assertNotIn('Project B', project_names)
    
    def test_retrieve_project(self):
        url = reverse('project-update', args=[self.projects[0].id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['project_name'], self.projects[0].project_name)


    def test_update_project_as_admin(self):
        url = reverse('project-update', args=[self.projects[0].id])
        data = {"status": "closed"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "closed")

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

        
        
        