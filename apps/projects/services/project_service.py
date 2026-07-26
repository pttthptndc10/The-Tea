from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember

class ProjectService:
    @staticmethod
    def user_can_view(user, project):
        """
        All logged in users can view project details (Outsider view-only).
        """
        return user.is_authenticated

    @staticmethod
    def user_can_edit(user, project):
        """
        Check if user can edit project:
        - Admin can always edit.
        - If project is unmanaged (manager is None), it is VIEW-ONLY for everyone except Admin until a new manager is assigned!
        - Manager or assigned project members can edit if project is managed.
        """
        if not user.is_authenticated:
            return False
        if user.is_admin():
            return True
        if project.is_unmanaged():
            # View-only if manager is deleted/missing
            return False
        if project.manager == user:
            return True
        return ProjectMember.objects.filter(project=project, user=user).exists()

    @staticmethod
    def assign_manager(project, new_manager):
        """
        Assigns or updates project manager.
        """
        project.manager = new_manager
        project.save()
        # Also ensure manager is added to project members
        ProjectMember.objects.get_or_create(project=project, user=new_manager)
        return True
