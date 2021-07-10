from django.contrib import admin

from .models import Comment, Follow, Group, Post


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author')
    search_fields = ('text',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
