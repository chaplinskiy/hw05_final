import uuid
from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Follow, Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='UrlTester')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group'
        )
        cls.following_user = User.objects.create_user(
            username='FollowingTester'
        )
        cls.not_following_user = User.objects.create_user(
            username='NotFollowingTester'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Some test post text'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.following_user
        )

    def setUp(self):
        cache.clear()

    def test_follow(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него"""
        post_to_follow = Post.objects.create(
            author=self.follow.author,
            text='Follow me'
        )
        post_list_following = Post.objects.filter(
            author__following__user=self.user
        )
        post_list_not_following = Post.objects.filter(
            author__following__user=self.not_following_user
        )
        self.assertIn(post_to_follow.text, post_list_following.last().text)
        self.assertIsNone(
            post_list_not_following.last()
        )

    def test_http_status_is_ok_for_guest_client(self):
        group = self.group
        username = self.user.username
        post_id = self.post.id
        response_urls = {
            '/',
            f'/group/{group.slug}/',
            f'/{username}/',
            f'/{username}/{post_id}/',
        }
        for url in response_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(HTTPStatus.OK.value, response.status_code)

    def test_http_status_is_ok_for_authorized_client(self):
        username = self.user.username
        post_id = self.post.id
        response_urls = {
            f'/{username}/{post_id}/edit/',
            '/new/',
        }
        for url in response_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(HTTPStatus.OK.value, response.status_code)

    def test_post_edit_page_unauthorized(self):
        username = self.user.username
        post_id = self.post.id
        response = self.guest_client.get(f'/{username}/{post_id}/edit/')
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, response.url)

    def test_post_edit_page_authorized_not_author(self):
        username = self.user.username
        not_author = User.objects.create_user(username='NotUrlTester')
        post_id = self.post.id
        authorized_not_author = Client()
        authorized_not_author.force_login(not_author)
        response = authorized_not_author.get(
            f'/{username}/{post_id}/edit/'
        )
        self.assertRedirects(response, f'/{username}/{post_id}/')

    def test_new_guest_client(self):
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_urls_use_correct_template(self):
        slug = self.group.slug
        username = self.user.username
        post_id = self.post.id
        templates_url_names = {
            'index.html': ['/'],
            'group.html': [f'/group/{slug}/'],
            'posts/new_post.html': [
                '/new/',
                f'/{username}/{post_id}/edit/',
            ]
        }
        for template, urls in templates_url_names.items():
            with self.subTest(urls=urls):
                for url in urls:
                    # cache.clear()
                    response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_not_found(self):
        """status_code is 404 for non_existing_url, ¿ok?"""
        non_existing_url = uuid.uuid4()
        response = self.guest_client.get(non_existing_url)
        self.assertEqual(HTTPStatus.NOT_FOUND.value, response.status_code)
