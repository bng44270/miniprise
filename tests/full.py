from miniprise.middleware import SqliteMiddlewareGroup
from miniprise.middleware.modules import cmdb, auth

svr = SqliteMiddlewareGroup('miniprise.db')
svr.LoadModule(auth.AuthModule)
svr.LoadModule(cmdb.CMDBModule)

# Test CMDBModule
ci_id = svr.Insert("ci",{"name":"server01"})
sw_id = svr.Insert("ci",{"name":"web server software"})
ci_cat = svr.Insert("ci_cat",{"name":"Linux"})
ci_attr = svr.Insert("ci_cat_attr",{"name":"distro","cat":ci_cat})
svr.Insert("ci_cat_uses",{"item":ci_id,"cat":ci_cat})
svr.Insert("ci_attr",{"item":ci_id,"attr":ci_attr,"val":"debian"})

# Test AuthModule
user_id = svr.Insert("user",{"username":"andrew"})
person_class_id = svr.MODULES['AuthModule']['functions']['GetUserClassByName']("Person",svr)
firstname_user_prop_id = svr.MODULES['AuthModule']['functions']['GetUserClassPropertyByName']("First name",svr)
lastname_user_prop_id = svr.MODULES['AuthModule']['functions']['GetUserClassPropertyByName']("Last name",svr)
svr.Insert("user_class_uses",{"user":user_id,"class":person_class_id})
svr.Insert("user_prop",{"user":user_id,"prop":firstname_user_prop_id,"val":"Andrew"})
svr.Insert("user_prop",{"user":user_id,"prop":lastname_user_prop_id,"val":"Nilsson"})
admin_role_id = svr.Insert("role",{"name":"Administrator"})
email_role_id = svr.Insert("role",{"name":"Email user"})
svr.Insert("role_user",{"user":user_id,"role":admin_role_id})
group_id = svr.Insert("user_group",{"name":"E-mail Account Holders"})
svr.Insert("user_group_member",{"user_group":group_id,"user":user_id})
svr.Insert("user_group_role",{"user_group":group_id,"role":email_role_id})
res_type = svr.Insert("resource_type",{"name":"File folder"})
folder_descr_attr_id = svr.Insert("resource_type_attr",{"restype":res_type,"name":"Folder name"})
res_id = svr.Insert("resource",{"name":"Confidential Files","restype":res_type})
svr.Insert("resource_attr",{"resource":res_id,"attr":folder_descr_attr_id,"val":"Folder contains confidential files"})
svr.Insert("access_role",{"resource":res_id,"role":admin_role_id,"access":15})

# Generate OAuth credentials and token
svr.MODULES['AuthModule']['functions']['GenerateOAuthCreds'](user_id,svr)
svr.MODULES['AuthModule']['functions']['GenerateToken'](user_id,svr)