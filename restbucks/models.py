from django.db import models


from django.contrib.auth.models import User
from django.utils.text import slugify
from django_fsm import FSMField, transition
from django.core.mail import send_mail


class AbstractBaseModel(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductAttribute(AbstractBaseModel):
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductAttributeOption(AbstractBaseModel):
    
    name = models.CharField(max_length=100)

    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.name


class Product(AbstractBaseModel):
    
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    unit_price = models.PositiveIntegerField(default=0)

    # each product could have some optional attributes.
    optional_attributes = models.ManyToManyField(ProductAttribute, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)


class Order(AbstractBaseModel):
   
    customer = models.ForeignKey(
        User,
        related_name='orders',
        on_delete=models.CASCADE,
    )

    state = FSMField(
        default='waiting',
        protected=True,
    )

    total_price = models.PositiveIntegerField(default=0)

    @transition(field=state, source="waiting", target="preparation")
    def prepare(self):
        try:
         send_mail(
            'Order State',
            'order canceled.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        except:
            pass
        

    @transition(field=state, source="preparation", target="ready")
    def ready(self):
        try:
         send_mail(
            'Order State',
            'order canceled.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        except:
            pass

    @transition(field=state, source="ready", target="delivered")
    def deliver(self):
       try:
          send_mail(
            'Order State',
            'order canceled.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
       except:
          pass

    @transition(field=state, source="waiting", target="canceled")
    def cancel(self):
        try:
         send_mail(
            'Order State',
            'order canceled.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        except:
            pass


class OrderItem(AbstractBaseModel):
    product = models.ForeignKey(
        Product,
        verbose_name="Product",
        on_delete=models.PROTECT,
    )
    order = models.ForeignKey(
        Order,
        verbose_name="Order",
        related_name='items',
        on_delete=models.CASCADE,
    )
    count = models.PositiveIntegerField("Count", )
    selected_options = models.ManyToManyField(ProductAttributeOption, blank=True)

# {"order": [
#             {
#                 "product":  "latte",
#                 "options": [
#                     {
#                         "name": "milk",
#                         "value": "skim"
#                     }
#                 ],
#                 "count": 1
#             }
#         ]
# }
def create_order(user_id, items,order_id=0):
    if order_id == 0:
        order = Order.objects.create(customer_id=user_id)
    else:
        order = Order.objects.filter(pk=order_id, customer=user_id).first()
        order.total_price = 0
    for item in items:
        selected_product = Product.objects.filter(product_name__iexact=item.get('product')).first()
        if not selected_product:
            continue
        order_item = OrderItem.objects.create(product=selected_product, order=order, count=item.get('count'))
        order.total_price += selected_product.unit_price
        for option in item.get('options'):
            selected_product_attr = selected_product.optional_attributes.filter(name__iexact=option.get('name')).first()
            if selected_product_attr:
                selected_option = selected_product_attr.options.filter(name__iexact=option.get('value')).first()
                if selected_option:
                    order_item.selected_options.add(selected_option)
                    order_item.save()
    order.save()
