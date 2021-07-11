import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import response
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import ITEMS_PER_PAGE

from ..models import Comment, Follow, Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='FollowTester')
        cls.whoyauthor = User.objects.create_user(username='NotFollowTester')
        cls.user = User.objects.create_user(username='ViewsTester')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.whoyauthor_client = Client()
        cls.whoyauthor_client.force_login(cls.whoyauthor)
        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test Group description'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Some test post text',
            image=image
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()

    def test_comments_authorized(self):
        """Авторизированный пользователь может комментировать посты"""
        comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            text='test comment'
        )
        self.assertEqual(comment.text, self.post.comments.last().text)

    def test_follow_unfollow_authorized(self):
        """Авторизованный пользователь может подписываться и отписываться"""
        following = self.author.following.count()
        follower = self.user.follower.count()
        self.authorized_client.get(f'/{self.author}/follow/')
        self.assertEqual(self.author.following.count(), following + 1)
        self.assertEqual(self.user.follower.count(), follower + 1)
        self.authorized_client.get(f'/{self.author}/unfollow/')
        self.assertEqual(self.author.following.count(), following)
        self.assertEqual(self.user.follower.count(), follower)

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него"""
        Follow.objects.create(user=self.user, author=self.author)
        Post.objects.create(author=self.author, text='Follow me')
        response_1 = self.authorized_client.get(reverse('follow_index'))
        response_2 = self.whoyauthor_client.get(reverse('follow_index'))
        self.assertEqual(response_1.context['posts_total'], 1)
        self.assertEqual(response_2.context['posts_total'], 0)

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': (
                reverse('group_posts', kwargs={'slug': ViewsTest.group.slug})
            ),
            'posts/new_post.html': reverse('new_post'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        response = self.guest_client.get(reverse('index'))
        post = response.context['page'][0]
        post_context = {
            ViewsTest.post.group: post.group,
            ViewsTest.post.pub_date: post.pub_date,
            ViewsTest.post.text: post.text,
            ViewsTest.post.author: post.author,
            ViewsTest.post.image: post.image,
        }
        for key, value in post_context.items():
            self.assertEqual(key, value)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': ViewsTest.group.slug})
        )
        group = response.context['group']
        group_context = {
            ViewsTest.group.title: group.title,
            ViewsTest.group.description: group.description,
            ViewsTest.group.posts.last().author: group.posts.last().author,
            ViewsTest.group.posts.last().pub_date: group.posts.last().pub_date,
            ViewsTest.group.posts.last().text: group.posts.last().text,
            ViewsTest.group.posts.last().image: group.posts.last().image,
        }
        for key, value in group_context.items():
            self.assertEqual(key, value)

    def test_new_post_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': ViewsTest.user.username,
                    'post_id': ViewsTest.post.id,
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': ViewsTest.user.username})
        )
        author = response.context['author']
        author_context = {
            ViewsTest.user.username: author.username,
            # без обертки в str() сыпется тест на этом месте. Быдлокод, чо:
            str(ViewsTest.user.posts.all()): str(author.posts.all()),
            ViewsTest.user.posts.count(): author.posts.count(),
            ViewsTest.user.posts.last().pub_date: author.posts.last().pub_date,
            ViewsTest.user.posts.last().text: author.posts.last().text,
            ViewsTest.user.posts.last().id: author.posts.last().id,
            ViewsTest.user.posts.last().image: author.posts.last().image,
        }
        for key, value in author_context.items():
            self.assertEqual(key, value)

    def test_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'username': ViewsTest.user.username,
                    'post_id': ViewsTest.post.id,
                }
            )
        )
        author = response.context['author']
        post_context = {
            ViewsTest.user.username: author.username,
            # без обертки в str() сыпется тест на этом месте. Быдлокод, чо:
            str(ViewsTest.user.posts.all()): str(author.posts.all()),
            ViewsTest.user.posts.count(): author.posts.count(),
            ViewsTest.user.posts.last().pub_date: author.posts.last().pub_date,
            ViewsTest.user.posts.last().text: author.posts.last().text,
            ViewsTest.user.posts.last().id: author.posts.last().id,
            ViewsTest.user.posts.last().image: author.posts.last().image,
        }
        for key, value in post_context.items():
            self.assertEqual(key, value)

    # решил не писать отдельный класс для этого теста
    def test_index_page_cache(self):
        """Проверка работы кэша на главной странице"""
        # если не создавать экземпляр поста здесь, остальные тесты не пройдут:
        post = Post.objects.create(
            author=self.user,
            text='Index page cache test post'
        )
        response_1 = self.guest_client.get(reverse('index'))
        response_2 = self.guest_client.get(reverse('index'))
        post.delete()
        self.assertEqual(response_1.context['posts_total'], 2)
        self.assertIsNone(response_2.context)
        cache.clear()
        response_3 = self.guest_client.get(reverse('index'))
        self.assertEqual(response_3.context['posts_total'], 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='PaginatorViewsTester')
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Test Group',
            slug='test-group',
            description='Test Group description'
        )
        for i in range(ITEMS_PER_PAGE + 3):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Some test post text'
            )

    def setUp(self):
        cache.clear()

    def test_first_page_contains_enough_records(self):
        reverse_names = {
            reverse('index'),
            reverse(
                'group_posts',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ),
            reverse(
                'profile',
                kwargs={'username': PaginatorViewsTest.user.username}
            ),
        }
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    ITEMS_PER_PAGE
                )

    def test_second_page_contains_enough_records(self):
        reverse_names = {
            reverse('index'),
            reverse(
                'group_posts',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ),
            reverse(
                'profile',
                kwargs={'username': PaginatorViewsTest.user.username}
            ),
        }
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    3
                )


class GroupViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='GroupViewsTester')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group1 = Group.objects.create(
            title='Test Group One',
            slug='test-group-one'
        )
        cls.group2 = Group.objects.create(
            title='Test Group Two',
            slug='test-group-two'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group1,
            text='Some test post text'
        )

    def setUp(self):
        cache.clear()

    def test_grouped_post_is_shown_on_index_and_group1_pages(self):
        reverse_names = {
            reverse('index'),
            reverse(
                'group_posts', kwargs={'slug': GroupViewsTest.group1.slug}
            ),
        }
        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post = response.context['page'][0]
                self.assertEqual(GroupViewsTest.post.id, post.id)

    def test_grouped_post_is_not_shown_on_group2_page(self):
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': GroupViewsTest.group2.slug})
        )
        group = response.context['group']
        self.assertIsNone(group.posts.last())
