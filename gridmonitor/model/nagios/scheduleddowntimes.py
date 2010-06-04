import sqlalchemy as sa
from sqlalchemy import orm
from gridmonitor.model.nagios import meta
from gridmonitor.model.nagios import objects as nagiosobjects

t_scheduleddowntime = sa.Table("nagios_scheduleddowntime",meta.metadata,
        sa.Column("scheduleddowntime_id",sa.types.INT(11),primary_key=True),
        sa.Column("instance_id",sa.types.SMALLINT(6)),
        sa.Column("downtime_type",sa.types.SMALLINT(6)),
        sa.Column("object_id",None, sa.ForeignKey("nagios_objects.object_id")),
        sa.Column("entry_time",sa.types.DATETIME),
        sa.Column("author_name",sa.types.VARCHAR(64)),
        sa.Column("comment_data",sa.types.VARCHAR(255)),
        sa.Column("internal_downtime_id",sa.types.INT(11)),
        sa.Column("triggered_by_id",sa.types.INT(11)),
        sa.Column("is_fixed",sa.types.SMALLINT(6)),
        sa.Column("duration",sa.types.SMALLINT(6)),
        sa.Column("scheduled_start_time",sa.types.DATETIME),
        sa.Column("scheduled_end_time",sa.types.DATETIME),
        sa.Column("was_started",sa.types.SMALLINT(6)),
        sa.Column("actual_start_time",sa.types.DATETIME),
        sa.Column("actual_start_time_usec",sa.types.INT(11))
)


class ScheduledDownTime(object):
    pass

orm.mapper(ScheduledDownTime,t_scheduleddowntime, properties=dict(
        generic_object=orm.relation(nagiosobjects.Object,
            primaryjoin=(nagiosobjects.t_object.c.object_id == t_scheduleddowntime.c.object_id)))
)
