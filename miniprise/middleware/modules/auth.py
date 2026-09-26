from . import SqliteMiddlewareModuleBase
import time
import subprocess
import re
import base64

class AuthModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("user",{"id":"PrimaryKeyType","username":"StringType"}) 
    self.AddTable("user_class",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("user_class_prop",{"id":"PrimaryKeyType","name":"StringType","class":"ForeignKeyType","REF_class":"user_class.id"})
    self.AddTable("user_prop",{"user":"ForeignKeyType","prop":"ForeignKeyType","val":"StringType","REF_user":"user.id","REF_prop":"user_class_prop.id"})
    self.AddTable("user_class_uses",{"user":"ForeignKeyType","class":"ForeignKeyType","REF_user":"user.id","REF_class":"class.id"})

    self.AddTable("oauth_user",{"user":"ForeignKeyType","id":"StringType","secret":"StringType","REF_user":"user.id"})
    self.AddTable("oauth_token_lease",{"user":"ForeignKeyType","token":"StringType","expires":"NumberType","REF_user":"user.id"})

    self.AddTable("role",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("role_user",{"user":"ForeignKeyType","role":"ForeignKeyType","REF_user":"user.id","REF_role":"role.id"})

    self.AddTable("user_group",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("user_group_member",{"user_group":"ForeignKeyType","user":"ForeignKeyType","REF_user_group":"user_group.id","REF_user":"user.id"})
    self.AddTable("user_group_role",{"user_group":"ForeignKeyType","role":"ForeignKeyType","REF_user_group":"user_group.id","REF_role":"role.id"})

    self.AddTable("resource_type",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("resource_type_attr",{"id":"PrimaryKeyType","restype":"ForeignKeyType","name":"StringType","REF_restype":"resource_type.id"})
    self.AddTable("resource",{"id":"PrimaryKeyType","name":"StringType","restype":"ForeignKeyType","REF_restype":"resoruce_type.id"})
    self.AddTable("resource_attr",{"resource":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_resource":"resource.id","REF_attr":"resource_type_attr.id"})

    #####################
    #
    # access_role.access
    #     V & 1 => Create
    #     V & 2 => Read
    #     V & 4 => Update
    #     V & 8 => Delete
    #
    #     C = 1
    #     CR = 3
    #     RU = 6
    #     CRU = 7
    #     CRUD = 15
    #####################
    self.AddTable("access_role",{"resource":"ForeignKeyType","role":"ForeignKeyType","access":"NumberType","REF_resource":"resource.id","REF_role":"role.id"})
    
    self.AddFunction(self.ExpireTokens)
    self.AddFunction(self.GenerateToken)
    self.AddFunction(self.RevokeToken)
    self.AddFunction(self.GenerateOAuthCreds)
    self.AddFunction(self.RevokeOAuthCreds)
    self.AddFunction(self.GetUserClassByName)
    self.AddFunction(self.GetUserClassPropertyByName)
  
  def InitModule(self,dbref,mods=[]):
    user_classes = {"Person":["First name","Last name","E-mail address","Phone"],"Service":["Application","Owner"]}
    dbref.BulkInsert("user_class",[{"name":k} for k in user_classes.keys()])
    for this_class in user_classes.keys():
      this_class_id = self.GetUserClassByName(this_class,dbref)
      dbref.BulkInsert("user_class_prop",[{"name":v,"class":this_class_id} for v in user_classes[this_class]])
    
    dbref.BulkInsert('resource_type',[{"name":"url"},{"name":"table"},{"name":"field"}])
    self.Expose("oauth_token",self.GenerateToken,("client_id","client_secret"))
  
  def GenerateToken(self,client_id,client_secret,dbref):
    found = dbref.Query('oauth_user',[('id','EQ',client_id),('secret','EQ',client_secret)],['user'])
    if len(found) == 1 and len(found[0]) == 1:
      cmd_out = subprocess.run(['openssl','rand','-hex','128'],capture_output=True, text=True)
      new_token = cmd_out.stdout.strip()
      if len(new_token) == 256:
        self.RevokeToken(user_id,dbref)
        dbref.Insert('oauth_token_lease',{"user":found,"token":new_token,"expires":(int(time.time()) + (60 * 15))})
      else:
        raise Exception("Error generating OAuth token")
    else:
      raise Exception(f"User not found (id={user_id})")

  def RevokeToken(self,user_id,dbref):
    found = dbref.Query('user',[('id','EQ',user_id)],['id'])
    if len(found) == 1 and len(found[0]) == 1:
      dbref.Delete('oauth_token_lease',[('user','EQ',user_id)])
    else:
      raise Exception(f"User not found (id={user_id})")
  
  def ExpireTokens(self,dbref):
    nowdate = time.time()
    expired = dbref.Query("oauth_tokem_lease",[('expires','LT',nowdate)],["id"])

    if expired and len(expired) > 0 and len(expired[0]) > 0:
      remove_token = [('id','EQ',a[0]) for a in expired]
      dbref.Delete('oauth_token_lease',remove_token)

  def GenerateOAuthCreds(self,user_id,dbref):
    found = dbref.Query('user',[('id','EQ',user_id)],['id'])
    if len(found) == 1 and len(found[0]) == 1:
      cmd_out = subprocess.run(['openssl','rand','-hex','16'],capture_output=True, text=True)
      ufmt_client_id = cmd_out.stdout.strip()
      if len(ufmt_client_id) == 32:
        client_id = re.sub(r'^([0-9a-f]{8})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{12})',"\\1-\\2-\\3-\\4-\\5",ufmt_client_id)
        client_secret = self.__genclientsecret()

        self.RevokeOAuthCreds(user_id,dbref)
        dbref.Insert('oauth_user',{"user":user_id,"id":client_id,"secret":client_secret})
      else:
        raise Exception("Error generating client ID")
    else:
      raise Exception(f"User not found (id={user_id})")
  
  def RevokeOAuthCreds(self,username,dbref):
    user_id = self.GetUserIDByName(username,dbref)
    if user_id:
      dbref.Delete('oauth_token_lease',[('user','EQ',user_id)])
      dbref.Delete('oauth_user',[('user','EQ',user_id)])

  def __genclientsecret(self):
    cmd_out = subprocess.run(['openssl','rand','-hex','32'],capture_output=True, text=True)
    ufmt_client_secret = cmd_out.stdout.strip()
    if len(ufmt_client_secret) == 64:
      byte = '(?P<byteN>[0-9a-f][0-9a-f])'
      re_str = ""
      for i in range(0,32):
        re_str += byte.replace('N',str(i))

      split_ufmt_client_secret = re.match(re.compile('^' + re_str + '$'),ufmt_client_secret)

      intar = []
      for i in range(0,32):
        idx = 'byte' + str(i)
        intar.append(int(split_ufmt_client_secret[idx],16))

      b64enc_data = base64.b64encode(bytes(intar))

      return b64enc_data.decode('utf-8')
    else:
      raise Exception("Error generating client secret")

  def GetUserClassByName(self,n,dbref):
    uclass = dbref.Query('user_class',[('name','EQ',n)],['id'])
    if len(uclass) == 1 and len(uclass[0]) == 1:
      return uclass[0][0]
    else:
      return None

  def GetUserClassPropertyByName(self,n,dbref):
    uprop = dbref.Query('user_class_prop',[('name','EQ',n)],['id'])
    if len(uprop) == 1 and len(uprop[0]) == 1:
      return uprop[0][0]
    else:
      return None
  
  def GetUserIDByName(self,n,dbref=None):
    uname = dbref.Query('user',[('username','EQ',n)],['id'])
    if len(uname) == 1 and len(uname[0]) == 1:
      return uname[0][0]
    else:
      return None

  def CheckAccessRead(self,q,f,dbref):
    pass



# RETAINED THE BELOW CODE FOR REFERENCE
#
  #def Secure(self,dbref):
  #   result = dbref.Query("resource_type",[("name","EQ","table")],["id"])
  #   result2 = dbref.Query("resource_type",[("name","EQ","field")],["id"])
  #   if len(result) == 1 and len(result[0]) == 1 and len(result2) == 1 and len(result2[0]) == 1:
  #     table_res_type_id = result[0][0]
  #     field_res_type_id = result2[0][0]

  #     ticket_view_role_id = dbref.Insert("role",{"name":"ticket_view"})
  #     ticket_edit_role_id = dbref.Insert("role",{"name":"ticket_edit"})
  #     ticket_creator_role_id = dbref.Insert("role",{"name":"ticket_creator"})
  #     ticket_admin_role_id = dbref.Insert("role",{"name":"ticket_admin"})


  #     ticket_table_id = dbref.Insert("resource",{"name":"ticket","restype":table_res_type_id})
  #     ticket_attr_table_id = dbref.Insert("resource",{"name":"ticket_attr","restype":table_res_type_id})
  #     ticket_stage_table_id = dbref.Insert("resource",{"name":"ticket_stage","restype":table_res_type_id})
  #     ticket_type_table_id = dbref.Insert("resource",{"name":"ticket_type","restype":table_res_type_id})
  #     ticket_type_stage_table_id = dbref.Insert("resource",{"name":"ticket_type_stage","restype":table_res_type_id})
  #     ticket_type_attr_table_id = dbref.Insert("resource",{"name":"ticket_type_attr","restype":table_res_type_id})

  #     access_roles = []
  #     access_roles.append({"resource":ticket_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_table_id,"role":ticket_admin_role_id,"access":15})
  #     access_roles.append({"resource":ticket_attr_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_attr_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_attr_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_attr_table_id,"role":ticket_admin_role_id,"access":15})
  #     access_roles.append({"resource":ticket_stage_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_stage_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_stage_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_stage_table_id,"role":ticket_admin_role_id,"access":15})
  #     access_roles.append({"resource":ticket_type_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_type_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_type_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_type_table_id,"role":ticket_admin_role_id,"access":15})
  #     access_roles.append({"resource":ticket_type_stage_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_type_stage_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_type_stage_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_type_stage_table_id,"role":ticket_admin_role_id,"access":15})
  #     access_roles.append({"resource":ticket_type_attr_table_id,"role":ticket_view_role_id,"access":2})
  #     access_roles.append({"resource":ticket_type_attr_table_id,"role":ticket_edit_role_id,"access":6})
  #     access_roles.append({"resource":ticket_type_attr_table_id,"role":ticket_creator_role_id,"access":7})
  #     access_roles.append({"resource":ticket_type_attr_table_id,"role":ticket_admin_role_id,"access":15})

  #     for this_table in [t for t in dbref.keys() if t.startswith('ticket')]:
  #       for this_field in dbref[this_table].FIELDS.keys():
  #         field_resource_id = dbref.Insert("resource",{"name":f"{this_table}.{this_field}","restype":field_res_type_id})

  #         if dbref[this_table].FIELDS[this_field] == "PrimaryKeyType":  
  #           access_roles.append({"resource":field_resource_id,"role":ticket_view_role_id,"access":2})
  #         else:
  #           access_roles.append({"resource":field_resource_id,"role":ticket_view_role_id,"access":2})
  #           access_roles.append({"resource":field_resource_id,"role":ticket_edit_role_id,"access":6})
  #           access_roles.append({"resource":field_resource_id,"role":ticket_creator_role_id,"access":7})
  #           access_roles.append({"resource":field_resource_id,"role":ticket_admin_role_id,"access":15})
      
  #     dbref.BulkInsert("access_role",access_roles)