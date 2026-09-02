# miniprise
A Python library for building an enterprise-level, feature-rich platform using Flask and SQLite

To test the CMDB example app:  
1. Run ```$ python3```  
2. Run ```>>> from tests.cmdb import svr```  

```svr``` contains an instance of SqliteMiddlewareGroup configured with the CMDB module.  The related database file will be created, tables create, and CMDB-related middleware modules will be loaded.
  
  
## Planned architecture  
Core Components:  
* Database Access  
* Middleware  
* Data Rendering  
* Front End  
* Integrations  
  
Future Core Extensions:  
* KPI  
* Ticketing  
* CMDB  
* Space Management
* more?  
  
Note that only the Middleware and data access components are under development.  The front end UI, data rendering module, and other components have yet to be developed.  
<img src="https://github.com/bng44270/miniprise/blob/main/media/architecture.png" />
  
  

