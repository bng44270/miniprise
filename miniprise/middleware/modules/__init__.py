class SqliteMiddlewareModuleBase():
  def __init__(self):
    self.mod_name = self.__class__.__name__
    self.TABLES = {}
    self.VIEWS = {}
    self.FUNCTIONS = {}
  
  def AddTableView(self,n,t,q=[],f=[]):
    if not n in self.VIEWS.keys():
      self.VIEWS[n] = {"type":"table","name":n,"table":t,"query":q,"fields":f}

  def AddJoinView(self,n,t,f={},j={},where=[],jointype=None):
    if not n in self.VIEWS.keys():
      self.VIEWS[n] = {"type":"join","table":t,"fields":f,"joins":j,"where":where,"jointype":jointype}
  
  def AddTable(self,t,s):
    self.TABLES[t] = {"schema":s, "modname":self.__class__.__name__, "Triggers":SqliteMiddlewareModuleTriggerGroup()}

  def AddFunction(self,f):
    self.FUNCTIONS[f.__name__] = f
  
  def InitModule(self,dbref,mods=[]):
    pass

  def SetBeforeQuery(self,t,f,p=100):
    self.TABLES[t]["Triggers"].BeforeQuery = f
    self.TABLES[t]["Triggers"].BeforeQueryPriority = p
  
  def SetBeforeInsert(self,t,f,p=100):
    self.TABLES[t]["Triggers"].BeforeInsert = f
    self.TABLES[t]["Triggers"].BeforeInsertPriority = p
  
  def SetAfterInsert(self,t,f,p=100):
    self.TABLES[t]["Triggers"].AfterInsert = f
    self.TABLES[t]["Triggers"].AfterInsertPriority = p
  
  def SetBeforeUpdate(self,t,f,p=100):
    self.TABLES[t]["Triggers"].BeforeUpdate = f
    self.TABLES[t]["Triggers"].BeforeUpdatePriority = p
  
  def SetAfterUpdate(self,t,f,p=100):
    self.TABLES[t]["Triggers"].AfterUpdate = f
    self.TABLES[t]["Triggers"].AfterUpdatePriority = p
  
  def SetBeforeDelete(self,t,f,p=100):
    self.TABLES[t]["Triggers"].BeforeDelete = f
    self.TABLES[t]["Triggers"].BeforeDeletePriority = p
  
  def SetAfterDelete(self,t,f,p=100):
    self.TABLES[t]["Triggers"].AfterDelete = f
    self.TABLES[t]["Triggers"].AfterDeletePriority = p

class SqliteMiddlewareModuleTriggerGroup:
  def __init__(self):
    self.BeforeQuery = None
    self.BeforeQueryPriority = 100
    self.BeforeInsert = None
    self.BeforeInsertPriority = 100
    self.AfterInsert = None
    self.AfterInsertPriority = 100
    self.BeforeUpdate = None
    self.BeforeUpdatePriority = 100
    self.AfterUpdate = None
    self.AfterUpdatePriority = 100
    self.BeforeDelete = None
    self.BeforeDeletePriority = 100
    self.AfterDelete = None
    self.AfterDeletePriority = 100
