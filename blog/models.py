from django.db import models
from users.models import User
import cloudinary
from io import BytesIO
from PIL import Image

    


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user.name)


class Post(models.Model):
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, default=1)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to = 'images/')
    thumbnail = models.ImageField(upload_to='images/', blank=True, null=True)
    pub_date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(Comment, related_name='posts', blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title
    

    def get_image(self):
        if self.image:
            return '' + self.image.url
        return ''
    
    def get_thumbnail(self):
        if self.thumbnail:
            return self.extract_secure_url(self.thumbnail.url)
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return self.extract_secure_url(self.thumbnail.url) if self.thumbnail else ''
            else:
                return ''

    def extract_secure_url(self, url):
        return url.split('/media/')[1]
    
    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=90)
        thumb_io.seek(0)

        thumbnail_data = thumb_io.read()

        thumbnail = cloudinary.uploader.upload(thumbnail_data, folder='images')

        return thumbnail['secure_url']
    

