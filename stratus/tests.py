import unittest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
REPO_DATA = ("local", "master")
COMMIT_SHA = ("78a325da2d00c5071ddddc8b35dfb0e1241660b1",)
PATH = ("plantilla.html",)

class TestCommitViews(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('test','test','test')
        self.u.is_active = True
        self.u.save()
        self.client.login(username='test',password='test')

    def test_log(self):
        """Test the creation of the Instance from the form data."""
        url = reverse('stratus-log', args=REPO_DATA)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_commit_view(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + COMMIT_SHA
        url = reverse('stratus-commit-view', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_file_history(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-history-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_undo(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA
        url = reverse('stratus-undo', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')


class TestFileViews(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('test','test','test')
        self.u.is_active = True
        self.u.save()
        self.client.login(username='test',password='test')

    def test_edit(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-edit-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_new(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('cstratus-new-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_upload(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-history-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_delete(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-delete-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_rename(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-delete-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_view(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH + COMMIT_SHA
        url = reverse('stratus-delete-file', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url ,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')


class TestTreeViews(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('test','test','test')
        self.u.is_active = True
        self.u.save()
        self.client.login(username='test',password='test')

    def test_tree_view(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-tree-view', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_commit_tree_view(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-commit-tree-view', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')


class TestMetaViews(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('test','test','test')
        self.u.is_active = True
        self.u.save()
        self.client.login(username='test',password='test')

    def test_search(self):
        """Test the creation of the Instance from the form data."""
        data = REPO_DATA + PATH
        url = reverse('stratus-search', args=data)
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')

    def test_repos(self):
        """Test the creation of the Instance from the form data."""
        url = reverse('stratus-repos', )
        response = self.client.get( url )
        self.assertNotContains(response,'error')
        response = self.client.get( url,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotContains(response,'error')