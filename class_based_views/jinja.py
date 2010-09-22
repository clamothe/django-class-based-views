from class_based_views import TemplateView
from class_based_views.djangojinja2 import select_template 

class JinjaView(TemplateView):
    """
    Uses Jinja instead of django to render views.
    Use as a mixin, or as a replacement for TemplateView:
    
    class ViewA(JinjaView, DetailView): 
        "DetailView rendered using Jinja"
        ...
    class ViewB(JinjaView):
        "TemplateView rendered using Jinja"
        ...
    """                
    def load_template(self, names):
        """
        Load a list of templates using the Jinja template loader.
        """
        return select_template(names)

    def get_context_instance(self, context=None):
        """
        Get the template context instance.
        For django templates, this normally returns a Context (or subclass) 
        instance. However, for jinja, only a dictionary is returned.
        """
        return context or {}

