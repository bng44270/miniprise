from . import SqliteMiddlewareModuleBase

class CMDBModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("ci",{"id":"PrimaryKeyType","name":"StringType","parent":"ForeignKeyType","REF_parent":"ci.id"})
    self.SetBeforeInsert('ci',self.BeforeInsertCI,10)
    self.SetBeforeUpdate('ci',self.BeforeUpdateCI,10)
    
    self.AddTable("ci_cat",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("ci_cat_attr",{"id":"PrimaryKeyType","name":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
    
    self.AddTable("ci_cat_uses",{"item":"ForeignKeyType","cat":"ForeignKeyType","REF_item":"ci.id","REF_cat":"ci_cat.id"})
    self.SetAfterInsert('ci_cat_uses',self.AfterInsertCICatUses)
    self.SetBeforeDelete('ci_cat_uses',self.BeforeDeleteCICatUses)
    self.SetAfterDelete('ci_cat_uses',self.AfterDeleteCICatUses,100)
    
    self.AddTable("ci_attr",{"item":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","multi":"BooleanType","REF_item":"ci.id","REF_attr":"ci_cat_attr.id"})
    self.AddTable("discovered_ci_rule",{"id":"PrimaryKeyType","name":"StringType","cat":"ForeignKeyType","REF_cat":"ci_cat.id"})
    self.AddTable("discovered_ci",{"name":"StringType","rule":"ForeignKeyType","lastseen":"NumberType","REF_rule":"discovered_ci_rule.id"})
    self.SetAfterInsert('discovered_ci',self.AfterInsertDiscoveredCI)

    self.AddJoinView('ci_cat_attrs','ci',{"ci.name":"ci_name","ci_cat.name":"ci_cat","ci_cat_attr.name":"attr","ci_attr.val":"attr_val"},{"ci_cat_uses":[('ci_cat.id','EQ','ci_cat_uses.cat'),('ci.id','EQ','ci_cat_uses.item')],"ci_cat":[("ci_cat.id","EQ","ci_cat_uses.cat")],"ci_cat_attr":[("ci_cat.id","EQ","ci_cat_attr.cat")],"ci_attr":[("ci_attr.attr","EQ","ci_cat_attr.id")]})
  
  def InitModule(self, dbref,mods):
    cats = {"Computer":["Display size","Memory","CPU","Storage","MAC address"],"nmap-discovered":['Open port','IP address','OS name','OS vendor','OS family','OS type','OS generation']}
    dbref.BulkInsert('ci_cat',[{"name":k} for k in cats.keys()])
    
    for this_cat in cats.keys():
      cat_id = self.__getcatbyname(this_cat,dbref)
      dbref.Insert('discovered_ci_rule',{"name":(this_cat + "_rule"),"cat":cat_id})
      dbref.BulkInsert('ci_cat_attr',[{"name":a,"cat":cat_id} for a in cats[this_cat]])
  
  def __getcatbyname(self,n,dbref):
    cat = dbref.Query('ci_cat',[('name','EQ',n)],['id'])
    if len(cat) == 1 and len(cat[0]) == 1:
      return cat[0][0]
    else:
      return None
  
  ###########
  # Prevent clearing CI name
  ###########
  def BeforeInsertCI(self,row,dbdef):
    if 'name' in row.keys() and len(row['name']) == 0:
      raise Exception("Cannot clear name of CI")
  
  ###########
  # Prevent clearing CI name
  ###########
  def BeforeUpdateCI(self,q,update,dbdef):
    row = {k:v for (k,v) in update}
    if 'name' in row.keys() and len(row['name']) == 0:
      raise Exception("Cannot clear name of CI")
  
  ###########
  # Populate ci_attr fields when ci_cat_uses is populated
  ###########
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
    
    if len(atts) > 0:
      dbref.BulkInsert("ci_attr",atts)
  
  ###########
  # Capture deleted record for use in AfterDeleteCICatUses
  ###########
  def BeforeDeleteCICatUses(q,dbref):
    result = dbref.Query("ci_cat_uses",q,["cat","item"])
    return [{"cat":a[0],"item":a[1]} for a in result]
  
  ###########
  # Delete fields from ci_cat when ci_cat_uses is removed
  ###########
  def AfterDeleteCICatUses(q,dbref,passed):
    for cat_item in passed:
      result = dbref.Query("ci_cat_attr",[("cat","EQ",cat_item["cat"])],["id"])
      for this_attr in [{"attr":a[0]} for a in result]:
        dbref.Delete("ci_attr",[("item","EQ",cat_item["item"]),("attr","EQ",this_attr)],dbref)
  
  ###########
  # Add relationship (ci_rel) when relationship is discovered
  ###########
  def AfterInsertDiscoveredRelationship(self,row,dbref,passed):
    parentCIID = row['parent']
    childCIID = row['child']
    relrec = dbref.Query('discovered_rel_rule',[('id',row['reltype'])],['reltype'])
    if len(relrec) == 1:
      reltype = relrec[0][0]
      dbref.Insert('ci_rel',{'parent':parentCIID,'child':childCIID,'reltype':reltype})
  
  ###########
  # Insert CI and cats when a CI is discovered
  ###########
  def AfterInsertDiscoveredCI(self,row,dbref,passed):
    dbref.Insert('ci',{"name":row['name']})
    ciqry = dbref.Query('ci',[('name','EQ',row['name'])],['id'])
    if len(ciqry) == 1 and len(ciqry[0]) == 1:
      ci = ciqry[0][0]
      rulerec = dbref.Query('discovered_ci_rule',[('id',row['rule'])],['cat'])
      for rule in rulerec:
        usecat = rule[0]
        dbref.Insert('ci_cat_uses',{'item':ci,'cat':usecat})
    
