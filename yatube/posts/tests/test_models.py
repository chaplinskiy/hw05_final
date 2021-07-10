from django.test import TestCase

from ..models import Group, Post, User


class ModelStrTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='ModelsTester')
        cls.group = Group.objects.create(
            title="Test Group Title"
        )
        cls.post = Post.objects.create(
            author=ModelStrTest.user,
            text="lorem ipsum dolor sit amet"
        )

    def test_group_str(self):
        """Проверяем, что в __str__ группы записалось значение из title"""
        group = ModelStrTest.group
        self.assertEqual(
            str(group), group.title,
            'В __str__ группы записалось что-то не то!'
        )

    def test_post_str(self):
        """Проверяем, что в __str__ поста записались первые 15 символов"""
        post = ModelStrTest.post
        self.assertEqual(
            str(post), post.text[:15], 'В __str__ поста лежит что-то не то!'
        )
