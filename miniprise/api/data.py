from flask import Flask, send_file, make_response, request
from middleware import SqliteMiddlewareGroup
from conf import UsedModules
import json

class DataAccessAPI(Flask):
  def __init__(self,import_name,dbfile):
    super().__init__(import_name=import_name)
    self.DB = SqliteMiddlewareGroup(dbfile)
    for this_mod in UsedModules:
      self.DB.LoadModule(this_mod)
    
    self.__build_table_api()
  
  def __query_table(self,table):
    checkmime = request.headers.get("Accept")
    if checkmime == "application/json":
      qobj = request.get_json()
      usequery = qobj["query"] if "query" in qobj.keys() else []
      usefields = qobj["fields"] if "fields" in qobj.keys() else []
      usecount = qobj["count"] if "count" in qobj.keys() else 0
      result = self.DB.Query(table,usequery,usefields,usecount)
      resp = {}
      resp["success"] = False
      if len(result) > 0:
        resp["success"] = True
        resp["result"] = result
      
      return make_response(json.dumps(resp),200)
    else:
      return make_response("Invalid request",500)
  
  def __insert_table(self,table):
    pass
  def __update_table(self,table):
    pass
  def __delete_table(self,table):
    pass
  def __mod_function(self,module,function):
    funcdef = self.DB.MODULES[module]["functions"][function]
    arglist = funcdef.__code__.co_varnames[0:funcdef.__code__.co_argcount]
    pass
  def __build_table_api(self):
    self.add_url_rule(f"/table/<table>/query",view_func=self.__query_table,methods=["POST"])
    self.add_url_rule(f"/table/<table>/insert",view_func=self.__insert_table,methods=["POST"])
    self.add_url_rule(f"/table/<table>/update",view_func=self.__update_table,methods=["POST"])
    self.add_url_rule(f"/table/<table>/delete",view_func=self.__delete_table,methods=["POST"])
    self.add_url_rule(f"/module/<module>/<function>",view_func=self.__mod_function,methods=["POST"])

      
