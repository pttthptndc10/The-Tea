from apps.tasks.models import Task, TaskAssignee
from apps.projects.services.project_service import ProjectService

class TaskService:
    @staticmethod
    def user_can_edit_task(user, task):
        """
        Permission check:
        - Admin can always edit.
        - Project Manager can edit.
        - Assigned users can edit status & notes if project is managed.
        """
        if not user.is_authenticated:
            return False
        if user.is_admin():
            return True
        if task.project.is_unmanaged():
            # View only if project manager is deleted/missing
            return False
        if task.project.manager == user:
            return True
        return TaskAssignee.objects.filter(task=task, user=user).exists()

    @staticmethod
    def assign_members(task, user_list):
        """
        Assigns multiple members to a task and triggers in-app notifications.
        """
        from apps.notifications.services.notification_service import NotificationService
        TaskAssignee.objects.filter(task=task).exclude(user__in=user_list).delete()
        newly_assigned = []
        for u in user_list:
            created = TaskAssignee.objects.get_or_create(task=task, user=u)[1]
            if created:
                newly_assigned.append(u)
        
        if newly_assigned:
            NotificationService.notify_task_assignment(task, newly_assigned)

    @staticmethod
    def cancel_task(task):
        """
        Cancels task instead of deleting (Soft cancellation requirement).
        """
        task.status = Task.Status.CANCELLED
        task.save()
        return True
