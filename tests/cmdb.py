from miniprise.middleware import SqliteMiddlewareGroup
from miniprise.middleware.modules import cmdb as mods

svr = SqliteMiddlewareGroup('cmdb.db')
svr.LoadModule(mods.CIModule)
