from core import models
from shop import serializers

from rest_framework import viewsets, status, filters, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from rest_framework.authentication import TokenAuthentication
from django.db.models import Avg, Sum

from shop.permissions import (
    ShopAccessPermission,
    WarehouseAccessPermission,
    ProductAccessPermission,
    CustomerAccessPermission,
    VendorAccessPermission,
    CustomerTransactionPermission,
    CustomerOrderedItemsPermission,
    CustomerTrasnscationBillPermission,
    CustomerTrasnscationDueListPermission,
    MoveProductPermission,
    ExpensePermission,
    ReportViewPermission,
)


def getShop(user):
    if user.is_owner:
        return models.Shop.objects.get(owner=user)

    if user.is_manager or user.is_salesman:
        created_by = user.created_by
        return models.Shop.objects.get(owner=created_by)


class ShopViewSet(viewsets.ModelViewSet):
    """Manage shops"""

    queryset = models.Shop.objects.all()
    serializer_class = serializers.ShopSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (ShopAccessPermission,)

    def get_queryset(self):
        if not self.request.user.is_superuser:
            own_shop = getShop(self.request.user)
            return self.queryset.filter(pk=own_shop.id)

        return self.queryset

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return serializers.AdminShopSerializer

        return serializers.ShopSerializer


class BaseShopAttr(viewsets.ModelViewSet):
    """Base class for WarehouseViewSet and ProductViewSet"""

    authentication_classes = (TokenAuthentication,)

    def perform_create(self, serializer):
        own_shop = getShop(self.request.user)
        print(own_shop)
        serializer.save(shop=own_shop)

    def get_queryset(self):
        if not self.request.user.is_superuser:
            own_shop = getShop(self.request.user)
            return self.queryset.filter(shop=own_shop)

        return self.queryset


class WarehouseViewSet(BaseShopAttr):
    """Manage warehouses"""

    queryset = models.Warehouse.objects.all()
    serializer_class = serializers.WarehouseSerializer
    permission_classes = (WarehouseAccessPermission,)


class WarehouseProductsView(BaseShopAttr):
    """Manage products in Warehouse"""

    queryset = models.WareHouseProducts.objects.all()
    serializer_class = serializers.WarehouseProductsSerializer
    permission_classes = (WarehouseAccessPermission,)


class ProductViewSet(BaseShopAttr):
    """Manage products"""

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (ProductAccessPermission,)


class SalesmanViewSet(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        queryset = models.User.objects.all()
        queryset = queryset.filter(
            created_by=getShop(self.request.user).owner, is_salesman=True
        )
        return Response(serializers.SalesmanSerializer(queryset, many=True).data)


class ManagerViewSet(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        queryset = models.User.objects.all()
        queryset = queryset.filter(
            created_by=getShop(self.request.user).owner, is_manager=True
        )
        return Response(serializers.SalesmanSerializer(queryset, many=True).data)


class CustomerViewSet(BaseShopAttr):
    """Manage customer"""

    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    permission_classes = (CustomerAccessPermission,)


class VendorViewSet(BaseShopAttr):
    """Manage vendor"""

    queryset = models.Vendor.objects.all()
    serializer_class = serializers.VendorSerializer
    permission_classes = (VendorAccessPermission,)


class CustomerTrasnscationViewSet(BaseShopAttr):
    """Manage transaction of customer"""

    queryset = models.CustomerTrasnscation.objects.all()
    serializer_class = serializers.CustomerTrasnscationSerializer
    permission_classes = (CustomerTransactionPermission,)


class CustomerOrderedItemsViewSet(viewsets.ModelViewSet):
    """Manage customer ordered items of a single order"""

    authentication_classes = (TokenAuthentication,)
    queryset = models.CustomerOrderedItems.objects.all()
    serializer_class = serializers.CustomerOrderedItemsSerializer
    permission_classes = (CustomerOrderedItemsPermission,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ("=order__id",)
    """
    '^' Starts-with search.
    '=' Exact matches.
    '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
    '$' Regex search.
    """

    def perform_create(self, serializer):
        own_shop = getShop(self.request.user)
        serializer.save(shop=own_shop)

    def get_queryset(self):
        own_shop = getShop(self.request.user)
        return self.queryset.filter(shop=own_shop)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return serializers.CustomerOrderedItemsUpdateSerializer

        return self.serializer_class

    # def retrieve(self, request, *args, **kwargs):
    #     """overriding retrieve function, to get result of list of transaction filtered by order_id"""

    #     # do your customization here
    #     # instance = self.get_object()
    #     # # instance = CustomerOrderedItems.objects.filter(order=self.kwargs[])
    #     # print(instance.id)
    #     try:
    #         # http://api/kwargs['pk']
    #         transaction = CustomerTrasnscation.objects.filter(pk=kwargs['pk'])

    #         instance = CustomerOrderedItems.objects.filter(
    #             order=transaction[0])

    #         serialized_data = []

    #         for i in instance:
    #             serialize = self.get_serializer(i)
    #             serialized_data.append(serialize.data)

    #         return Response(serialized_data, status=status.HTTP_200_OK)

    #     except:
    #         return Response(status=status.HTTP_404_NOT_FOUND)


class CustomerTrasnscationBillViewSet(BaseShopAttr):
    """Manage bill of a transaction"""

    queryset = models.CustomerTrasnscationBill.objects.all()
    serializer_class = serializers.CustomerTrasnscationBillSerializer
    permission_classes = (CustomerTrasnscationBillPermission,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ("=order__id",)
    """
    '^' Starts-with search.
    '=' Exact matches.
    '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
    '$' Regex search.
    """


class CustomerDueListViewSet(BaseShopAttr):
    """Show customer transactions who has due"""

    serializer_class = serializers.CustomerTrasnscationBillSerializer
    permission_classes = (CustomerTrasnscationDueListPermission,)

    def get_queryset(self):
        own_shop = getShop(self.request.user)
        return models.CustomerTrasnscationBill.objects.filter(shop=own_shop, due__gt=0)


class VendorTrasnscationViewSet(BaseShopAttr):
    """Manage transaction of Vendor"""

    queryset = models.VendorTrasnscation.objects.all()
    serializer_class = serializers.VendorTrasnscationSerializer
    permission_classes = (CustomerTransactionPermission,)


class VendorOrderedItemsViewSet(viewsets.ModelViewSet):
    """Manage Vendor ordered items of a single order"""

    authentication_classes = (TokenAuthentication,)
    queryset = models.VendorOrderedItems.objects.all()
    serializer_class = serializers.VendorOrderedItemsSerializer
    permission_classes = (CustomerOrderedItemsPermission,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ("=order__id",)

    def get_serializer_class(self):
        """return appropriate serializer"""
        if self.action == "retrieve":
            return serializers.VendorOrderedItemsSerializer
        elif self.action == "upload_image":
            return serializers.VendorTrasnscationImageSerializer

        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """upload and image to the vendor transaction"""
        transaction = self.get_object()
        serializer = self.get_serializer(transaction, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        own_shop = getShop(self.request.user)
        serializer.save(shop=own_shop)

    def get_queryset(self):
        own_shop = getShop(self.request.user)
        return self.queryset.filter(shop=own_shop)


class VendorTrasnscationBillViewSet(BaseShopAttr):
    """Manage bill of a transaction"""

    queryset = models.VendorTrasnscationBill.objects.all()
    serializer_class = serializers.VendorTrasnscationBillSerializer
    permission_classes = (CustomerTrasnscationBillPermission,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ("=order__id",)
    """
    '^' Starts-with search.
    '=' Exact matches.
    '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
    '$' Regex search.
    """


class VendorDueListViewSet(BaseShopAttr):
    """Show Vendor transactions who has due"""

    serializer_class = serializers.VendorTrasnscationBillSerializer
    permission_classes = (CustomerTrasnscationDueListPermission,)

    def get_queryset(self):
        own_shop = getShop(self.request.user)
        return models.VendorTrasnscationBill.objects.filter(shop=own_shop, due__gt=0)


class MoveProductViewSet(BaseShopAttr):
    """Moving products shop to warehouse"""

    queryset = models.MoveProduct.objects.all()
    serializer_class = serializers.MoveProductSerializer
    permission_classes = (MoveProductPermission,)


class ExpenseViewSet(BaseShopAttr):
    """Moving products shop to warehouse"""

    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer
    permission_classes = (ExpensePermission,)


class ReportViewSet(viewsets.ViewSet):
    """Shows purchase report group by day"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (ReportViewPermission,)

    def getModel(self):
        pass

    # Ref of Group by SUM
    # https://stackoverflow.com/questions/18144907/how-to-rename-fields-of-an-annotated-query/38104242

    def list(self, request, **kwargs):

        user = models.User.objects.get(id=request.user.id)
        own_shop = getShop(user)

        if kwargs:
            # if user want to get report of a specific date
            date = kwargs["date"]

            queryset = (
                self.getModel()
                .objects.filter(shop=own_shop)
                .values("created_timestamp__date")
                .annotate(bill=Sum("bill"))
                .filter(created_timestamp__date=date)
            )

            queryset = [
                {"date": x["created_timestamp__date"], "bill": x["bill"]}
                for x in queryset
            ]
            return Response(queryset)

        # if user want to see all report
        queryset = (
            self.getModel()
            .objects.filter(shop=own_shop)
            .values("created_timestamp__date")
            .annotate(bill=Sum("bill"))
        )

        queryset = [
            {"date": x["created_timestamp__date"], "bill": x["bill"]} for x in queryset
        ]
        return Response(queryset)


class PurchaseReportViewSet(ReportViewSet):
    def getModel(self):
        return models.VendorOrderedItems


class SellReportViewSet(ReportViewSet):
    def getModel(self):
        return models.CustomerOrderedItems