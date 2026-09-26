from . import SqliteMiddlewareModuleBase

class SpaceModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("location_type",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("location",{"id":"PrimaryKeyType","name":"StringType","sptype":"ForeignKeyType","parent":"ForeignKeyType","REF_type":"location_type.id","REF_parent":"location.id"})
    self.AddTable("location_type_attr",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("location_type_uses",{"sptype":"ForeignKeyType","location":"ForeignKeyType","REF_sptype":"location_type.id","REF_location":"location.id"})
    self.AddTable("location_attr",{"location":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_location":"location.id","REF_attr":"location_type_attr.id"})