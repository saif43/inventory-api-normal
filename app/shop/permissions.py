from rest_framework import permissions
from core import models


def getShop(user):
    if user.is_owner:
        return models.Shop.objects.get(owner=user)

    if user.is_manager or user.is_salesman:
        created_by = user.created_by
        return models.Shop.objects.get(owner=created_by)


class ShopAccessPermission(permissions.BasePermission):
    """Allowing/Restricting user to update their profile"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        has_shop = None

        try:
            if getShop(request.user):
                has_shop = True
        except:
            has_shop = False

        try:
            """IF user is Superuser"""
            if request.user.is_superuser:
                return True

            """IF user is Owner, but doesn't have any shop"""
            if (
                request.user.is_owner
                and not has_shop
                and request.method in ["GET", "POST"]
            ):
                return True

            """IF user is Owner and has a shop"""
            if (
                request.user.is_owner
                and has_shop
                and request.method
                in [
                    "GET",
                    "PUT",
                    "PATCH",
                ]
            ):
                return True

        except:
            return False


class WarehouseAccessPermission(permissions.BasePermission):
    """Allowing/Restricting user to access warehouse"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if (
                    request.user.is_salesman or request.user.is_manager
                ) and request.method in permissions.SAFE_METHODS:
                    return True

        except:
            return False


class ProductAccessPermission(permissions.BasePermission):
    """Allowing/Restricting user to access Product"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if request.user.is_manager and request.method in [
                    "POST",
                    "GET",
                    "PUT",
                    "PATCH",
                ]:
                    return True

                if request.user.is_salesman and request.method == "GET":
                    return True

        except:
            return False


class CustomerAccessPermission(permissions.BasePermission):
    """Allowing/Restricting user to access Customer"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if (
                    request.user.is_salesman or request.user.is_manager
                ) and request.method in permissions.SAFE_METHODS:
                    return True

        except:
            return False


class VendorAccessPermission(permissions.BasePermission):
    """Allowing/Restricting user to access Customer"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if (
                    request.user.is_salesman or request.user.is_manager
                ) and request.method in permissions.SAFE_METHODS:
                    return True

        except:
            return False


class CustomerTransactionPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the transactions"""

    message = "You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if (
                    request.user.is_manager or request.user.is_salesman
                ) and request.method in ["POST", "GET", "PUT", "PATCH"]:
                    return True
        except:
            pass


class CustomerTrasnscationBillPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the transactions"""

    message = "Mehtod allowed: GET | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user) and request.method in [
                "GET",
                "PUT",
                "PATCH",
            ]:
                return True
        except:
            pass


class CustomerTrasnscationDueListPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the transactions"""

    message = "Mehtod allowed: GET | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user) and request.method in permissions.SAFE_METHODS:
                return True
        except:
            pass


class CustomerOrderedItemsPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the transactions"""

    message = "PATCH method not allowed | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if request.method == "PATCH":
                """ we are restricting PATCH method to stock calculation purpose"""
                return False

            if getShop(request.user):
                if request.user.is_owner:
                    return True

                if (
                    request.user.is_manager or request.user.is_salesman
                ) and request.method in ["POST", "GET", "PUT"]:
                    return True
        except:
            pass


class MoveProductPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the transactions"""

    message = "Mehtod allowed: GET | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user) and request.method in ["GET", "POST"]:
                return True
        except:
            pass


class ExpensePermission(permissions.BasePermission):
    """Allowing/Restricting user to access the expense"""

    message = "Mehtod allowed: GET | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user) and request.user.is_owner:
                return True

            if getShop(request.user) and request.method in ["GET", "POST"]:
                return True
        except:
            pass


class ReportViewPermission(permissions.BasePermission):
    """Allowing/Restricting user to access the expense"""

    message = "Mehtod allowed: GET | You must have a shop to access this."

    def has_permission(self, request, obj):
        try:
            if getShop(request.user) and request.method in ["GET", "POST"]:
                return True
        except:
            pass