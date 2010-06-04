import sqlalchemy as sa
from sqlalchemy import orm

from gridmonitor.model.nagios import meta

# XXX service-table is only a subset of ndoutils nagios_services table

t_service = sa.Table("nagios_services", meta.metadata,
    sa.Column("service_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("config_type",sa.types.SMALLINT(6)),
    sa.Column("host_object_id",sa.types.INT(11)),
    sa.Column("service_object_id",sa.types.INT(11)),
    sa.Column("display_name",sa.types.VARCHAR(64))
)

t_servicestatus = sa.Table("nagios_servicestatus", meta.metadata,
    sa.Column("servicestatus_id",sa.types.INT(11),primary_key=True),
    sa.Column("instance_id",sa.types.SMALLINT(6)),
    sa.Column("service_object_id",None, sa.ForeignKey("nagios_services.service_object_id")),
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
    sa.Column("last_time_ok",sa.types.DATETIME),
    sa.Column("last_time_warning",sa.types.DATETIME),
    sa.Column("last_time_unknown",sa.types.DATETIME),
    sa.Column("last_time_critical",sa.types.DATETIME),
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
    sa.Column("obsess_over_service",sa.types.SMALLINT(6)),
    sa.Column("modified_service_attributes",sa.types.INT(11)),
    sa.Column("event_handler",sa.types.VARCHAR(255)),
    sa.Column("check_command",sa.types.VARCHAR(255)),
    sa.Column("normal_check_interval",sa.types.FLOAT),
    sa.Column("retry_check_interval",sa.types.FLOAT),
    sa.Column("check_timeperiod_object_id",sa.types.INT(11)))

class Service(object):
    pass

class ServiceStatus(object):
    pass


orm.mapper(Service,t_service, properties=dict(
        status=orm.relation(ServiceStatus,
                primaryjoin=(t_servicestatus.c.service_object_id == t_service.c.service_object_id)))
)

orm.mapper(ServiceStatus,t_servicestatus)
