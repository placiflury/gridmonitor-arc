import sqlalchemy as sa
from sqlalchemy import orm
from gridmonitor.model.nagios import meta

t_object = sa.Table("nagios_objects",meta.metadata,
        sa.Column("object_id",sa.types.INT(11),primary_key=True),
        sa.Column("instance_id",sa.types.SMALLINT(6)),
        sa.Column("objecttype_id",sa.types.SMALLINT(6)),
        sa.Column("name1",sa.types.VARCHAR(128)),
        sa.Column("name2",sa.types.VARCHAR(128)),
        sa.Column("is_active",sa.types.SMALLINT(6))
)


class Object(object):
    pass

orm.mapper(Object,t_object)
