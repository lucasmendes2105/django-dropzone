from django.contrib import admin
from django.urls import reverse, path
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import json
import pdb

# Register your models here.


class DropZoneMixin(object):
    change_form_template = 'dropzone/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['opts_dz'] = self.modelDropZone._meta
        return super(DropZoneMixin, self).change_view(request, object_id, form_url, extra_context=extra_context)


class DropZoneAdminAbsctract(object):

    def get_model_name(self):
        options = self.model._meta
        if hasattr(options, 'model_name'):
            return getattr(options, 'model_name')
        return getattr(options, 'module_name')

    def get_dz_list_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_list' % (app_name, self.get_model_name())

    def get_dz_upload_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_upload' % (app_name, self.get_model_name())

    def get_dz_delete_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_delete' % (app_name, self.get_model_name())


class DropZoneAdminMixin(DropZoneAdminAbsctract):
    maxFilesize = 5  # 5MB
    acceptedFiles = "image/*"
    add_form_template = 'admin/change_form.html'
    change_form_template = 'dropzone/upload_mixin.html'
    default_order_field = 'order'

    class Media:
        js = (
            'dropzone/dropzone.min.js',
        )
        css = {
            'all': ['dropzone/dropzone.min.css', ],
        }

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload-file/<int:parent_id>/', self.upload_file, name=self.get_dz_upload_name()),
            path('delete-file/<int:parent_id>/<int:pk>/', self.delete_file, name=self.get_dz_delete_name()),
        ]
        return my_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['url_upload_file'] = reverse('admin:%s' % self.get_dz_upload_name(), args=[object_id, ])
        extra_context['arquivos'] = json.dumps(self.get_arquivos(request, object_id), ensure_ascii=False)
        extra_context['maxFilesize'] = self.maxFilesize
        extra_context['acceptedFiles'] = self.acceptedFiles
        if self.ordering_view:
            extra_context['ordering_url'] = '{}?{}={}'.format(reverse(self.ordering_view), self.dropzone_parent_name, object_id)
        return super(DropZoneAdminMixin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_arquivos(self, request, object_id):
        kwargs = {self.dropzone_parent_name: object_id}
        files = self.modelDropZone.objects.filter(**kwargs).all()
        data = []
        for f in files:
            delete_url = reverse('admin:%s' % self.get_dz_delete_name(), args=[object_id, f.id, ])
            try:
                size = f.image.size
            except Exception as e:
                size = 0
            from django_thumbor import generate_url
            data.append({'id': f.id, 'delete_url': delete_url, 'name': f.filename, 'size': size, 'url': generate_url(f.image.url, width=120, height=120)})
        return data

    def get_model_name_parent(self):
        return self.model._meta.model_name

    def upload_file(self, request, parent_id):
        parent = self.get_object(request, parent_id)
        kwargs = {self.dropzone_parent_name: parent_id}

        posted_file = request.FILES.get('file')
        f = self.modelDropZone(image=posted_file, **kwargs)
        f.save()

        if self.ordering_view:
            f.order = f.id
            f.save(update_fields=['order', ])

        delete_url = reverse('admin:%s' % self.get_dz_delete_name(), args=[parent_id, f.id, ])
        response = {'id': f.id, 'delete_url': delete_url}
        return HttpResponse(json.dumps(response), content_type="application/json")

    @csrf_exempt
    def delete_file(self, request, parent_id, pk):
        parent = self.get_object(request, parent_id)
        kwargs = {self.dropzone_parent_name: parent_id}

        obj = get_object_or_404(self.modelDropZone, pk=pk, **kwargs)
        obj.delete()
        return HttpResponse('')


class DropZoneAdmin(admin.ModelAdmin):
    title = 'Enviar Fotos'
    maxFilesize = 5  # 5MB
    acceptedFiles = "image/*"

    class Media:
        js = (
            'js/dropzone/dropzone.min.js',
        )
        css = {
            'all': ['js/dropzone/dropzone.min.css', ],
        }

    def get_urls(self):
        urls = super(DropZoneAdmin, self).get_urls()
        my_urls = [
            path('upload/<int:parent_id>/', self.upload_files, name=self.get_dz_list_name()),
            path('upload-file/<int:parent_id>/', self.upload_file, name=self.get_dz_upload_name()),
            path('delete-file/<int:pk>/', self.delete_file, name=self.get_dz_delete_name()),
        ]
        return my_urls + urls

    def get_model_name(self):
        options = self.model._meta
        if hasattr(options, 'model_name'):
            return getattr(options, 'model_name')
        return getattr(options, 'module_name')

    def get_dz_list_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_list' % (app_name, self.get_model_name())

    def get_dz_upload_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_upload' % (app_name, self.get_model_name())

    def get_dz_delete_name(self):
        app_name = self.model._meta.app_label
        return '%s_%s_dz_delete' % (app_name, self.get_model_name())

    def has_upload_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def upload_files(self, request, parent_id):
        parent = self.get_queryset_parent(request, parent_id)

        if not self.has_upload_permission(request, parent):
            raise PermissionDenied

        url_upload_file = reverse('admin:%s' % self.get_dz_upload_name(), args=[parent_id, ])
        arquivos = json.dumps(self.get_arquivos(request, parent), ensure_ascii=False)

        c = {
            'url_upload_file': url_upload_file,
            'arquivos': arquivos,
            'title': self.title,
            'opts_parent': self.modelParent._meta,
            'parent': parent,
            'maxFilesize': self.maxFilesize,
            'acceptedFiles': self.acceptedFiles,
            'is_popup': request.GET.get('_popup')
        }

        return render(request, 'dropzone/upload.html', c)

    def get_arquivos(self, request, parent):
        kwargs = {self.modelParent._meta.model_name: parent}
        files = self.get_queryset(request).filter(**kwargs).all()
        data = []
        for f in files:
            delete_url = reverse('admin:%s' % self.get_dz_delete_name(), args=[f.id, ])
            try:
                size = f.image.size
            except Exception as e:
                size = 0
            from django_thumbor import generate_url
            data.append({'id': f.id, 'delete_url': delete_url, 'name': f.filename, 'size': size, 'url': generate_url(f.image.url, width=120, height=120)})
        return data

    def upload_file(self, request, parent_id):
        parent = self.get_queryset_parent(request, parent_id)
        posted_file = request.FILES.get('file')
        kwargs = {self.modelParent._meta.model_name: parent}

        f = self.model(image=posted_file, **kwargs)
        f.save()
        delete_url = reverse('admin:%s' % self.get_dz_delete_name(), args=[f.id, ])
        response = {'id': f.id, 'delete_url': delete_url}
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_model_parent(self):
        return self.modelParent

    def get_queryset_parent(self, request, pk):
        return get_object_or_404(self.modelParent, pk=pk)

    @csrf_exempt
    def delete_file(self, request, pk):
        obj = get_object_or_404(self.get_queryset(request), pk=pk)
        obj.delete()
        return HttpResponse('')
