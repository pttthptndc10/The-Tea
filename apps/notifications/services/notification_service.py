from apps.notifications.models import Notification

class NotificationService:
    @staticmethod
    def send_notification(user, title, message, link=""):
        """
        Sends a new in-app notification to a user.
        """
        if not user:
            return None
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            link=link
        )

    @staticmethod
    def notify_task_assignment(task, assignees):
        """
        Notifies assigned users about a task assignment.
        """
        for u in assignees:
            NotificationService.send_notification(
                user=u,
                title=f"Nhiệm vụ mới: {task.title}",
                message=f"Bạn đã được giao nhiệm vụ '{task.title}' thuộc dự án {task.project.name}.",
                link=f"/projects/{task.project.id}/?tab=checklist"
            )

    @staticmethod
    def notify_manager_assignment(project, manager):
        """
        Notifies a user when assigned as Manager of a project.
        """
        if manager:
            NotificationService.send_notification(
                user=manager,
                title=f"Quản lý dự án: {project.name}",
                message=f"Bạn vừa được chỉ định làm Người quản lý (Manager) cho dự án '{project.name}'.",
                link=f"/projects/{project.id}/"
            )
