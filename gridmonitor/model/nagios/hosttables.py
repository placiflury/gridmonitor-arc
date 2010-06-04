import sqlalchemy as sa
from sqlalchemy import orm

from gridmonitor.model.nagios import meta


t_hostgroup = sa.Table("nagios_hostgroups", meta.metadata,
    sa.Column("hostgroup_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("config_type",sa.types.SMALLINT(6)),
    sa.Column("hostgroup_object_id",sa.types.INT(11)),
    sa.Column("alias",sa.types.VARCHAR(255))
)

t_hostgroup_member = sa.Table("nagios_hostgroup_members", meta.metadata,
    sa.Column("hostgroup_member_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("hostgroup_id",None, sa.ForeignKey("nagios_hostgroups.hostgroup_id")),
    sa.Column("host_object_id",None,sa.ForeignKey("nagios_hosts.host_object_id"))
)

# XXX host-table is only a subset of ndoutils nagios_hosts table
t_host = sa.Table("nagios_hosts", meta.metadata,
    sa.Column("host_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("config_type",sa.types.SMALLINT(6)),
    sa.Column("host_object_id",sa.types.INT(11), unique=True, nullable=False),
    sa.Column("alias",sa.types.VARCHAR(64)),
    sa.Column("display_name",sa.types.VARCHAR(64))
)

t_hoststatus = sa.Table("nagios_hoststatus", meta.metadata,
    sa.Column("hoststatus_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("host_object_id",None, sa.ForeignKey("nagios_hosts.host_object_id")),
    sa.Column("status_update_time",sa.types.DATETIME),
    sa.Column("output",sa.types.VARCHAR(255)),
    sa.Column("perfdata",sa.types.VARCHAR(255)),
    sa.Column("current_state",sa.types.SMALLINT(6)),
    sa.Column("has_been_checked",sa.types.SMALLINT(6)),
    sa.Column("should_be_scheduled",sa.types.SMALLINT(6)),
    sa.Column("current_check_attempt",sa.types.SMALLINT(6)),
    sa.Column("max_check_attempts",sa.types.SMALLINT(6)),
    sa.Column("last_check",sa.types.DATETIME),
    sa.Column("next_check",sa.types.DATETIME),
    sa.Column("check_type",sa.types.SMALLINT(6)),
    sa.Column("last_state_change",sa.types.DATETIME),
    sa.Column("last_hard_state_change",sa.types.DATETIME),
    sa.Column("last_hard_state",sa.types.SMALLINT(6)),
    sa.Column("last_time_up",sa.types.DATETIME),
    sa.Column("last_time_down",sa.types.DATETIME),
    sa.Column("last_time_unreachable",sa.types.DATETIME),
    sa.Column("state_type",sa.types.SMALLINT(6)),
    sa.Column("last_notification",sa.types.DATETIME),
    sa.Column("next_notification",sa.types.DATETIME),
    sa.Column("no_more_notifications",sa.types.SMALLINT(6)),
    sa.Column("notifications_enabled",sa.types.SMALLINT(6)),
    sa.Column("problem_has_been_acknowledged",sa.types.SMALLINT(6)),
    sa.Column("acknowledgement_type",sa.types.SMALLINT(6)),
    sa.Column("current_notification_number",sa.types.SMALLINT(6)),
    sa.Column("passive_checks_enabled",sa.types.SMALLINT(6)),
    sa.Column("active_checks_enabled",sa.types.SMALLINT(6)),
    sa.Column("event_handler_enabled",sa.types.SMALLINT(6)),
    sa.Column("flap_detection_enabled",sa.types.SMALLINT(6)),
    sa.Column("is_flapping",sa.types.SMALLINT(6)),
    sa.Column("percent_state_change",sa.types.FLOAT),
    sa.Column("latency",sa.types.FLOAT),
    sa.Column("execution_time",sa.types.FLOAT),
    sa.Column("scheduled_downtime_depth",sa.types.SMALLINT(6)),
    sa.Column("failure_prediction_enabled",sa.types.SMALLINT(6)),
    sa.Column("process_performance_data",sa.types.SMALLINT(6)),
    sa.Column("obsess_over_host",sa.types.SMALLINT(6)),
    sa.Column("modified_host_attributes",sa.types.INT(11)),
    sa.Column("event_handler",sa.types.VARCHAR(255)),
    sa.Column("check_command",sa.types.VARCHAR(255)),
    sa.Column("normal_check_interval",sa.types.FLOAT),
    sa.Column("retry_check_interval",sa.types.FLOAT),
    sa.Column("check_timeperiod_object_id",sa.types.INT(11))
)

class HostGroup(object):
    pass

class HostGroupMember(object):
    pass

class Host(object):
    pass

class HostStatus(object): 
    pass

orm.mapper(HostGroupMember,t_hostgroup_member, properties=dict(
        host=orm.relation(Host, 
                primaryjoin=(t_host.c.host_object_id == t_hostgroup_member.c.host_object_id)))
)

orm.mapper(HostGroup,t_hostgroup,properties=dict(
        members=orm.relation(HostGroupMember,
                    primaryjoin=(t_hostgroup_member.c.hostgroup_id == t_hostgroup.c.hostgroup_id)))
)

orm.mapper(Host,t_host, properties=dict(
        status=orm.relation(HostStatus,
                primaryjoin=(t_hoststatus.c.host_object_id == t_host.c.host_object_id)))
)

orm.mapper(HostStatus,t_hoststatus)

