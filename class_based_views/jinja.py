from class_based_views import TemplateView

class JinjaView(TemplateView):
    """
    Uses Jinja instead of django to render views.
    Use as a mixin:
    
    class MyView(JinjaView, DetailView):
        ...
    """                
    def load_template(self, names):
        """
        Load a list of templates using the default template loader.
        """
        return select_template(names)

    def get_context_instance(self, context=None):
        """
        Get the template context instance.
        For django templates, this normally returns a Context (or subclass) 
        instance. However, for jinja, only a dictionary is returned.
        """
        return context or {}

