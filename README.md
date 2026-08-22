# miniprise
A Python library for building an enterprise-level, feature-rich backend using SQLite

To test the CMDB example app:  
1. Run ```$ python3```  
2. Run ```>>> from test.cmdb import InitiailizeCMDB```  
3. Run ```>>> svr = InitializeCMDB()```

```svr``` contains an instance of SqliteMiddlewareGroup.  The related database file will be created, tables create, and CMDB-related middleware modules will be loaded.
  
  
## Planned architecture diagram
<img src="https://github.com/bng44270/miniprise/blob/main/media/architecture.png" />
