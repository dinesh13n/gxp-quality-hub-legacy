"""Start-up exposure guard (BEH-SEC-08, AC-SEC-16, HAR-05): default bind 127.0.0.1; a non-loopback bind is refused
with E-SEC-EXPOSURE-NOT-APPROVED unless network.exposure_approved is true WITH an approval reference AND TLS
cert/key settings are present. Called before any listener is created (no server exists yet in INC-03)."""
import ipaddress

from hub.security.errors import ExposureNotApproved

LOOPBACK_NAMES = ("localhost",)


def is_loopback(bind):
    host = (bind or "").strip()
    if host.startswith("[") and "]" in host:
        host = host[1:host.index("]")]
    elif host.count(":") == 1:
        host = host.split(":")[0]
    if host.lower() in LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_startup(settings):
    n = settings["network"]
    bind = n["bind"]
    if is_loopback(bind):
        return {"bind": bind, "exposure": "loopback"}
    if not n.get("exposure_approved") or not n.get("exposure_approval_ref"):
        raise ExposureNotApproved({"bind": bind, "reason": "network.exposure_approved + exposure_approval_ref (HAR-05) required"})
    tls = n.get("tls") or {}
    if not tls.get("cert_file") or not tls.get("key_file"):
        raise ExposureNotApproved({"bind": bind, "reason": "TLS settings (network.tls.cert_file/key_file) required"})
    return {"bind": bind, "exposure": "approved", "approval_ref": n["exposure_approval_ref"]}
