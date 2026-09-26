from . import SqliteMiddlewareModuleBase

class TicketModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("ticket_type",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("ticket_type_stage",{"id":"PrimaryKeyType","tickettype":"ForeignKey","name":"StringType","order":"NumberType","REF_tickettype":"ticket_type.id"})
    self.AddTable("ticket_type_attr",{"id":"PrimaryKeyType","name":"StringType","tickettype":"ForeignKeyType","REF_tickettype":"ticket_type.id"})
    self.AddTable("ticket",{"id":"PrimaryKeyType","description":"StringType","tickettype":"ForeignKeyType","REF_tickettype":"ticket_type.id"})
    self.AddTable("ticket_attr",{"ticket":"ForeignKeyType","attr":"ForeignKeyType","val":"StringType","REF_ticket":"ticket.id","REF_attr":"ticket_type_attr.id"})
    self.AddTable("ticket_stage",{"ticket":"ForeignKeyType","stage":"ForeignKeyType","REF_ticket":"ticket.id","REF_stage":"ticket_type_stage.id"})

    self.AddFunction(self.CheckAccessRead)
  
  def InitModule(self,dbref,mods):
    pass