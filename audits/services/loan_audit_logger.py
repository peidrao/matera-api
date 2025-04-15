from audits.models.loan_audit_model import LoanAuditLog


def log_loan_action(*, loan, action, user=None, ip_address=None, metadata=None):
    LoanAuditLog.objects.create(
        loan=loan,
        action=action,
        performed_by=user,
        ip_address=ip_address,
        metadata=metadata or {},
    )
