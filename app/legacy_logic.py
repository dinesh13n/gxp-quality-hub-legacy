# Historically grown decision logic used by both API and month-end reports.
def priority(status,severity,amount):
    if status=='CLOSED': return 'archive'
    if severity=='CRITICAL' or amount > 50000: return 'urgent'
    if severity=='HIGH' or status=='ESCALATED': return 'review'
    return 'queue'
def manual_review_required(status,severity):
    return severity in ('HIGH','CRITICAL') or status in ('ESCALATED','REOPENED')
