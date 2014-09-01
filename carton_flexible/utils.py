# yes it's possible to do this in a 'magic way' by patching self.__dict__ , however this approach is clean and self-explanatory
class AttributeDict(dict):
    def __init__(self,dict=None):
        if dict is not None:
            for key,value in dict.iteritems():
                self[key] = value
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value