from .. import SqliteMiddlewareModuleBase
import time
import subprocess
import re
import base64

class AuthModule(SqliteMiddlewareModuleBase):
  def __init__(self):
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

    self.AddTable("access_profile",{"id":"PrimaryKeyType","resource":"ForeignKeyType","REF_resource":"resource.id"})
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
    self.AddTable("access_role",{"profile":"ForeignKeyType","role":"ForeignKeyType","access":"NumberType","REF_profile":"access_profile.id","REF_role":"role.id"})
  
  def InitModule(self,dbref):
    self.AddFunction(self.ExpireTokens)
    self.AddFunction(self.GenerateToken)
    self.AddFunction(self.RevokeToken)
    self.AddFunction(self.GenerateOAuthCreds)
    self.AddFunction(self.RevokeOAuthCreds)

    user_classes = {"Person":["First name","Last name","E-mail address","Phone"],"Service":["Application","Owner"]}
    dbref.BulkInsert("user_class",[{"name":k} for k in user_classes.keys()])
    for this_class in user_classes.keys():
      this_class_id = self.__getuserclassbyname(this_class,dbref)
      dbref.BulkInsert("user_class_prop",[{"name":v,"class":this_class_id} for v in user_classes[this_class]])
    
    res_types = [{"name":"url"},{"name":"table"}]
    dbref.BulkInsert('resource_type',res_types)

  def GenerateToken(self,username,dbref):
    user_id = self.__getuseridbyname(username,dbref)
    if user_id:
      new_token = subprocess.run(['openssl','rand','-hex','50'],capture_output=True, text=True)
      if len(new_token.stdout) == 50:
        self.RevokeToken(username,dbref)
        dbref.Insert('oauth_token_lease',{"user":user_id,"token":new_token.stdout})

  def RevokeToken(self,username,dbref):
    user_id = self.__getuseridbyname(username,dbref)
    if user_id:
      dbref.Delete('oauth_token_lease',[('user','EQ',user_id)])
  
  def ExpireTokens(self,dbref):
    nowdate = time.time()
    expired = dbref.Query("oauth_tokem_lease",[('expires','LT',nowdate)],["id"])

    if expired and len(expired) > 0 and len(expired[0]) > 0:
      remove_token = [('id','EQ',a[0]) for a in expired]
      dbref.Delete('oauth_token_lease',remove_token)

  def GenerateOAuthCreds(self,username,dbref):
    user_id = self.__getuseridbyname(username,dbref)
    if user_id:
      ufmt_client_id = subprocess.run(['openssl','rand','-hex','16'],capture_output=True, text=True)
      if len(ufmt_client_id.stdout) == 32:
        client_id = re.sub(r'^([0-9a-f]{8})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{4})([0-9a-f]{12})',"\\1-\\2-\\3-\\4-\\5",ufmt_client_id.stdout)
        client_secret = self.__genclientsecret()

        self.RevokeOAuthCreds(username,dbref)
        dbref.Insert('oauth_user',{"user":user_id,"id":client_id,"secret":client_secret})
  
  def RevokeOAuthCreds(self,username,dbref):
    user_id = self.__getuseridbyname(username,dbref)
    if user_id:
      dbref.Delete('oauth_token_lease',[('user','EQ',user_id)])
      dbref.Delete('oauth_user',[('user','EQ',user_id)])

  def __genclientsecret(self):
    ufmt_client_secret = subprocess.run(['openssl','rand','-hex','32'],capture_output=True, text=True)
    if len(ufmt_client_secret) == 64:
      byte = '(?P<byteN>[0-9a-f][0-9a-f])'
      re_str = ""
      for i in range(0,32):
        re_str += byte.replace('N',str(i))

      split_ufmt_client_secret = re.match(re.compile('^' + re_str + '$'),ufmt_client_secret.stdout)

      intar = []
      for i in range(0,32):
        idx = 'byte' + str(i)
        intar.append(int(split_ufmt_client_secret[idx],16))

      b64enc_data = base64.b64encode(bytes(intar))

      return b64enc_data.decode('utf-8')

  def __getuserclassbyname(self,n,dbref):
    uclass = dbref.Query('user_class',[('name','EQ',n)],['id'])
    if len(uclass) == 1 and len(uclass[0]) == 1:
      return uclass[0][0]
    else:
      return None
  
  def __getuseridbyname(self,n,dbref):
    uname = dbref.Query('user',[('name','EQ',n)],['id'])
    if len(uname) == 1 and len(uname[0]) == 1:
      return uname[0][0]
    else:
      return None


