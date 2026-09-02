from .. import SqliteMiddlewareModuleBase, SqliteMiddlewareLibrary as lib

class CIModule(SqliteMiddlewareModuleBase):
  def __init__(self):
    self.AddTable("ci",{"id":"PrimaryKeyType","name":"StringType"})
    super().SetBeforeInsert('ci',self.BeforeInsertCI,10)
    super().SetBeforeUpdate('ci',self.BeforeUpdateCI,10)
    
    self.AddTable("ci_rel_type",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("ci_cat",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("ci_cat_attr",{"id":"PrimaryKeyType","name":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
    
    self.AddTable("ci_cat_uses",{"item":"ForeignKeyType","cat":"ForeignKeyType","REF_item":"ci.id","REF_cat":"ci_cat.id"})
    super().SetAfterInsert('ci_cat_uses',self.AfterInsertCICatUses)
    super().SetBeforeDelete('ci_cat_uses',self.BeforeDeleteCICatUses)
    super().SetAfterDelete('ci_cat_uses',self.AfterDeleteCICatUses,100)
    
    self.AddTable("ci_attr",{"item":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_item":"ci.id","REF_attr":"ci_cat_attr.id"})
    self.AddTable("ci_rel",{"parent":"ForeignKeyType","child":"ForeignKeyType","reltype":"ForeignKeyType","REF_parent":"ci.id","REF_child":"ci.id","REF_reltype":"ci_rel_type.id"})
    self.AddTable("discovered_ci_rule",{"id":"PrimaryKeyType","pattern":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
    self.AddTable("discovered_ci",{"item":"ForeignKeyType","rule":"ForeignKeyType","lastseen":"NumberType","REF_item":"ci.id","REF_rule":"discovered_ci_rule.id"})
    self.SetAfterInsert('discovered_ci',self.AfterInsertDiscoveredCI)
    self.AddTable("discovered_rel_rule",{"id":"PrimaryKeyType","pattern":"StringType","reltype":"ForeignKeyType","REF_reltype":"ci_rel_type.id"})
    self.AddTable("discovered_rel",{"parent":"ForeignKeyType","child":"ForeignKeyType","rule":"ForeignKeyType","lastseen":"NumberType","REF_parent":"ci.id","REF_child":"ci.id","REF_rule":"discovered_rel_rule.id"})
    self.SetAfterInsert('discovered_rel',self.AfterInsertDiscoveredRelationship)
  
  def AddTable(self,n,s):
    super()._SqliteMiddlewareModuleBase__addtable(n,s)
  
  def BeforeInsertCI(self,row,dbdef):
    if lib.FieldChangesToEmpty("name",row):
      raise Exception("Cannot clear name of CI")
  
  def BeforeUpdateCI(self,q,update,dbdef):
    row = {k:v for (k,v) in update}
    if lib.FieldChangesToEmpty("name",row):
      raise Exception("Cannot clear name of CI")
  
  def AfterInsertCICatUses(self,row,dbref,passed):
    ci = row["item"]
    category = row["cat"]
    
    attributes = dbref.Query("ci_cat_attr",[("cat","EQ",category)],["id"])
    
    atts = []
    for new_att in attributes:
      r = {}
      r["item"] = ci
      r["attr"] = new_att[0]
      r["val"] = ""
      atts.append(r)
    
    dbref.BulkInsert("ci_attr",atts)
  
  def BeforeDeleteCICatUses(q,dbref):
    result = dbref.Query("ci_cat_uses",q,["cat","item"])
    return [{"cat":a[0],"item":a[1]} for a in result]
    
  def AfterDeleteCICatUses(q,dbref,passed):
    for cat_item in passed:
      result = dbref.Query("ci_cat_attr",[("cat","EQ",cat_item["cat"])],["id"])
      for this_attr in [{"attr":a[0]} for a in result]:
        dbref.Delete("ci_attr",[("item","EQ",cat_item["item"]),("attr","EQ",this_attr)],dbref)
  
  def AfterInsertDiscoveredRelationship(self,row,dbref,passed):
    parentCIID = row['parent']
    childCIID = row['child']
    relrec = dbref.Query('discovered_rel_rule',[('id',row['reltype'])],['reltype'])
    if len(relrec) == 1:
      reltype = relrec[0][0]
      dbref.Insert('ci_rel',{'parent':parentCIID,'child':childCIID,'reltype':reltype})
  
  def AfterInsertDiscoveredCI(self,row,dbref,passed):
    ci = row['item']
    rulerec = dbref.Query('discovered_ci_rule',[('id',row['rule'])],['cat'])
    for rule in rulerec:
      usecat = rule[0]
      dbref.Insert('ci_cat_uses',{'item':ci,'cat':usecat})
    
