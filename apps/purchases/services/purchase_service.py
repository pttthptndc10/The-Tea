from apps.purchases.models import PurchaseSession, PurchaseSessionProject

class PurchaseService:
    @staticmethod
    def toggle_session_status(session):
        """
        Toggles session status between OPEN and CLOSED (Mo lai / Dong phien).
        """
        if session.status == PurchaseSession.Status.OPEN:
            session.status = PurchaseSession.Status.CLOSED
        else:
            session.status = PurchaseSession.Status.OPEN
        session.save()
        return session.status

    @staticmethod
    def sync_session_projects(session, project_list):
        """
        Links projects to a purchase session and computes snapshot amounts.
        """
        PurchaseSessionProject.objects.filter(session=session).exclude(project__in=project_list).delete()
        for p in project_list:
            psp, created = PurchaseSessionProject.objects.get_or_create(session=session, project=p)
            psp.save() # Auto recalculates snapshot amount
