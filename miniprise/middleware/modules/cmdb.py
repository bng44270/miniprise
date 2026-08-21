from .. import SqliteMiddlewareModuleBase, SqliteMiddlewareLibrary as lib

class CIModule(SqliteMiddlewareModuleBase):
  def BeforeInsert(self,row,dbdef):
    if lib.FieldChangesToEmpty("name",row):
      raise Exception("Cannot clear name of CI")
  
  def BeforeUpdate(self,q,update,dbdef):
    row = {k:v for (k,v) in update}
    if lib.FieldChangesToEmpty("name",row):
      raise Exception("Cannot clear name of CI")

class CICatUsesModule(SqliteMiddlewareModuleBase):
  def AfterInsert(self,row,dbref,passed):
    ci = row['item']
    category = row['cat']
    
    attributes = dbref.Query('ci_cat_attr',[("cat","EQ",category)],["id"])
    
    atts = []
    for new_att in attributes:
      r = {}
      r['item'] = ci
      r['attr'] = new_att[0]
      r['val'] = ""
      atts.append(r)
    
    dbref.BulkInsert('ci_attr',atts)
  
  def BeforeDelete(q,dbref):
    result = dbref.Query('ci_cat_uses',q,["cat","item"])
    return [{"cat":a[0],"item":a[1]} for a in result]
    
  def AfterDelete(q,dbref,passed):
    for cat_item in passed:
      result = dbref.Query('ci_cat_attr',[("cat","EQ",cat_item['cat'])],["id"])
      for this_attr in [{"attr":a[0]} for a in result]:
        dbref.Delete('ci_attr',[('item','EQ',cat_item['item']),("attr","EQ",this_attr)],dbref)
