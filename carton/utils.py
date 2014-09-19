import pickle

class CartException(Exception):
    pass


def get_object(adict):
    """Convert a pickle to a class

    @param :adict Dictionary
    @return :class:Struct
    """
    return pickle.loads(adict)