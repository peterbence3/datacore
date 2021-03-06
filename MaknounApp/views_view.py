from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from MaknounApp.arango_agent import ArangoAgent

from MaknounApp.templatetags.custom_tags import str2bool 
from MaknounApp import models
from MaknounApp import views
from django.db.models import Q
from MaknounApp import master_entity_view
import json

class ViewsView(master_entity_view.MasterEntityView):
    model = models.View
    english_name = 'Views'
    template_name = 'view'

    def before_render(self, context, request):
        db = models.Database.objects.filter(english_name=request.user.current_database_name).first()
        context['banks'] = models.Bank.objects.filter(database__id=db.id)
        context['relations'] = models.Relation.objects.filter(database__id=db.id)

    def add(self, data, request):
        db = models.Database.objects.filter(english_name=request.user.current_database_name).first()
        if not db:
            return super().parse_response(('1', 'يبدو أن أحدهم قام بحذف قاعدة البيانات الحاليّة'),'json')
            
        if not data["english_name"] or not data["arabic_name"]:
            return super().parse_response(('1', 'الرجاء التأكد من تعبئة كل الخانات المطلوبة'),'json')
        
        oldEntity = self.model.objects.filter(Q(english_name = data['english_name']) | Q(arabic_name = data['arabic_name']), database__id=db.id).first()

        if oldEntity:
            return super().parse_response(('1', 'يوجد ملف بنفس الاسم، الرجاء اختيار اسم آخر'),'json')

        if not data['data_fields'] or len(data['data_fields'])==0:
            return super().parse_response(('1', 'الرجاء التأكد من تعبئة كل الخانات المطلوبة'),'json')

        view = models.View()
        view.english_name = data['english_name']
        view.arabic_name = data['arabic_name']
        view.compressed = str2bool(data['compressed'])
        view.database = db  
        #add arango view here#
        view_fields = []
        for df in data["data_fields"].split(','):
            data_field = models.DataField.objects.filter(id=int(df)).first()
            view_fields.append(data_field)
        ArangoAgent(db.english_name).create_arangosearch_view(view.english_name, view.compressed, view_fields)
        #--------------------#
        view.save()

        for df in data["data_fields"].split(','):
            data_field = models.DataField.objects.filter(id=int(df)).first()
            view.data_fields.add(data_field)
            
        view.save()

        return super().parse_response(('0','تمّت العمليّة بنجاح'),'json')

    def edit(self, data, request):
        db = models.Database.objects.filter(english_name=request.user.current_database_name).first()
        if not db:
            return super().parse_response(('1', 'يبدو أن أحدهم قام بحذف قاعدة البيانات الحاليّة'),'json')
            
        if not data["english_name"] or not data["arabic_name"]:
            return super().parse_response(('1', 'الرجاء التأكد من تعبئة كل الخانات المطلوبة'),'json')

        oldEntity = self.model.objects.filter(english_name = data['english_name'], database__id=db.id).first()
        if not oldEntity:
            return super().parse_response(('1', 'لا يوجد ملف بنفس الاسم'),'json')

        tempentity = self.model.objects.filter(~Q(english_name = data['english_name']), Q(arabic_name = data['arabic_name']), database__id=db.id).first()
        if tempentity:
            return super().parse_response(('1', 'يوجد ملف بنفس الاسم العربي'),'json')

        if not data['data_fields'] or len(data['data_fields'])==0:
            return super().parse_response(('1', 'الرجاء التأكد من تعبئة كل الخانات المطلوبة'),'json')
        
        for df in data["data_fields"].split(','):
            found = False
            for vdf in oldEntity.data_fields.iterator():
                if vdf.id == int(df):
                    found = True
                    break
            if not found:
                d_f = models.DataField.objects.filter(id=int(df)).first()
                #add arango view-field here#
                ArangoAgent(db.english_name).add_arangosearch_view_field(oldEntity.english_name, d_f)
                #--------------------#
                oldEntity.data_fields.add(d_f)

        for vdf in oldEntity.data_fields.iterator():
            found = False
            for df in data["data_fields"].split(','):
                if vdf.id == int(df):
                    found = True
                    break
            if not found:
                #remove arango view-field here#
                ArangoAgent(db.english_name).delete_arangosearch_view_field(oldEntity.english_name, vdf)
                #--------------------#
                oldEntity.data_fields.remove(vdf)

        oldEntity.arabic_name = data['arabic_name']
        oldEntity.compressed = str2bool(data['compressed'])
        oldEntity.save()

        return super().parse_response(('0','تمّت العمليّة بنجاح'),'json')

    def delete(self, data, request):
        db = models.Database.objects.filter(english_name=request.user.current_database_name).first()
        if not db:
            return super().parse_response(('1', 'يبدو أن أحدهم قام بحذف قاعدة البيانات الحاليّة'),'json')
            
        oldEntity = self.model.objects.filter(english_name = data['entityid'], database__id=db.id).first()
        if not oldEntity:
            return super().parse_response(('1', 'لا يوجد ملف بنفس الاسم'),'json')

        ArangoAgent(db.english_name).delete_arangosearch_view(oldEntity.english_name)
        oldEntity.delete()

        return super().parse_response(('0','تمّت العمليّة بنجاح'),'json')

   