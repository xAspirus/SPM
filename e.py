class Base:
  def __init__(self):
    ...
  
  def func(self, x, y, z):
    print('base class func called')

class More(Base):
  @classmethod
  def convert_base(cls, obj: Base):
    obj.__class__ = cls
    f = type(obj).func
    def func(self, x, y, z):
      print('more class func called')
      f(self, x, y, z)
    obj.func = func

obj = Base()
More.convert_base(obj)
obj.func(0, 0, 0)
