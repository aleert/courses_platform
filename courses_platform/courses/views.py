from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.response import Response

from .models import Module, Item
from .serializers import ModuleSerializer, ItemSerializer


class IsOwnerOrSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or view.get_object().owner == request.user)


class ItemDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class ModuleItemsView(ListCreateAPIView):
    permission_classes = [IsOwnerOrSuperuser, ]
    serializer_class = ItemSerializer

    def get_queryset(self):
        qs = Module.objects.get(pk=self.kwargs['module_pk']).all_items
        return qs


class ModuleView(RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    queryset = Module.objects.all()
    #
    # def get_queryset(self):
    #     qs = Module.objects.filter(pk=self.kwargs['module_pk']).all()
    #     return qs.all()
    #
    # def list(self, request, *args, **kwargs):
    #     qs = self.filter_queryset(self.get_queryset())
    #     return Response(qs.values('items').all())
