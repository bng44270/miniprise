from . import SqliteMiddlewareModuleBase

class AssetModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("asset_type",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("asset",{"id":"PrimaryKeyType","name":"StringType","assettype":"ForeignKeyType","REF_type":"asset_type.id"})
    self.AddTable("asset_type_attr",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("asset_type_uses",{"assettype":"ForeignKeyType","asset":"ForeignKeyType","REF_assettype":"asset_type.id","REF_asset":"asset.id"})
    self.AddTable("asset_attr",{"asset":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_asset":"asset.id","REF_attr":"asset_type_attr.id"})