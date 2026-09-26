from . import SqliteMiddlewareModuleBase

class KPIModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("kpi_metric",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("kpi_registry",{"id":"PrimaryKeyType","table":"StringType","field":"StringType","metric":"ForeignKeyType","REF_metric":"kpi_metric.id"})
    self.AddTable("kpi_values",{"kpi":"ForeignKeyType","val":"NumberType","date":"NumberType","REF_kpi":"kpi_registry.id"})
    