from miniprise.middleware import SqliteMiddlewareGroup
from miniprise.middleware.modules import cmdb, auth

svr = SqliteMiddlewareGroup('cmdb.db')
svr.LoadModule(auth.AuthModule)
svr.LoadModule(cmdb.CIModule)

