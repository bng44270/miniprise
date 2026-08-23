from json import dumps as dict2str, loads as str2dict
from threading import Timer
from os import rename
from glob import glob as listfilespec
from os.path import exists, getsize
from re import match as regex_match, compile as str2regex, sub as regex_sub
import sqlite3
import gzip

typeof = lambda v : type(v).__name__

class DataDef(list):
  """
    DataDef (extends Python List object)

    DataTypes:

      StringType - string data
      NumberType - numeric data (int or float)
      BooleanType - boolean data
    
    Usage:

      d = DataDef({"name":"StringType","age":"NumberType","retired":"BooleanType"})
      
  """
  def __init__(self,fields,data=[],skipfieldval=False):
    self.TYPES = {}
    self.TYPES["StringType"] = "string"
    self.TYPES["NumberType"] = "number"
    self.TYPES["BooleanType"] = "boolean"
    
    self.TYPEMAP = {}
    self.TYPEMAP["float"] = "number"
    self.TYPEMAP["int"] = "number"
    self.TYPEMAP["str"] = "string"
    self.TYPEMAP["bool"] = "boolean"
    
    if not skipfieldval:
      if not self._validatefields(fields):
        raise Exception(f"Invalid schema definition ({str(fields)})")
    
    self.FIELDS = fields
    
    self.__addqueryopts()
    
    if len(data) > 0:
      for row in data:
        self.Insert(row)
  
  def AddField(self,fname,ftype):
    """
      # Extend schema by adding type
      d.AddField("town","StringType")
    """
    if not self._validatefields({fname:ftype}):
      raise Exception(f"Invalid schema update ({fname}:{ftype})")
    
    self.FIELDS[fname] = ftype
    for row in self:
      row[fname] = None
  
  def Delete(self,q):
    """
      # Delete records where age is 70-79
      d.Delete([("age","GE",70),("age","LE",79)])

      # Delete records where age is 19
      d.Delete([("age","EQ",19)])

      # Delete records where age is 30 and name starts with "Jan"
      d.Delete([("age","EQ",30),("name","ST","Jan")])
    
      Available operators:
        EQ => Equal
        NE => Not Equal
        GT => Greater Than
        LT => Less Than
        GE => Greater Than or Equal
        LE => Less Thank or Equal
        ST => Starts With
        EN => Ends with
        CN => Contains
    """
    r = [i for (i,v) in enumerate(self) if len([a for a in q if self.CONDS[a[1]](a[0],a[2])]) == len(q)]
    
    for thisidx in r:
      del self[thisidx]
  
  def Update(self,q,updates=[]):
    """
      # Set retired to True where age is 67-69
      d.Update([("age","GE",67),("age","LE"69)],[("retired",True)])
    """
    r = [i for (i,v) in enumerate(self) if len([a for a in q if self.CONDS[a[1]](a[0],a[2])]) == len(q)]
    
    for thisidx in r:
      for thisupdate in updates:
        if not self.__validateupdate(thisupdate):
          raise Exception(f"Invalid update ({str(thisupdate)})")
        
        self[thisidx][thisupdate[0]] = thisupdate[1]          
  
  def Query(self,q):
    """
      # Query for records where age is between 40 and 59
      result = d.Query([("age","GE",40),("age","LE"59)])
    """
    if not self.__validatequery(q):
      raise Exception(f"Invalid query ({str(q)})")
    
    result = []
    
    r = [i for (i,v) in enumerate(self) if len([a for a in q if self.CONDS[a[1]](a[0],a[2])]) == len(q)]
    
    for thisidx in r:
      result.append(self[thisidx])
    
    return result
  
  def Insert(self,row):
    """
      # Valid Inserts
      d.insert({"name":"Bob","age":43,"retired":False})
      d.insert({"name":"Jim","age":30,"retired":False})
      d.insert({"name":"Dave","age":71,"retired":True})
      d.insert({"name":"Joe","age":19})

      # Invalid insert will raise an exception (age must be a number)
      d.insert({"name":"Zeke","age":"43","retired":False})
    """
    if not self.__validaterow(row):
      raise Exception(f"Invalid insert ({str(row)})")
    
    self.append(row)
  
  def __validatequery(self,q):
    for thisquery in q:
      if not len(thisquery) == 2:
        return False
      
      if not thisquery[0] in self.FIELDS:
        return False
    
    return True
  
  def __validateupdate(self,fieldupdate):
    if not len(fieldupdate) == 2:
      return False
    
    if not self.__validaterow({fieldupdate[0]:fieldupdate[1]}):
      return False
    
    return True
  
  def __validaterow(self,row):
    for thisfield in row.keys():
      if not thisfield in self.FIELDS.keys():
        return False
      
      if not self.TYPES[self.FIELDS[thisfield]] == self.TYPEMAP[typeof(row[thisfield])]:
        return False
    
    return True
  
  def _validatefields(self,fields):
    validfields = [a for a in fields.values() if a in self.TYPES.keys()]
    
    return True if len(validfields) == len(fields) else False
  
  def __addqueryopts(self):
    self.CONDS = {}
    self.CONDS["EQ"] = self.__q_equals
    self.CONDS["NE"] = self.__q_notequal
    self.CONDS["GT"] = self.__q_greaterthan
    self.CONDS["GE"] = self.__q_greaterthanorequal
    self.CONDS["LT"] = self.__q_lessthan
    self.CONDS["LE"] = self.__q_lessthanorequal
    self.CONDS["ST"] = self.__q_startswith
    self.CONDS["EN"] = self.__q_endswith
    self.CONDS["CN"] = self.__q_contains
  
  def __q_equals(self,v1,v2):
    return v1 == v2
  
  def __q_notequal(self,v1,v2):
    return not v1 == v2
  
  def __q_greaterthan(self,v1,v2):
    return v1 > v2
  
  def __q_lessthan(self,v1,v2):
    return v1 < v2
  
  def __q_greaterthanorequal(self,v1,v2):
    return v1 >= v2
  
  def __q_lessthanorequal(self,v1,v2):
    return v1 <= v2
  
  def __q_startswith(self,v1,v2):
    return str(v1).startswith(v2)
  
  def __q_endswith(self,v1,v2):
    return str(v1).endswith(v2)
  
  def __q_contains(self,v1,v2):
    return str(v2) in str(v1)

class pkey(int):
  def __new__(c,v):
    return super().__new__(c,v)

class fkey(int):
  def __new__(c,v):
    return super().__new__(c,v)

class SqliteDef(DataDef):
  """
    SqliteDef (extends above DataDef object)

    Usage:
    
      # Initialize dataset from JSON file
      # NOTE:  DataCache requiring identical fields on each record to accurately detect schema
      mydata = SqliteDef({"name":"StringType","age":"NumberType","retired":"BooleanType"},'/path/to/file.db')
      
      # After first initializing data cache with schema, the schema is cached also.
      # For subsequent executions, the schema can be omitted as follows:
      mydata = DataCache(file='/path/to/people.json')

      # Caching may also be configured to reoccur after a specified number of seconds
      # In this example caching occurs every 30 seconds:
      mydata = DataCache(file='/path/to/people.json',cachetime=30)
  """
  
  def __init__(self,fields=None,dbfile="",table="",uselog=False):
    self.USE_LOG = uselog
    
    if self.USE_LOG:
      self.LOG_BUFFER = []
    
    self.FieldTypeMap = {}
    self.FieldTypeMap["StringType"] = "TEXT"
    self.FieldTypeMap["NumberType"] = "REAL"
    self.FieldTypeMap["BooleanType"] = "INTEGER CHECK (<F> IN (0,1)) DEFAULT 0"
    self.FieldTypeMap["PrimaryKeyType"] = "INTEGER PRIMARY KEY AUTOINCREMENT"
    self.FieldTypeMap["ForeignKeyType"] = "INTEGER"
    
    if len(dbfile) == 0:
      raise Exception("No DB specified")
    
    if len(table) == 0:
      raise Exception("No table name provided")
    
    if not exists(dbfile):
      self.__createdbfile(dbfile)
    
    self.TABLE = table
    self.DBFILE = dbfile
    
    self.__connect()
    
    if not fields:
      fields = self.__readschema()
      
      if len(fields.keys()) == 0:
        raise Exception("No schema provided")

    super().__init__(fields,skipfieldval=True)
    
    self.TYPES["PrimaryKeyType"] = "primarykey"
    self.TYPES["ForeignKeyType"] = "foreignkey"
    
    self.TYPEMAP["pkey"] = "primarykey"
    self.TYPEMAP["fkey"] = "foreignkey"
    
    if not self._validatefields({k:v for k,v in fields.items() if not k.startswith("REF_")}):
      raise Exception(f"Invalid schema definition ({str(fields)})")
    
    if not self.__checktable():
      self.__createtable(table,fields)
    
    self.__addfieldconv()
    self.__addsqlops()
  
  def GetPrimaryKeyValue(self,q=[]):
    pkfieldar = [a for a in self.FIELDS.keys() if self.FIELDS[a] == "PrimaryKeyType"]
    if not len(pkfieldar) == 1:
      return None
    
    result = self.Query(q,pkfieldar,1)
    
    if not len(result) == 1:
      return None
    
    return (pkfieldar[0],result[0][0])
      
  
  def RunSql(self,s,count=0):
    results = self.CONN.cursor().execute(s)
    
    cmd = s.split(' ')[0]
    
    if cmd.upper() in ['INSERT','UPDATE','ALTER','CREATE','DELETE','DROP']:
      if self.USE_LOG:
        self.LOG_BUFFER.append(s)
      
      self.CONN.commit()
    else:
      return results.fetchall() if count == 0 else results.fetchmany(count)
  
  def AddField(self,fname,ftype):
    super().AddField(fname,ftype)
    self.RunSql(f'ALTER TABLE {self.TABLE} ADD COLUMN {fname} {ftype};')
  
  def Insert(self,row={}):
    insert_sql_fields = ",".join([a for a in row.keys()])
    insert_sql_values = ",".join([self.FIELD_CONV[a](row[a]) for a in row.keys()])
    insert_sql = f'INSERT INTO {self.TABLE}(' + insert_sql_fields + ") VALUES (" + insert_sql_values + ");"
    self.RunSql(insert_sql)
  
  def BulkInsert(self,rowset=[]):
    insert_sql_fields = ",".join([a for a in rowset[0].keys()])
    
    insert_sql_value_list = []
    
    for row in rowset:
      insert_sql_value_list.append("(" + ",".join([self.FIELD_CONV[a](row[a]) for a in row.keys()]) + ")")
    
    insert_sql_values = ",".join(insert_sql_value_list)
    
    insert_sql = f'INSERT INTO {self.TABLE}(' + insert_sql_fields + ") VALUES " + insert_sql_values + ";"
    self.RunSql(insert_sql)
  
  def Delete(self,q):
    delete_sql_where = " AND ".join([self.COMPARES[(self.FIELDS[a[0]],a[1],self.FIELDS[a[0]])](a[0],a[2]) for a in q])
    delete_sql = f'DELETE FROM {self.TABLE} WHERE ' + delete_sql_where + ';'    
    self.RunSql(delete_sql)
  
  def Update(self,q,updates=[]):
    update_sql_set = ','.join([f'{a[0]} = {self.FIELD_CONV[a[0]](a[1])}' for a in updates])
    update_sql_where = " AND ".join([self.COMPARES[(self.FIELDS[a[0]],a[1],self.FIELDS[a[0]])](a[0],a[2]) for a in q])
    update_sql = f'UPDATE {self.TABLE} SET ' + update_sql_set + " WHERE " + update_sql_where + ';'
    self.RunSql(update_sql)
  
  def Query(self,q=[],f=[],count=0):
    query_sql_fields = ','.join(f) if len(f) > 0 else "*"
    query_sql_where = " AND ".join([self.COMPARES[(self.FIELDS[a[0]],a[1],self.FIELDS[a[0]])](a[0],a[2]) for a in q])
    query_sql = f'SELECT ' + query_sql_fields + f' FROM {self.TABLE}' + ((' WHERE ' + query_sql_where) if len(q) > 0 else "") + ';'
    result = self.RunSql(query_sql,count)
    
    return result
  
  def Cache(self):
    select_sql_fields = ",".join([a for a in self.FIELDS.keys()])
    select_sql = f"SELECT " + select_sql_fields + f" FROM {self.TABLE};"
    result = self.RunSql(select_sql)
    
    for sql_row in result:
      row = {}
      for field in [(i,v) for i,v in enumerate(self.FIELDS.keys())]:
        row[field[1]] = sql_row[field[0]]
      
      super().Insert(row)
  
  def __createtable(self,table,fields):
    create_sql_fields = ",".join([f'{a} {self.FieldTypeMap[fields[a]].replace("<F>",a)}' for a in fields.keys() if not a.startswith("REF_")])
    create_sql_fk = ",".join([f"FOREIGN KEY ({a}) REFERENCES {fields["REF_" + a].split('.')[0] + "(" + fields["REF_" + a].split('.')[1] + ")"}" for a in [regex_sub(r'REF_','',b) for b in fields.keys() if b.startswith("REF_")]])
    create_sql = f'CREATE TABLE {table} (' + create_sql_fields + (("," + create_sql_fk) if len(create_sql_fk) > 0 else "") + ');'
    self.RunSql(create_sql);
      
  def __checktable(self):
    check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.TABLE}';"
    return len(self.RunSql(check_sql,1)) == 1
  
  def __createdbfile(self,f):
    c = sqlite3.connect(f)
    c.commit()
  
  def __del__(self):
    self.CONN.close()
  
  def __readschema(self):
    f = self.__getsqlfieldlist();
    d = {}
    
    for this_f in f:
      bare_field = this_f[1].replace(this_f[0],"<F>")
      ddtype = self.__unmapfieldtype(bare_field)
      d[this_f[0]] = ddtype
    
    return d
  
  def __connect(self):
    self.CONN = sqlite3.connect(self.DBFILE)
  
  def __unmapfieldtype(self,t):
    if not t in self.FieldTypeMap.values():
      raise Exception(f"Invalid field type ({t})")
    
    return [a[0] for a in self.FieldTypeMap.items() if a[1] == t][0]
  
  def __getsqlfieldlist(self):
    read_sql = f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{self.TABLE}';"
    result =  self.RunSql(read_sql,1)
    
    if not len(result) == 1:
      raise Exception(f"Schema error:  table not found ({self.TABLE})")
    else:
      create_sql = result[0][0]
      field_list = [[a.strip().split(" ")[0]," ".join(a.strip().split(" ")[1:])] for a in regex_sub(r'^CREATE TABLE [^\(]+\((.+)\)$','\\1',create_sql).split(',') if not a.strip().startswith('FOREIGN KEY')]
      return field_list
  
  def __addfieldconv(self):
    self.FIELD_CONV = {}
    
    for f in [a for a in self.FIELDS.keys() if not a.startswith("REF_")]:
      if self.FIELDS[f] == "StringType":
        self.FIELD_CONV[f] = self.__str2sql
      elif self.FIELDS[f] == "NumberType" or self.FIELDS[f] == "BooleanType" or self.FIELDS[f] == "PrimaryKeyType" or self.FIELDS[f] == "ForeignKeyType":
        self.FIELD_CONV[f] = self.__num2sql
      else:
        raise Exception(f'Invalid field type ({f})')
  
  def __addsqlops(self):
    self.COMPARES = {}
    self.COMPARES[("StringType","EQ","StringType")] = self.__streq2sql
    self.COMPARES[("StringType","NE","StringType")] = self.__strne2sql
    self.COMPARES[("StringType","ST","StringType")] = self.__strst2sql
    self.COMPARES[("StringType","EN","StringType")] = self.__stren2sql
    self.COMPARES[("StringType","CN","StringType")] = self.__strcn2sql
    
    self.COMPARES[("NumberType","EQ","NumberType")] = self.__numeq2sql
    self.COMPARES[("NumberType","NE","NumberType")] = self.__numne2sql
    self.COMPARES[("NumberType","GT","NumberType")] = self.__numgt2sql
    self.COMPARES[("NumberType","LT","NumberType")] = self.__numlt2sql
    self.COMPARES[("NumberType","GE","NumberType")] = self.__numge2sql
    self.COMPARES[("NumberType","LE","NumberType")] = self.__numle2sql
    
    self.COMPARES[("BooleanType","EQ","BooleanType")] = self.__numeq2sql
    self.COMPARES[("BooleanType","NE","BooleanType")] = self.__numne2sql
    self.COMPARES[("BooleanType","GT","BooleanType")] = self.__numgt2sql
    self.COMPARES[("BooleanType","LT","BooleanType")] = self.__numlt2sql
    self.COMPARES[("BooleanType","GE","BooleanType")] = self.__numge2sql
    self.COMPARES[("BooleanType","LE","BooleanType")] = self.__numle2sql
    
    self.COMPARES[("PrimaryKeyType","EQ","PrimaryKeyType")] = self.__numeq2sql
    self.COMPARES[("PrimaryKeyType","NE","PrimaryKeyType")] = self.__numne2sql
    self.COMPARES[("PrimaryKeyType","GT","PrimaryKeyType")] = self.__numgt2sql
    self.COMPARES[("PrimaryKeyType","LT","PrimaryKeyType")] = self.__numlt2sql
    self.COMPARES[("PrimaryKeyType","GE","PrimaryKeyType")] = self.__numge2sql
    self.COMPARES[("PrimaryKeyType","LE","PrimaryKeyType")] = self.__numle2sql
    
    self.COMPARES[("ForeignKeyType","EQ","ForeignKeyType")] = self.__numeq2sql
    self.COMPARES[("ForeignKeyType","NE","ForeignKeyType")] = self.__numne2sql
    self.COMPARES[("ForeignKeyType","GT","ForeignKeyType")] = self.__numgt2sql
    self.COMPARES[("ForeignKeyType","LT","ForeignKeyType")] = self.__numlt2sql
    self.COMPARES[("ForeignKeyType","GE","ForeignKeyType")] = self.__numge2sql
    self.COMPARES[("ForeignKeyType","LE","ForeignKeyType")] = self.__numle2sql
  
  def __str2sql(self,v):
    return f"'{v}'"
  
  def __num2sql(self,v):
    return f"{v}"
  
  def __streq2sql(self,v1,v2):
    return v1 + " = " + self.__str2sql(v2)
  
  def __strne2sql(self,v1,v2):
    return v1 + " <> " + self.__str2sql(v2)
  
  def __strst2sql(self,v1,v2):
    return v1 + " LIKE " + regex_sub(r"'$","%'",self.__str2sql(v2))
  
  def __stren2sql(self,v1,v2):
    return v1 + " LIKE " + regex_sub(r"^'","'%",self.__str2sql(v2))
  
  def __strcn2sql(self,v1,v2):
    return v1 + " LIKE " + regex_sub(r"^'([^']+)'",r"'%\1%'",self.__str2sql(v2))
  
  def __numeq2sql(self,v1,v2):
    return v1 + " = " + self.__num2sql(v2)
  
  def __numne2sql(self,v1,v2):
    return v1 + " <> " + self.__num2sql(v2)
  
  def __numgt2sql(self,v1,v2):
    return v1 + " > " + self.__num2sql(v2)
  
  def __numlt2sql(self,v1,v2):
    return v1 + " < " + self.__num2sql(v2)
  
  def __numge2sql(self,v1,v2):
    return v1 + " >= " + self.__num2sql(v2)
  
  def __numle2sql(self,v1,v2):
    return v1 + " <= " + self.__num2sql(v2)
  
  def CreateSqliteTable(fields=None,dbfile="",table="",uselog=False):
    return SqliteDef(fields,dbfile,table,uselog)

class SqliteDefGroup(dict):
  def __init__(self,dbfile="",maxlog=10000000):
    if len(dbfile) == 0:
      raise Exception("No DB specified")
    
    if not exists(dbfile):
      self.__createdbfile(dbfile)
      
    self.DBFILE = dbfile
    self.LOGFILE = dbfile + ".log.gz"
    self.MAX_LOG = maxlog
    
    self.NEXT_LOG_SAVE = len(listfilespec(self.LOGFILE + ".*")) + 1
    
    if self.__class__.__name__ == "SqliteDefGroup":
      self.__populatetables()
  
  def Insert(self,t,row={}):
    self[t].Insert(row,self)
    self.__commitlogs(t)
  
  def BulkInsert(self,t,rowset=[]):
    self[t].BulkInsert(rowset,self)
    self.__commitlogs(t)
  
  def Update(self,t,q,update=[]):
    self[t].Update(q,update,self)
    self.__commitlogs(t)
  
  def Delete(self,t,q):
    self[t].Delete(q,self)
    self.__commitlogs(t)
  
  def Query(self,t,q=[],f=[]):
    return self[t].Query(q,f)
  
  def LoadModule(self,t,m):
    self[t].LoadModule(m)
  
  def CreateTable(self,t,f):
    self[t] = SqliteDef.CreateSqliteTable(f,self.DBFILE,t,True)
    self.__commitlogs(t)
  
  def ExistsTable(self,t):
    return t in self.keys()
  
  def __commitlogs(self,t):
    l = self[t].LOG_BUFFER.copy()
    self[t].LOG_BUFFER.clear()
    
    l.reverse()
    
    logfile = gzip.open(self.LOGFILE,"at",encoding='utf-8')
    
    for line in l:
      logfile.write(line + "\n")
    
    logfile.close()
    
    if getsize(self.LOGFILE) > self.MAX_LOG:
      rename(self.LOGFILE,self.LOGFILE + self.NEXT_LOG_SAVE)
      self.NEXT_LOG_SAVE = self.NEXT_LOG_SAVE + 1
  
  def __populatetables(self):
    for this_table in self.__listtables():
      self[this_table] = SqliteDef.CreateSqliteTable(dbfile=self.DBFILE,table=this_table,uselog=True)
  
  def __listtables(self):
    t = []
    c = sqlite3.connect(self.DBFILE)
    resp = c.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND name <> 'sqlite_sequence';")
    
    for table in resp.fetchall():
      t.append(table[0])
    
    return t
  
  def __createdbfile(self,f):
    c = sqlite3.connect(f)
    c.commit()


class SqliteMiddleware(SqliteDef):
  """
    SqliteMiddleware - implement middleware containing Pre- and Post- Insert, Update, and Delete events
  
    Usage:
      
      1. Create class inheriting SqliteMiddlewareModule
      2. Within the new class write one or more of the following methods:
        - BeforeInsert(row,db_def)
        - AfterInsert(row,db_def)
        - BeforeUpdate(query,updates,db_def)
        - AfterUpdate(query,updates,db_def)
        - BeforeDelete(query,db_def)
        - AfterDelete(query,db_def)
  """
  def __init__(self,fields=[],dbfile="",table="",uselog=False):
    super().__init__(fields,dbfile,table,uselog)
    self.MODS = {}
  
  def Insert(self,row={},ref=None):
    passdata = {}
    for mod_name in self.MODS.keys():
      passdata[mod_name] = None
    
    for mod_name in self.MODS.keys():
      passdata[mod_name] = self.MODS[mod_name].BeforeInsert(row,(ref if ref else self)) or False
    
    super().Insert(row)
    
    for mod_name in self.MODS.keys():
      self.MODS[mod_name].AfterInsert(row,(ref if ref else self),passdata[mod_name])
  
  def BulkInsert(self,rowset=[],ref=None):
    passdata = {}
    for mod_name in self.MODS.keys():
      passdata[mod_name] = None
    
    for row in rowset:
      for mod_name in self.MODS.keys():
        passdata[mod_name] = self.MODS[mod_name].BeforeInsert(row,(ref if ref else self)) or False
    
    super().BulkInsert(rowset)
    
    for row in rowset:
      for mod_name in self.MODS.keys():
        self.MODS[mod_name].AfterInsert(row,(ref if ref else self),passdata[mod_name])
  
  def Update(self,q,update=[],ref=None):
    passdata = {}
    for mod_name in self.MODS.keys():
      passdata[mod_name] = None
    
    for mod_name in self.MODS.keys():
      passdata[mod_name] = self.MODS[mod_name].BeforeUpdate(q,update,(ref if ref else self)) or False
    
    super().Update(q,update)
    
    for mod_name in self.MODS.keys():
      self.MODS[mod_name].AfterUpdate(q,update,(ref if ref else self),passdata[mod_name])
  
  def Delete(self,q,ref=None):
    passdata = {}
    for mod_name in self.MODS.keys():
      passdata[mod_name] = None
    
    for mod_name in self.MODS.keys():
      passdata[mod_name] = self.MODS[mod_name].BeforeDelete(q,(ref if ref else self)) or False
    
    super().Delete(q)
    
    for mod_name in self.MODS.keys():
      self.MODS[mod_name].AfterDelete(q,(ref if ref else self),passdata[mod_name])
  
  def Query(self,q=[],f=[],count=0):
    return super().Query(q,f,count)
  
  def LoadModule(self,m):
    if not issubclass(m,SqliteMiddlewareModuleBase):
      raise Exception("Module must extend SqliteMiddlewareModuleBase")
    
    self.MODS[m.__name__] = m()
  
  def __createtable(self,t,f):
    super().__createtable(t,f)
  
  def CreateMiddlewareTable(fields=[],dbfile="",table="",uselog=False):
    return SqliteMiddleware(fields,dbfile,table,uselog)


class SqliteMiddlewareGroup(SqliteDefGroup):
  def __init__(self,dbfile="",maxlog=10000000):
    super().__init__(dbfile,maxlog)
    
    self.__populatetables()
  
  def LoadModule(self,t,m):
    self[t].LoadModule(m)
  
  def CreateTable(self,t,f):
    self[t] = SqliteMiddleware(f,self.DBFILE,t,True)
    self._SqliteDefGroup__commitlogs(t)
  
  def __populatetables(self):
    for this_table in self._SqliteDefGroup__listtables():
      self[this_table] = SqliteMiddleware(dbfile=self.DBFILE,table=this_table,uselog=True)


class SqliteMiddlewareModuleBase:
  def BeforeInsert(self,row,dbdef):
    pass
  
  def AfterInsert(self,row,dbdef,passed):
    pass
  
  def BeforeUpdate(self,q,update,dbdef):
    pass
  
  def AfterUpdate(self,q,update,dbdef,passed):
    pass
  
  def BeforeDelete(self,q,dbdef):
    pass
  
  def AfterDelete(self,q,dbdef,passed):
    pass

  
class SqliteMiddlewareLibrary:
  def FieldChangesToEmpty(f,row):
    if f in row.keys():
      if len(row[f]) == 0:
        return True
    
    return False
  
  def FieldChanges(f,row):
    if f in row.keys():
      if len(row[f]) >  0:
        return True
    
    return False
  
  def FieldChangesTo(f,row,v):
    if f in row.keys():
      if row[f] == v:
        return True
    
    return False
  
  def FieldChangesGreaterThan(f,row,v):
    if f in row.keys():
      if row[f] > v:
        return True
    
    return False
  
  def FieldChangesLessThan(f,row,v):
    if f in row.keys():
      if row[f] < v:
        return True
    
    return False

