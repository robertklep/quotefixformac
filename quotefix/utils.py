import  objc, re

# Method Swizzler: exchange an existing Objective-C method with a new
# implementation (akin to monkeypatching)
def swizzle(cls, SEL):
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
class Template:

    def __init__(self, template):
        self.template = template

    def _substitute_param(self, param, params):
        return params.get(param, "${%s}" % param)

    def _substitute(self, params):
        expanded = self.template
        expanded = re.sub(r'\$\{(.*?)\}',  lambda p: self._substitute_param(p.group(1), params), expanded)
        return expanded

    def substitute(self, params):
        return self._substitute(params)
