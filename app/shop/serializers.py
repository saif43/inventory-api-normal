from rest_framework import serializers
from core import models


def getShop(user):
    if user.is_owner:
        return models.Shop.objects.get(owner=user)

    if user.is_manager or user.is_salesman:
        created_by = user.created_by
        return models.Shop.objects.get(owner=created_by)


class ShopSerializer(serializers.ModelSerializer):
    """Serializer for shop"""

    class Meta:
        model = models.Shop
        fields = (
            "id",
            "shopname",
            "money",
            "owner",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "owner", "created_timestamp", "modified_timestamp")


class AdminShopSerializer(serializers.ModelSerializer):
    """Admin(Superuser) Serializer for shop"""

    def __init__(self, *args, **kwargs):
        """Shows owner for superuser only"""

        super(AdminShopSerializer, self).__init__(*args, **kwargs)
        self.fields["owner"].queryset = models.User.objects.filter(is_owner=True)

    class Meta:
        model = models.Shop
        fields = (
            "id",
            "shopname",
            "money",
            "owner",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "created_timestamp", "modified_timestamp")

    def validate(self, data):
        owner = data["owner"]

        if not owner:
            raise serializers.ValidationError("No owner has been selected.")

        return data


class WarehouseSerializer(serializers.ModelSerializer):
    """Serializer for warehouse"""

    # if we like to show shop details
    # shop = ShopSerializer(read_only=True)

    class Meta:
        model = models.Warehouse
        fields = ("id", "name", "shop", "created_timestamp", "modified_timestamp")
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class WarehouseProductsSerializer(serializers.ModelSerializer):
    """Serializer for warehouse products"""

    class Meta:
        model = models.WareHouseProducts
        fields = (
            "id",
            "warehouse",
            "product",
            "quantity",
            "shop",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")

    def to_representation(self, instance):
        """For the nested represtation"""

        response = super().to_representation(instance)
        response["product"] = ProductSerializer(instance.product).data
        response["warehouse"] = WarehouseSerializer(instance.product).data

        response["product"].pop("buying_price")
        response["product"].pop("stock")
        response["product"].pop("shop")

        response["warehouse"].pop("shop")
        return response


class SalesmanSerializer(serializers.Serializer):
    """Serializer for salesman list"""

    id = serializers.IntegerField()
    username = serializers.CharField()
    mobile = serializers.CharField()


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product"""

    class Meta:
        model = models.Product
        fields = (
            "id",
            "name",
            "buying_price",
            "avg_buying_price",
            "selling_price",
            "stock",
            "stock_alert_amount",
            "shop",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "shop",
            "avg_buying_price",
            "created_timestamp",
            "modified_timestamp",
        )


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer"""

    class Meta:
        model = models.Customer
        fields = (
            "id",
            "name",
            "contact",
            "shop",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Customer"""

    class Meta:
        model = models.Vendor
        fields = (
            "id",
            "name",
            "contact",
            "shop",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class CustomerTrasnscationSerializer(serializers.ModelSerializer):
    """Serializer for customer product transaction"""

    def __init__(self, *args, **kwargs):
        """Filter customers by shop"""

        super(CustomerTrasnscationSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(user=self.context["request"].user)
        self.fields["customer"].queryset = models.Customer.objects.filter(shop=own_shop)

    class Meta:
        model = models.CustomerTrasnscation
        fields = (
            "id",
            "shop",
            "customer",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class CustomerOrderedItemsSerializer(serializers.ModelSerializer):
    """Serializer for ordered products"""

    def validate(self, data):
        product = data["product"]
        data["product_detail"] = data["product"]
        # data["selling_price"] = product.selling_price
        quantity = data["quantity"]
        order = data["order"]

        if product is None:
            raise serializers.ValidationError("No product has been selected.")
        if order is None:
            raise serializers.ValidationError("No order has been selected.")

        exists = models.CustomerOrderedItems.objects.filter(
            product=product, order=order
        )

        data["bill"] = data["custom_selling_price"] * quantity

        if exists:
            raise serializers.ValidationError("Duplicate entires not allowed.")

        stock = product.stock - quantity

        if stock < 0:
            raise serializers.ValidationError("Insufficient stock.")

        product.stock = stock
        product.save()

        return data

    def __init__(self, *args, **kwargs):
        """Filter customers by shop"""

        super(CustomerOrderedItemsSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(user=self.context["request"].user)
        self.fields["product"].queryset = models.Product.objects.filter(shop=own_shop)
        self.fields["order"].queryset = models.CustomerTrasnscation.objects.filter(
            shop=own_shop
        )

    class Meta:
        model = models.CustomerOrderedItems
        fields = (
            "id",
            "order",
            "shop",
            "product",
            "product_detail",
            "custom_selling_price",
            "quantity",
            "bill",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "shop",
            "bill",
            "product_detail",
            "created_timestamp",
            "modified_timestamp",
        )

    def to_representation(self, instance):
        """For the nested represtation"""

        response = super().to_representation(instance)
        response["product_detail"] = ProductSerializer(instance.product).data
        response["product_detail"].pop("buying_price")
        response["product_detail"].pop("shop")
        return response


class CustomerOrderedItemsUpdateSerializer(CustomerOrderedItemsSerializer):
    """Update Serializer for ordered products"""

    def validate(self, data):
        product = data["product"]
        quantity = data["quantity"]
        order = data["order"]

        if product is None:
            raise serializers.ValidationError("No product has been selected.")
        if order is None:
            raise serializers.ValidationError("No order has been selected.")

        exists = models.CustomerOrderedItems.objects.filter(
            product=product, order=order
        )[0]

        stock = product.stock + exists.quantity
        stock -= quantity

        data["bill"] = product.selling_price * quantity

        if stock < 0:
            raise serializers.ValidationError("Insufficient stock.")

        product.stock = stock
        product.save()

        return data


class CustomerTrasnscationBillSerializer(serializers.ModelSerializer):
    """Serializer for Customer transaction bill"""

    def __init__(self, *args, **kwargs):
        """Filter customers by shop"""

        super(CustomerTrasnscationBillSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(self.context["request"].user)
        self.fields["order"].queryset = models.CustomerTrasnscation.objects.filter(
            shop=own_shop
        )

    def validate(self, data):
        order = self.instance.order
        total_bill = 0

        previous_paid = models.CustomerTrasnscationBill.objects.get(
            id=self.instance.id
        ).paid
        new_paid = data["paid"]

        shop = self.instance.shop

        orders = models.CustomerOrderedItems.objects.filter(order=order)

        for i in orders:
            total_bill += i.bill

        data["bill"] = total_bill
        data["due"] = total_bill - previous_paid - new_paid
        data["paid"] = previous_paid + new_paid

        if data["paid"] > total_bill:
            raise serializers.ValidationError("Over paid")

        shop.money += new_paid
        shop.save()

        return data

    class Meta:
        model = models.CustomerTrasnscationBill
        fields = (
            "id",
            "shop",
            "order",
            "bill",
            "paid",
            "due",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "shop",
            "order",
            "bill",
            "due",
            "created_timestamp",
            "modified_timestamp",
        )


class VendorTrasnscationSerializer(serializers.ModelSerializer):
    """Serializer for vendor product transaction"""

    def __init__(self, *args, **kwargs):
        """Filter vendors by shop"""

        super(VendorTrasnscationSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(self.context["request"].user)
        self.fields["vendor"].queryset = models.Vendor.objects.filter(shop=own_shop)

    class Meta:
        model = models.VendorTrasnscation
        fields = ("id", "shop", "vendor", "created_timestamp", "modified_timestamp")
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class VendorTrasnscationImageSerializer(serializers.ModelSerializer):
    """Serializer for vendor product transaction"""

    class Meta:
        model = models.VendorOrderedItems
        fields = (
            "id",
            "image",
        )
        read_only_fields = ("id",)


class VendorOrderedItemsSerializer(serializers.ModelSerializer):
    """Serializer for ordered products"""

    def validate(self, data):
        product = data["product"]
        data["product_detail"] = data["product"]
        # data["buying_price"] = product.buying_price
        quantity = data["quantity"]
        order = data["order"]
        warehouse = data["delivery_warehouse"]

        if product is None:
            raise serializers.ValidationError("No product has been selected.")
        if order is None:
            raise serializers.ValidationError("No order has been selected.")
        if warehouse is None:
            raise serializers.ValidationError("No warehouse has been selected.")

        data["bill"] = data["custom_buying_price"] * quantity

        stock = product.stock + quantity

        """Changing Product avg_buying_price"""
        if product.avg_buying_price == 0:
            product.avg_buying_price = data["custom_buying_price"]
        else:
            product.avg_buying_price = (
                data["custom_buying_price"] + product.avg_buying_price
            ) / 2

        product.stock = stock
        product.save()

        return data

    def __init__(self, *args, **kwargs):
        """Filter vendors by shop"""

        super(VendorOrderedItemsSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(self.context["request"].user)
        self.fields["product"].queryset = models.Product.objects.filter(shop=own_shop)
        self.fields["order"].queryset = models.VendorTrasnscation.objects.filter(
            shop=own_shop
        )
        self.fields["delivery_warehouse"].queryset = models.Warehouse.objects.filter(
            shop=own_shop
        )

    class Meta:
        model = models.VendorOrderedItems
        fields = (
            "id",
            "order",
            "shop",
            "product",
            "buying_price",
            "custom_buying_price",
            "product_detail",
            "delivery_warehouse",
            "quantity",
            "bill",
            "image",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "shop",
            "bill",
            "product_detail",
            "buying_price",
            "image",
            "created_timestamp",
            "modified_timestamp",
        )

    def to_representation(self, instance):
        """For the nested represtation"""

        response = super().to_representation(instance)
        response["product_detail"] = ProductSerializer(instance.product).data
        response["product_detail"].pop("selling_price")
        response["product_detail"].pop("shop")
        return response


class VendorTrasnscationBillSerializer(serializers.ModelSerializer):
    """Serializer for vendor transaction bill"""

    def __init__(self, *args, **kwargs):
        """Filter vendors by shop"""

        super(VendorTrasnscationBillSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(self.context["request"].user)
        self.fields["order"].queryset = models.VendorTrasnscation.objects.filter(
            shop=own_shop
        )

    def validate(self, data):
        order = self.instance.order

        previous_paid = models.VendorTrasnscationBill.objects.get(
            id=self.instance.id
        ).paid
        new_paid = data["paid"]

        shop = self.instance.shop
        total_bill = 0

        orders = models.VendorOrderedItems.objects.filter(order=order)

        for i in orders:
            total_bill += i.bill

        if new_paid > shop.money:
            raise serializers.ValidationError("Not enough money.")

        data["bill"] = total_bill
        data["due"] = total_bill - previous_paid - new_paid
        data["paid"] = previous_paid + new_paid

        if data["paid"] > total_bill:
            raise serializers.ValidationError("Over paid")

        shop.money -= new_paid
        shop.save()

        return data

    class Meta:
        model = models.VendorTrasnscationBill
        fields = (
            "id",
            "shop",
            "order",
            "bill",
            "paid",
            "due",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "order",
            "shop",
            "bill",
            "due",
            "created_timestamp",
            "modified_timestamp",
        )


class MoveProductSerializer(serializers.ModelSerializer):
    """Serializer for moving product shop to warehouse"""

    def __init__(self, *args, **kwargs):
        super(MoveProductSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        try:
            warehouse = data["warehouse"]
            product = data["product"]
            quantity = data["quantity"]
            move = data["move"]

            if not move:
                raise serializers.ValidationError("Please fulfill all fields.")
        except:
            raise serializers.ValidationError("Please fulfill all fields.")

        warehouse_stock = models.WareHouseProducts.objects.filter(
            warehouse=warehouse, product=product
        )

        shop_product = models.Product.objects.get(id=product.pk)

        if move == "S2W":
            if shop_product.stock < quantity:
                raise serializers.ValidationError(
                    "Shop does not have this amount of product."
                )

            if warehouse_stock:
                warehouse_stock = warehouse_stock[0]

                warehouse_stock.quantity += quantity
                shop_product.stock -= quantity

                warehouse_stock.save()
                shop_product.save()
            else:
                own_shop = getShop(self.context["request"].user)
                models.WareHouseProducts.objects.create(
                    warehouse=warehouse,
                    product=product,
                    quantity=quantity,
                    shop=own_shop,
                )

                shop_product.stock -= quantity
                shop_product.save()
        elif move == "W2S":

            if warehouse_stock:
                warehouse_stock = warehouse_stock[0]

                if warehouse_stock.quantity < quantity:
                    raise serializers.ValidationError(
                        "Warehouse does not have this amount of product."
                    )

                warehouse_stock.quantity -= quantity
                shop_product.stock += quantity

                warehouse_stock.save()
                shop_product.save()
            else:
                models.WareHouseProducts.objects.create(
                    warehouse=warehouse, product=product, quantity=0
                )
                raise serializers.ValidationError(
                    "Warehouse does not have this amount of product."
                )

        return data

    def __init__(self, *args, **kwargs):
        """Filter by shop"""

        super(MoveProductSerializer, self).__init__(*args, **kwargs)

        own_shop = getShop(self.context["request"].user)
        self.fields["warehouse"].queryset = models.Warehouse.objects.filter(
            shop=own_shop
        )
        self.fields["product"].queryset = models.Product.objects.filter(shop=own_shop)

    class Meta:
        model = models.MoveProduct
        fields = (
            "id",
            "shop",
            "warehouse",
            "product",
            "quantity",
            "move",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = ("id", "shop", "created_timestamp", "modified_timestamp")


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense"""

    class Meta:
        model = models.Expense
        fields = (
            "id",
            "shop",
            "subject",
            "amount",
            "created_timestamp",
            "modified_timestamp",
        )
        read_only_fields = (
            "id",
            "shop",
            "created_timestamp",
            "modified_timestamp",
        )
