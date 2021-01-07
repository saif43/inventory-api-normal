import uuid
import os

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals
from django.utils import timezone

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


def transaction_image_file_path(instance, filename):
    """Generate file path for new transaction image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/transaction/", filename)


class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_kwargs):
        """Creates and saves an user"""
        user = self.model(username=username, **extra_kwargs)
        user.set_password(password)

        if not username:
            raise ValueError("User must have an username")

        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        """Creates and saves a superuser"""
        user = self.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    username = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_salesman = models.BooleanField(default=False)
    created_by = models.ForeignKey("self", on_delete=None, null=True, blank=True)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username


class Shop(models.Model):
    """model for shop object"""

    shopname = models.CharField(max_length=255)
    money = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=None, null=True)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.shopname


class Product(models.Model):
    """Product model"""

    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    buying_price = models.PositiveIntegerField(default=0)
    avg_buying_price = models.PositiveIntegerField(default=0)
    selling_price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    stock_alert_amount = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """Warehouse model"""

    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class WareHouseProducts(models.Model):
    """Model for warehouse products"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("warehouse", "product")


class Customer(models.Model):
    """Customer Model"""

    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15, unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    """Vendor Model"""

    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=15, unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class CustomerTrasnscation(models.Model):
    """Model for the transaction with Customer"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_detail = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, related_name="customer_detail"
    )
    bill = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pk}"


class CustomerOrderedItems(models.Model):
    """Model for keeping customer ordered items"""

    order = models.ForeignKey(CustomerTrasnscation, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    selling_price = models.PositiveIntegerField(default=0)
    custom_selling_price = models.PositiveIntegerField(default=0)
    product_detail = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, related_name="product_detail"
    )
    quantity = models.PositiveIntegerField(default=0)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    bill = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("order", "shop", "product")


class CustomerTrasnscationBill(models.Model):
    """Model for tracking the bill of a transaction"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    order = models.OneToOneField(
        CustomerTrasnscation,
        on_delete=models.CASCADE,
    )
    bill = models.PositiveIntegerField(default=0)
    paid = models.PositiveIntegerField(default=0)
    due = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)


@receiver(signals.post_save, sender=CustomerTrasnscation)
def create_customer_bill(sender, instance, created, **kwargs):
    """Auto create bill, when customer creates a Transaction"""

    if created:
        CustomerTrasnscationBill.objects.create(
            order=instance, paid=0, shop=instance.shop
        )


@receiver(signals.post_save, sender=CustomerOrderedItems)
def update_customer_bill(sender, instance, created, **kwargs):
    """Auto create bill, when customer creates a Transaction"""

    if created:
        bill_object = CustomerTrasnscationBill.objects.filter(order=instance.order)[0]

        order_object = CustomerOrderedItems.objects.filter(order=instance.order)

        bill = 0

        for i in order_object:
            bill += i.bill

        if bill_object.due == 0:
            bill_object.due = bill

        bill_object.bill = bill
        bill_object.save()


class VendorTrasnscation(models.Model):
    """Model for the transaction with Vendor"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=None)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trans {self.pk}---{self.shop}"


class VendorOrderedItems(models.Model):
    """Model for keeping vendor ordered items"""

    order = models.ForeignKey(VendorTrasnscation, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    buying_price = models.PositiveIntegerField(default=0)
    custom_buying_price = models.PositiveIntegerField(default=0)
    product_detail = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        related_name="vendor_product_detail",
    )
    quantity = models.PositiveIntegerField(default=0)
    delivery_warehouse = models.ForeignKey(Warehouse, on_delete=None, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    bill = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True, upload_to=transaction_image_file_path)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("order", "shop", "product", "delivery_warehouse")


class VendorTrasnscationBill(models.Model):
    """Model for tracking the bill of a transaction"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    order = models.OneToOneField(
        VendorTrasnscation,
        on_delete=models.CASCADE,
    )
    bill = models.PositiveIntegerField(default=0)
    paid = models.PositiveIntegerField(default=0)
    due = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)


@receiver(signals.post_save, sender=VendorTrasnscation)
def create_vendor_bill(sender, instance, created, **kwargs):
    """Auto create bill, when vendor creates a Transaction"""

    if created:
        VendorTrasnscationBill.objects.create(
            order=instance, paid=0, shop=instance.shop
        )


@receiver(signals.post_save, sender=VendorOrderedItems)
def update_vendor_bill(sender, instance, created, **kwargs):
    """Auto update bill, when vendor updates a Transaction"""

    if created:
        bill_object = VendorTrasnscationBill.objects.filter(order=instance.order)[0]

        order_object = VendorOrderedItems.objects.filter(order=instance.order)

        bill = 0

        for i in order_object:
            bill += i.bill

        if bill_object.due == 0:
            bill_object.due = bill

        bill_object.bill = bill
        bill_object.save()


class MoveProduct(models.Model):
    """Model for moving product shop to warehouse"""

    options = (
        ("S2W", "Shop to Warehouse"),
        ("W2S", "Warehouse to Shop"),
    )

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    move = models.CharField(max_length=3, choices=options, null=True)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)


class Expense(models.Model):
    """Model for expense"""

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, default="Empty")
    amount = models.PositiveIntegerField(default=0)
    created_timestamp = models.DateTimeField(default=timezone.now, editable=False)
    modified_timestamp = models.DateTimeField(default=timezone.now)
