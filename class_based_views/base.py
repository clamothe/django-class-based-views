import copy
from django import http
from django.core.exceptions import ImproperlyConfigured
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _

def quacks_like_a_request(request):
    return hasattr(request, 'method') and hasattr(request, 'path')

class View(object):
    """
    Intentionally simple parent class for all views. Only implements 
    dispatch-by-method and simple sanity checking.
    """
    
    method_names = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'TRACE']
    
    def __init__(self, *args, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # If the first argument is a request, helpfully inform people
        # they need to instantiate the class in the URLs.
        if args and quacks_like_a_request(args[0]):
            raise RuntimeError("You must use an instance of View as a view, "
                               "not the class itself.")
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            if key in self.method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that." 
                                % (key, self.__class__.__name__))
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise TypeError("%s() received an invalid keyword %r" % (
                    self.__class__.__name__,
                    key,
                ))
    
    def __call__(self, request, *args, **kwargs):
        """
        Main entry point for a request-response process.
        """
        # First, change to a copy of ourselves to stop state in 
        # "self." persisting. We only need a shallow copy, really.
        self = copy.copy(self)
        self.request = request
        self.args = args
        self.kwargs = kwargs
        # Try to dispatch to the right method for that; if it doesn't exist,
        # raise a big error.
        if hasattr(self, request.method.upper()):
            return getattr(self, request.method.upper())(request, *args, **kwargs)
        else:
            allowed_methods = [m for m in self.method_names if hasattr(self, m)]
            return http.HttpResponseNotAllowed(allowed_methods)
    

class TemplateView(View):
    """
    A view which can render itself with a template.
    """
    template_name = None
    
    def render_to_response(self, template_names=None, context=None):
        """
        Returns a response with a template rendered with the given context.
        """
        return self.get_response(self.render(template_names, context))
    
    def get_response(self, content, **httpresponse_kwargs):
        """
        Construct an `HttpResponse` object.
        """
        return http.HttpResponse(content, **httpresponse_kwargs)
    
    def render(self, template_names=None, context=None):
        """
        Render the template with a given context.
        """
        context_instance = self.get_context_instance(context)
        return self.get_template(template_names).render(context_instance)
    
    def get_context_instance(self, context=None):
        """
        Get the template context instance. Must return a Context (or subclass) 
        instance.
        """
        if context is None:
            context = {}
        return RequestContext(self.request, context)
    
    def get_template(self, names=None):
        """
        Get a ``Template`` object for the given request.
        """
        if names is None:
            names = self.get_template_names()
        if not names:
            raise ImproperlyConfigured("'%s' must provide template_name." 
                                       % self.__class__.__name__)
        if isinstance(names, basestring):
            names = [names]
        return self.load_template(names)
    
    def get_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        if self.template_name is None:
            return []
        else:
            return [self.template_name]
    
    def load_template(self, names):
        """
        Load a list of templates using the default template loader.
        """
        return loader.select_template(names)
    
