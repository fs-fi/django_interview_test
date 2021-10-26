from django.contrib import admin

from restbucks.models import Product, ProductAttribute, ProductAttributeOption, Order, OrderItem
from restbucks.admin_panel import admin_changelist_link, admin_link
from django_fsm import can_proceed


class ProductAttributeInline(admin.StackedInline):
    model = ProductAttribute
    extra = 1
    fields = ('name',)


class ProductAttributeOptionInline(admin.StackedInline):
    model = ProductAttributeOption
    extra = 1
    fields = ('name',)


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'count', 'selected_options')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'unit_price']
    list_display_links = ['product_name']
    search_fields = ['product_name']
    prepopulated_fields = {'slug': ['product_name']}



@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_options']
    list_display_links = ['name']
    search_fields = ['name']
    inlines = [ProductAttributeOptionInline]

    @admin_changelist_link(
        'options',
        'options',
        query_string=lambda c: 'attribute_id={}'.format(c.pk)
    )
    def get_options(self, section):
        return 'options'


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_attribute']
    list_display_links = ['name']
    search_fields = ['name']

    @admin_link('attribute', 'ProductAttribute')
    def get_attribute(self, attribute):
        return attribute.name


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'state']
    list_display_links = ['id']
    inlines = [OrderItemInline]
    actions = ['change_to_prepare', 'change_to_ready', 'change_to__delivered', 'change_to__canceled']
    readonly_fields = ('state',)

    def change_to_prepare(self, request, queryset):
        for order in queryset.all():
            if can_proceed(order.prepare):
                order.prepare()
                order.save()

    def change_to_ready(self, request, queryset):
        for order in queryset.all():
            if can_proceed(order.ready):
                order.ready()
                order.save()

    def change_to_delivered(self, request, queryset):
        for order in queryset.all():
            if can_proceed(order.deliver):
                order.deliver()
                order.save()

    def change_to_canceled(self, request, queryset):
        for order in queryset.all():
            if can_proceed(order.cancel):
                order.cancel()
                order.save()

    