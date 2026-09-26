from . import SqliteMiddlewareModuleBase

class ConvergedModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    if "SpaceModule" in mods and "AssetModule" in mods:
      self.AddTable("asset_location",{"asset":"ForeignKeyType","location":"ForeignKeyType","REF_asset":"asset.id","REF_location":"location.id"})
    
    if "AuthModule" in mods and "CMDBModule" in mods:
      self.AddTable("ci_resource",{"ci":"ForeignKeyType","resource":"ForeignKeyType","REF_ci":"ci.id","REF_resource":"resource.id"})
    
    if 'SpaceModule' in mods and "TicketModule" in mods:
      self.AddTable("ticket_location",{"ticket":"ForeignKeyType","location":"ForeignKeyType","REF_ticket":"ticket.id","REF_location":"location.id"})
    
    if "CMDBModule" in mods and "TicketModule" in mods:
      self.AddTable("ticket_ci",{"ticket":"ForeignKeyType","ci":"ForeignKeyType","REF_ticket":"ticket.id","REF_ci":"ci.id"})
    
    if "AssetModule" in mods and "TicketModule" in mods:
      self.AddTable("ticket_asset",{"ticket":"ForeignKeyType","asset":"ForeignKeyType","REF_ticket":"ticket.id","REF_asset":"asset.id"})
      
    if "AuthModule" in mods and "TicketModule" in mods:
      self.AddTable("ticket_resource",{"ticket":"ForeignKeyType","resource":"ForeignKeyType","REF_ticket":"ticket.id","REF_resource":"resource.id"})    