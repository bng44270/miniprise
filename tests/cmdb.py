from miniprise.middleware import SqliteMiddlewareGroup
from miniprise.middleware.modules import cmdb as mods

def InitializeCMDB():
  cmdb = SqliteMiddlewareGroup('cmdb.db')
  
  if not cmdb.ExistsTable("ci"):
    cmdb.CreateTable("ci",{"id":"PrimaryKeyType","name":"StringType"})
  
  if not cmdb.ExistsTable("ci_rel_type"):
    cmdb.CreateTable("ci_rel_type",{"id":"PrimaryKeyType","name":"StringType"})
  
  if not cmdb.ExistsTable("ci_cat"):
    cmdb.CreateTable("ci_cat",{"id":"PrimaryKeyType","name":"StringType"})
  
  if not cmdb.ExistsTable("ci_cat_attr"):
    cmdb.CreateTable("ci_cat_attr",{"id":"PrimaryKeyType","name":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
  
  if not cmdb.ExistsTable("ci_cat_uses"):
    cmdb.CreateTable("ci_cat_uses",{"item":"ForeignKeyType","cat":"ForeignKeyType","REF_item":"ci.id","REF_cat":"ci_cat.id"})
  
  if not cmdb.ExistsTable("ci_attr"):
    cmdb.CreateTable("ci_attr",{"item":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_item":"ci.id","REF_attr":"ci_cat_attr.id"})
  
  if not cmdb.ExistsTable("ci_rel"):
    cmdb.CreateTable("ci_rel",{"parent":"ForeignKeyType","child":"ForeignKeyType","reltype":"ForeignKeyType","REF_parent":"ci.id","REF_child":"ci.id","REF_reltype":"ci_rel_type.id"})
  
  if not cmdb.ExistsTable("discovered_ci_rule"):
    cmdb.CreateTable("discovered_ci_rule",{"id":"PrimaryKeyType","pattern":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
  
  if not cmdb.ExistsTable("discovered_ci"):
    cmdb.CreateTable("discovered_ci",{"item":"ForeignKeyType","rule":"ForeignKeyType","lastseen":"NumberType","REF_item":"ci.id","REF_rule":"discovered_ci_rule.id"})
  
  if not cmdb.ExistsTable("discovered_rel_rule"):
    cmdb.CreateTable("discovered_rel_rule",{"id":"PrimaryKeyType","pattern":"StringType","reltype":"ForeignKeyType","REF_reltype":"ci_rel_type.id"})
  
  if not cmdb.ExistsTable("discovered_rel"):
    cmdb.CreateTable("discovered_rel",{"parent":"ForeignKeyType","child":"ForeignKeyType","rule":"ForeignKeyType","lastseen":"NumberType","REF_parent":"ci.id","REF_child":"ci.id","REF_rule":"discovered_rel_rule.id"})
  
  cmdb.LoadModule("ci",mods.CIModule)
  cmdb.LoadModule("ci_cat_uses",mods.CICatUsesModule)
  
  return cmdb
