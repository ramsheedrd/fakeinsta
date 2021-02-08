from .models import Post

def post_count(request):
    return {'post_count': Post.objects.all().count()}