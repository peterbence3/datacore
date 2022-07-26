import json
import traceback
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import logging
from MaknounApp import master_page_view 
from MaknounApp import models
from MaknounApp import views
from MaknounApp.arango_agent import ArangoAgent

class SearchEngineView(master_page_view.MasterPageView):
    english_name = 'SearchEngine'
    template_name = 'search_engine'

    def before_render(self, context, request):
        context['searchviews'] = models.View.objects.all().iterator()

    def post_recieved(self, data, request):
        try:
            if not data['query_string'] or len(data['query_string'])==0 or not data['query_fields'] or len(data['query_fields'])==0:
                return super().parse_response(('1', 'الرجاء التأكد من تعبئة كل الخانات المطلوبة'), 'json')

            db = models.Database.objects.filter(english_name=request.user.current_database_name).first()
            if not db:
                return super().parse_response(('1', 'يبدو أن أحدهم قام بحذف قاعدة البيانات الحاليّة'),'json')
            
            arango_agent = ArangoAgent(db.english_name)
            result = arango_agent.full_text_search(data['query_fields'].split(','),data['query_string'])
            result = arango_agent.transform_result_devexpress(result)
            
            return super().parse_response(('0',json.dumps(result)),'json')
        except Exception as e:
            logging.error(traceback.format_exc())
            return super().parse_response(('1' , str(e)),'json')
