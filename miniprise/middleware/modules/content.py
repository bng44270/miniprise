from .. import SqliteMiddlewareModuleBase

class ContentModule(SqliteMiddlewareModuleBase):
  def __init__(self):
    super().__init__()

    self.AddTable('content_template',{"id":"PrimaryKeyType","name":"StringType","content":"StringType"})
    self.AddTable('content',{"id":"PrimaryKeyType","name":"StringType","content":"StringType","template:":"ForeignKeyType","binary":"BooleanType","REF_template":"content_template.id"})
    self.AddTable('content_map',{"content":"ForeignKeyType","uri":"StringType","REF_content":"content.id"})
    