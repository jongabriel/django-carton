# yes it's possible to do this in a 'magic way' by patching self.__dict__ , however this approach is clean and self-explanatory
class AttributeDict(dict):
    def __init__(self,dicta=None):
        if dicta is not None:
            for key,value in dicta.iteritems():
                self[key] = value
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value
        
class CartException(Exception):
    pass

#from http://kiennt.com/blog/2012/06/14/python-object-and-dictionary-convertion.html, which
#itself is from a stackoverflow, 
#http://stackoverflow.com/questions/1305532/convert-python-dict-to-object/1305663#1305663
# convert a dictionary to a class
class Struct(object):
    def __init__(self, adict):
        """Convert a dictionary to a class

        @param :adict Dictionary
        """
        self.__dict__.update(adict)
        for k, v in adict.items():
            if isinstance(v, dict):
                self.__dict__[k] = Struct(v)

def get_object(adict):
    """Convert a dictionary to a class

    @param :adict Dictionary
    @return :class:Struct
    """
    return Struct(adict)