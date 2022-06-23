from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from math import floor
from django.db import transaction
from django.urls import reverse
from django.utils.text import slugify
# Utility functions

def auto_slug(name, cls):
    slug = slugify(name)
    num = 0
    while cls.objects.filter(slug=slug).exists():
        slug = slugify(f'{slug}-{num}')
        num += 1
    return slug

# Create your models here.
def get_profile_image_path(instance, file_name):
    return f'profile/{instance.user.id}/{file_name}'
class Profile(models.Model):
    GENDERS = [
        ('Male', _('Male')),
        ('Female', _('Female')),
    ]
    name = models.CharField(_('Name'), max_length=100, blank=True)
    birthday = models.DateField(_('Birthday'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=6, choices=GENDERS, blank=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    address = models.CharField(_('Address'), max_length=200, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to=get_profile_image_path, default='http://hinhnenhd.com/wp-content/uploads/2021/08/Tai-ngay-avt-trang-fb-moi-nhat-dep-nhat-doc-dao-12.jpg')
    timezone = models.CharField(_('Timezone'), max_length=100, default='UTC')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_access = models.DateTimeField(auto_now=True)

    @property
    def is_online(self):
        return self.last_access > timezone.now() - timezone.timedelta(minutes=5)

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(_('Name'), max_length=300)
    description = models.TextField(_('Description'))
    phone = models.CharField(_('Phone'), max_length=20)
    address = models.CharField(_('Address'), max_length=300)
    owner = models.OneToOneField(to=User, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=350, unique=True, null=True)

    def save(self, *args, **kwargs):
        self.slung = auto_slug(self.name, self.__class__)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name
        
def get_image_path(instance, file_name):
    return f'store/{instance.store.id}/{instance.id}/thumbnail/{file_name}'
class Product(models.Model):
    name = models.CharField(_('Name'), max_length=300)
    description = models.TextField(_('Description'))
    thumbnail = models.ImageField(_('Thumbnail'), upload_to=get_image_path)
    price = models.IntegerField(_('Price'))
    quantity = models.IntegerField(_('Quantity'))
    sold = models.IntegerField(_('Sold'), default=0)
    available = models.BooleanField(_('Available'), default=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name=_('Category'))
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    rating_count = models.IntegerField(default=0)
    cold_start = models.BooleanField(_('cold_start'), default=False)
    view = models.IntegerField(default=0)
    slug = models.SlugField(max_length=350, unique=True, null=True)
    content_based = models.IntegerField(default=5)

    def save(self, *args, **kwargs):
        self.slug = auto_slug(self.name, self.__class__)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.id, 'slug': self.slug})

    @property
    def buy_count(self):
        return self.orderdetail_set.all().count()
    
    @property
    def sell_price(self):
        if hasattr(self, 'sale') and self.sale.valid():
            return self.sale.price
        return self.price

    def __str__(self):
        return self.name

def get_product_image_path(instance, file_name):
    return f'store/{instance.product.store.id}/{instance.product.id}/{file_name}'
class ProductImage(models.Model):
    image = models.ImageField(upload_to=get_product_image_path)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

def get_product_video_path(instance, file_name):
    return f'store/{instance.product.store.id}/{instance.product.id}/{file_name}'

class ProductVideo(models.Model):
    video = models.FileField(upload_to=get_product_video_path)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

class LikedProduct(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.user)
    
class ProductSale(models.Model):
    SALE_TYPE = [
        ('P', 'Percentage'),
        ('F', 'Fixed'),
    ]
    product = models.OneToOneField(to=Product, on_delete=models.CASCADE, related_name='sale')
    value = models.IntegerField()
    sale_type = models.CharField(max_length=1, choices=SALE_TYPE)
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def price(self):
        if self.sale_type == 'P':
            return floor(self.product.price * (100 - self.value) / 100)
        else:
            return floor(self.product.price - self.value)
    
    def valid(self):
        return self.expired_at > timezone.now()

class Comment(models.Model):
    content = models.TextField()
    rate = models.IntegerField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Order(models.Model):
    STATUS = [
        ('Cart', 'Cart'), # Product in cart
        ('Pending', 'Pending'), # Waiting for store to confirm
        ('Accepted', 'Accepted'), # Store confirmed
        ('Rejected', 'Rejected'), # Store rejected
        ('Cancelled', 'Cancelled'), # User cancelled
        ('Finished', 'Finished'), # User finished
    ]
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS, default='Cart')
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    location = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cost = models.IntegerField(default=0)

    @property
    def detail(self):
        return OrderDetail.objects.filter(order=self)

    @property
    def cal_cost(self):
        if self.status == 'Cart':
            cost = 0
            for order_detail in self.detail:
                order_detail.cost = order_detail.product.sell_price * order_detail.quantity
                order_detail.save()
                cost += order_detail.cost
            self.cost = cost
            self.save()
        return self.cost

    def purchase(self, address):
        try:
            with transaction.atomic():
                cost = 0
                for order_detail in self.detail:
                    if order_detail.quantity > order_detail.product.quantity:
                        raise Exception('Product out of stock')
                    order_detail.cost = order_detail.product.sell_price * order_detail.quantity
                    order_detail.product.quantity -= order_detail.quantity
                    order_detail.save()
                    order_detail.product.save()
                    cost += order_detail.cost
                self.status = 'Pending'
                self.location = address
                self.cost = cost
                self.created_at = timezone.now()
                self.save()
                return True
        except Exception as e:
            return False

    def __str__(self):
        return str(self.id) + ' ' + self.user.username

class OrderDetail(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)

class Notification(models.Model):
    STATUS = [
        ('Unread', 'Unread'), # New notification
        ('Read', 'Read'), # Notification has been read
    ]

    ACTIONS = [
        ('Order', 'Order'), # New order
        ('Comment', 'Comment'), # New comment
        ('Accept', 'Accept'), # Store accepted order
        ('Reject', 'Reject'), # Store rejected order
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS, default='Unread')
    actor = models.CharField(max_length=100)
    action = models.CharField(max_length=10, choices=ACTIONS)
    target = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_product(self):
        if self.action == 'Comment':
            return Product.objects.get(id=self.target)
        return None

class Chat(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(default=timezone.now)

def get_chat_image_path(instance, file_name):
    return f'chat/{instance.chat.id}/{file_name}'
class Message(models.Model):
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    is_user = models.BooleanField(null=True)
    content = models.CharField(max_length=300)
    image = models.ImageField(upload_to=get_chat_image_path, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)