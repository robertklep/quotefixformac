from    new     import classobj, instance
import  objc, re

# Method Swizzler: exchange an existing Objective-C method with a new
# implementation (akin to monkeypatching)
def swizzle(cls, SEL):
    if isinstance(cls, basestring):
        cls = objc.lookUpClass(cls)
    def decorator(func):
        oldIMP = cls.instanceMethodForSelector_(SEL)
        if oldIMP.isClassMethod:
            oldIMP = cls.methodForSelector_(SEL)
        def wrapper(self, *args, **kwargs):
            return func(self, oldIMP, *args, **kwargs)
        newMethod = objc.selector(wrapper, selector = oldIMP.selector, signature = oldIMP.signature, isClassMethod = oldIMP.isClassMethod)
        objc.classAddMethod(cls, SEL, newMethod)
        return wrapper
    return decorator

# string.Template-like string interpolation
class SimpleTemplate:

    def __init__(self, template):
        self.template = template

    def _substitute_param(self, param, params):
        tokens  = param.split('.')
        node    = params.get(tokens.pop(0))
        while node and tokens:
            node = getattr(node, tokens.pop(0), None)
        if node == None:
            return '${%s}' % param
        return unicode(node)

    def _substitute(self, params):
        expanded = self.template
        expanded = re.sub(r'\$\{(.*?)\}',  lambda p: self._substitute_param(p.group(1), params), expanded)
        return expanded

    def substitute(self, params):
        return self._substitute(params)
