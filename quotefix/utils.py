import  objc, re, htmlentitydefs

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

# unescape HTML-escaped string
def htmlunescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
