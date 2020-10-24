from django.urls import path, include
from shop import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("shop", views.ShopViewSet)
router.register("warehouse", views.WarehouseViewSet)
router.register("product", views.ProductViewSet)
router.register("customer", views.CustomerViewSet)
router.register("vendor", views.VendorViewSet)
router.register("warehouse_products", views.WarehouseProductsView)
router.register("customer_transactions", views.CustomerTrasnscationViewSet)
router.register("customer_transactions_detail", views.CustomerOrderedItemsViewSet)
router.register("customer_bill", views.CustomerTrasnscationBillViewSet)
router.register("customer_bill_due", views.CustomerDueListViewSet, basename="customer_bill_due")
router.register("vendor_transactions", views.VendorTrasnscationViewSet)
router.register("vendor_transactions_detail", views.VendorOrderedItemsViewSet)
router.register("vendor_bill", views.VendorTrasnscationBillViewSet)
router.register("vendor_bill_due", views.VendorDueListViewSet, basename="vendor_bill_due")
router.register("move_product", views.MoveProductViewSet)
router.register("expense", views.ExpenseViewSet)
router.register("purchase_report", views.PurchaseReportViewSet, basename='purchase_report')
router.register("sell_report", views.SellReportViewSet, basename='sell_report')



app_name = "shop"

urlpatterns = [
    path("", include(router.urls)),
    path("salesman/", views.SalesmanViewSet.as_view(), name="salesman"),
    path("manager/", views.ManagerViewSet.as_view(), name="manager"),
    path("purchase_report/<str:date>/", views.PurchaseReportViewSet.as_view({'get': 'list'})),
    path("sell_report/<str:date>/", views.SellReportViewSet.as_view({'get': 'list'})),
]
