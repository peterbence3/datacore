from pickle import FALSE, TRUE
from django import template

from MaknounApp.models import Bank, Relation

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    if value and value.strip():
        parts = value.split(arg)
        result = []
        for p in parts:
            if p and p.strip():
                result.append(p.strip())
        return result
    return []

@register.filter(name='translate_permission')
def translate_permission(value):
    if value and value.strip():
        pages_dictionary= {
            'Home':'الرئيسيّة',
            'Banks':'بنوك المعلومات',
            'Relations':'العلاقات',
            'Import':'استيراد البيانات',
            'Views':'ملفّات محرّك البحث',
            'SearchEngine':'محرّك البحث',
            'AdvancedSearch':'بحث متقدّم',
            'GraphSearch':'بحث في العلاقات',
            'Users':'المستخدمين',
            'Settings':'الإعدادات',
        }
        return pages_dictionary[value.strip()]
    return value

@register.filter(name='fetch_all')
def fetch_all(value):
    if value:
        return value.all()
    return []

@register.filter(name='iterator')
def iterator(value):
    if value:
        return value.iterator()
    return []

@register.filter(name='select')
def select(array, value):
    selection = []
    if array and value:
        for a in array:
            selection.append(getattr(a, value))
    return selection

@register.filter(name='fetch_by_name')
def fetch_by_name(value, field_name):
    if value:
        try:
            return getattr(value, field_name).all()
        except Exception as e:
            return []
    return []

@register.filter(name='count')
def count(value):
    if value:
        if value.count() > 0:
            return True;
    return FALSE

@register.filter(name='equals')
def equals(value, arg):
    if value and arg and str(value).lower() == arg.lower():
        return True
    return False

@register.filter(name='if_equals_else')
def if_equals_else(value, args):
    if value and args:
        arg_list = [arg.strip() for arg in args.split(',')]
        if str(value).lower() == arg_list[0].lower():
            return arg_list[1]
        else:
            return arg_list[2]
    return ""

@register.filter(name='if_else')
def if_equals(value, args):
    if args:
        arg_list = [arg.strip() for arg in args.split(',')]
        if value:
            return arg_list[0]
        else:
            return arg_list[1]
    return ""

@register.filter(name='if_not_else')
def if_not_equals(value, args):
    if args:
        arg_list = [arg.strip() for arg in args.split(',')]
        if not value:
            return arg_list[0]
        else:
            return arg_list[1]
    return ""

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary[key]

@register.filter(name='str_or_default')
def str_or_default(str, default):
    if not str or len(str) == 0:
        return default;
    return str

@register.filter(name='str2bool')
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

@register.filter(name='array_to_string_no_brackets')
def array_to_string_no_brackets(v):
    result = ''
    if v and len(v)>0:
        for i in v:
            result += str(i) + ','
        result = result[:-1]
    return result

@register.filter(name='length')
def length(v):
    if v:
        return len(v)
    return 0

@register.filter(name='loop_count')
def loop_count(v):
    if v:
        count = 0
        for i in v:
            count+=1
        return count
    return 0

@register.filter(name='get_owner_arango_en_name')
def get_owner_arango_en_name(owner):
    if owner:
        if isinstance(owner, Bank):
            return 'col_' + owner.english_name
        elif isinstance(owner, Relation):
            return 'edge_' + owner.english_name
        else:
            return owner.english_name
    return owner

@register.filter(name='to_arabic_data_type')
def to_arabic_data_type(v):
    if v:
        if v.lower() == 'string':
            return 'نص'
        elif v.lower() == 'bool':
            return 'حقيقة'
        elif v.lower() == 'date':
            return 'تاريخ'
        elif v.lower() == 'number':
            return 'رقم'
        elif v.lower() == 'array_string':
            return 'لائحة نصّيّة'
        elif v.lower() == 'array_bool':
            return 'لائحة حقائق'
        elif v.lower() == 'array_date':
            return 'لائحة تواريخ'
        elif v.lower() == 'array_number':
            return 'لائحة رقميّة'
    return v