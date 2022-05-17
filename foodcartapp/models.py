from tkinter.tix import Tree
from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total(self):
        orders_with_totals = self.annotate(
            total=Sum(F('elements__price') * F('elements__quantity'))
        )
        return orders_with_totals


class Order(models.Model):
    PROCESSED = 'PROCESSED'
    UNPROCESSED = 'UNPROCESSED'
    STATUS_TYPE = (
        (PROCESSED, 'Обработанный заказ'),
        (UNPROCESSED, 'Необработанный заказ')
      )
    CASH = 'CASH'
    EPAY = 'EPAY'
    PAYMENT_TYPE = (
        (CASH, 'Наличностью'),
        (EPAY, 'Электронно')
    )
    firstname = models.CharField(
        verbose_name='Имя',
        max_length=50,
    )
    lastname = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
    )
    phonenumber = PhoneNumberField(
        verbose_name='Номер телефона',
        db_index=True,
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=100,
    )
    status = models.CharField(
        choices=STATUS_TYPE,
        max_length=11,
        verbose_name='Статус заказа',
        default=UNPROCESSED,
        db_index=True,
    )
    payment = models.CharField(
        choices=PAYMENT_TYPE,
        max_length=4,
        verbose_name='Способ оплаты',
        default=EPAY,
        db_index=True,
    )
    comment = models.TextField(
        'Комментарий',
        max_length=200,
        blank=True,
    )
    registered_at = models.DateTimeField(verbose_name='Зарегестрирован в',
                                         default=timezone.now, db_index=True)
    called_at = models.DateTimeField(verbose_name='Согласован в',
                                     null=True, blank=True, db_index=True)
    delivered_at = models.DateTimeField(verbose_name='Доставлен в',
                                        null=True, blank=True, db_index=True)
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"Заказ № {self.id}"

    def order(self):
        return f"{self.lastname} {self.firstname} {self.address}"
    order.short_description = 'Заказ'


class OrderElement(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='elements',
        verbose_name="заказ",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='products',
        verbose_name="продукт",
        on_delete=models.SET_DEFAULT,
        default="снят с продажи"
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999),
        ]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f"{self.product.name}"
