from django.contrib import admin
from .models import Post , Profile, Favorites , Chat , Comment , Message , Tag

class SlugAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('content',)}

admin.site.register(Post, SlugAdmin)
admin.site.register(Profile)
admin.site.register(Favorites)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Tag)