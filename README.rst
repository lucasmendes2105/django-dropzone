=====
Dropzone
=====

Dropzone is a Django app that facilitates integration with Django Admin and Dropzone.js

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "dropzone" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'dropzone',
    )

2. Import the classes and then extend like this::

    from dropzone.admin import DropZoneMixin, DropZoneAdmin, DropZoneSuitMixin

    class GaleriaAdmin(DropZoneSuitMixin, admin.ModelAdmin):
        modelDropZone = Foto

    class FotoAdmin(DropZoneAdmin):
        modelParent = Galeria

        def get_queryset_parent(self, request, pk):
            from django.shortcuts import get_object_or_404
            return get_object_or_404(self.modelParent, pk=pk, site=request.user)        

3. Done!