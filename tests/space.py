from miniprise.middleware import SqliteMiddlewareGroup

def InitializeSpaces():
  spaces = SqliteMiddlewareGroup("space")
  
  if not spaces.ExistsTable("location_type"):
    spaces.CreateTable("location_type",{"id":"PrimaryKeyType","name":"StringType"})
  
  if not spaces.ExistsTable("location"):
    spaces.CreateTable("location",{"id":"PrimaryKeyType","name":"StringType","type":"ForeignKeyType","REF_type":"location_type.id"})
  
  if not spaces.ExistsTable("location_type_attr"):
    spaces.CreateTable("location_type_attr",{"id":"PrimaryKeyType","name":"StringType"})
  
  if not spaces.ExistsTable("location_type_uses"):
    spaces.CreateTable("location_type_uses",{"type":"ForeignKeyType","location":"ForeignKeyType","REF_type":"location_type.id","REF_location":"location.id"})
  
  if not spaces.ExistsTable("location_attr"):
    spaces.CreateTable("location_attr",{"location":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_location":"location.id","REF_attr":"location_type_attr.id"})
  
  return spaces
