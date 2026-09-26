from .. import SqliteMiddlewareModuleBase

class ContentModule(SqliteMiddlewareModuleBase):
  def __init__(self,mods=[]):
    super().__init__()

    self.AddTable("content_template",{"id":"PrimaryKeyType","name":"StringType","content":"StringType"})
    #####################
    #
    # content.type
    #     1 => Text
    #     2 => Binary
    #     3 => URL Map
    #     4 => Content Collection
    #
    #####################
    self.AddTable("content",{"id":"PrimaryKeyType","type":"NumberType","name":"StringType","content":"StringType","template:":"ForeignKeyType","REF_template":"content_template.id"})
    self.AddTable("content_map",{"content":"ForeignKeyType","uri":"StringType","REF_content":"content.id"})
    self.AddTable("content_collection",{"id":"PrimaryKeyType","name":"StringType"})
    self.AddTable("content_collection_item",{"collection":"ForeignKeyType","content":"ForeignKeyType","order":"NumberType","REF_collection":"content_collection.id","REF_content":"content.id"})

    