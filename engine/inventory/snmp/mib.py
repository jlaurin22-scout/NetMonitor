"""
NetMonitor SNMP MIB-II constants.

This module contains the standard SNMP v2c System OIDs used during
device inventory. These OIDs are defined by MIB-II and are supported
by nearly every SNMP-enabled device.
"""

# System Group (MIB-II)

SYS_DESCR = "1.3.6.1.2.1.1.1.0"
SYS_OBJECT_ID = "1.3.6.1.2.1.1.2.0"
SYS_UPTIME = "1.3.6.1.2.1.1.3.0"
SYS_CONTACT = "1.3.6.1.2.1.1.4.0"
SYS_NAME = "1.3.6.1.2.1.1.5.0"
SYS_LOCATION = "1.3.6.1.2.1.1.6.0"


SYSTEM_OIDS = {
    "description": SYS_DESCR,
    "object_id": SYS_OBJECT_ID,
    "uptime": SYS_UPTIME,
    "contact": SYS_CONTACT,
    "name": SYS_NAME,
    "location": SYS_LOCATION,
}
