from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser, Department, Role
from rest_framework_simplejwt.tokens import RefreshToken

class AccountsTests(APITestCase):

    def setUp(self):
        # Set up a department and role for testing
        self.department = Department.objects.create(name="development")
        self.role = Role.objects.create(name="developer")

        # Create an admin user
        self.admin_user = CustomUser.objects.create_user(
            username='admin', 
            email='admin@example.com',
            password='admin123',
            department=self.department,
            role=self.role,
            is_staff=True
        )

        # Create a regular user
        self.user = CustomUser.objects.create_user(
            username='user', 
            email='user@example.com',
            password='user123',
            department=self.department,
            role=self.role
        )

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_register_user(self):
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newuser123",
            "department": self.department.id,
            "role": self.role.id
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 3)  # admin_user, user, and newuser

    def test_login_user(self):
        url = reverse('login')
        data = {
            "email": "user@example.com",
            "password": "user123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout_user(self):
        url = reverse('logout')
        # First, log in to get a valid token
        token = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        data = {"refresh": str(RefreshToken.for_user(self.user))}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_department_list_create(self):
        url = reverse('department-list-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))

        # Test department creation
        data = {"name": "testing"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

        # Test department list
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # two departments: "development" and "testing"

    def test_user_profile(self):
        url = reverse('user-profile')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user')

        # Test update user profile
        data = {"username": "updateduser"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updateduser')

    def test_admin_can_retrieve_update_delete_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))

        # Test retrieve user
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user')

        # Test update user
        data = {"username": "updateduser"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'updateduser')

        # Test delete user
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.id).exists())

    def test_non_admin_cannot_access_admin_endpoints(self):
        # Try to access the user list as a non-admin
        url = reverse('user-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_invalid_login(self):
        url = reverse('login')
        data = {
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_role_without_permission(self):
        url = reverse('role-list-create')
        data = {"name": "guest"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_another_user(self):
        another_user = CustomUser.objects.create_user(
            username='another_user',
            email='another_user@example.com',
            password='another_user123',
            department=self.department,
            role=self.role
        )
        url = reverse('user-detail', kwargs={'pk': another_user.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_department(self):
        url = reverse('department-list-create')
        data = {"name": "HR"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_retrieve_department(self):
        url = reverse('department-retrieve-update-destroy', args=[self.department.id])
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "development")

    def test_admin_can_delete_department(self):
        url = reverse('department-retrieve-update-destroy', kwargs={'pk': self.department.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(pk=self.department.id).exists())

    def test_user_cannot_delete_department(self):
        new_department = Department.objects.create(name="HR")
        url = reverse('department-retrieve-update-destroy', kwargs={'pk': new_department.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Department.objects.filter(pk=new_department.id).exists())

    def test_admin_can_update_role(self):
        new_role = Role.objects.create(name="manager")
        url = reverse('role-retrieve-update-destroy', kwargs={'pk': new_role.id})
        data = {"name": "senior_manager"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_role.refresh_from_db()
        self.assertEqual(new_role.name, "senior_manager")

    def test_user_cannot_update_role(self):
        new_role = Role.objects.create(name="intern")
        url = reverse('role-retrieve-update-destroy', kwargs={'pk': new_role.id})
        data = {"name": "junior intern"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.user))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        new_role.refresh_from_db()
        self.assertEqual(new_role.name, "intern")

    def test_create_role_as_admin(self):
        url = reverse('role-list-create')
        data = {"name": "consultant"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name="consultant").exists())

    def test_create_department_as_admin(self):
        url = reverse('department-list-create')
        data = {"name": "HR"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(name="hr").exists())

    def test_retrieve_department_details(self):
        url = reverse('department-retrieve-update-destroy', kwargs={'pk': self.department.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'development')

    def test_retrieve_role_details(self):
        url = reverse('role-retrieve-update-destroy', kwargs={'pk': self.role.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.get_token(self.admin_user))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'developer')

    def test_update_user_profile_without_authentication(self):
        url = reverse('user-profile')
        data = {"username": "anonymous_user"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_user_profile_without_authentication(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
