from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from apps.projects.models import Project
from apps.accounts.models import User
from apps.tasks.models import Task
from apps.purchases.models import PurchaseSession

@login_required
def reports_dashboard_view(request):
    """
    Reports & Analytics Dashboard (Báo cáo & Thống kê Tiến độ, Phiên mua sắm).
    """
    projects = Project.objects.all().prefetch_related('tasks')
    
    # 1. Project Progress Chart Data
    project_labels = []
    project_progress_data = []
    project_task_counts = []

    for p in projects:
        project_labels.append(p.name)
        project_progress_data.append(p.get_progress_percentage())
        project_task_counts.append(p.tasks.count())

    # 2. User Progress & Contribution Data
    users = User.objects.filter(status=User.Status.ACTIVE)
    user_labels = []
    user_completed_tasks = []
    user_total_tasks = []

    for u in users:
        user_labels.append(u.full_name or u.email)
        assigned_tasks = Task.objects.filter(assignees__user=u)
        user_total_tasks.append(assigned_tasks.count())
        user_completed_tasks.append(assigned_tasks.filter(status=Task.Status.COMPLETED).count())

    # 3. Purchase Session Area Summary
    purchase_sessions = PurchaseSession.objects.all().prefetch_related('session_projects')
    open_sessions_count = purchase_sessions.filter(status=PurchaseSession.Status.OPEN).count()
    closed_sessions_count = purchase_sessions.filter(status=PurchaseSession.Status.CLOSED).count()
    
    total_purchase_cost = sum(s.get_total_amount() for s in purchase_sessions)

    context = {
        # Overview Metrics
        'total_projects': projects.count(),
        'total_tasks': Task.objects.count(),
        'completed_tasks_count': Task.objects.filter(status=Task.Status.COMPLETED).count(),
        
        # Chart JSON Data
        'project_labels': project_labels,
        'project_progress_data': project_progress_data,
        'user_labels': user_labels,
        'user_completed_tasks': user_completed_tasks,
        'user_total_tasks': user_total_tasks,

        # Purchase Sessions Summary
        'purchase_sessions': purchase_sessions,
        'open_sessions_count': open_sessions_count,
        'closed_sessions_count': closed_sessions_count,
        'total_purchase_cost': total_purchase_cost,
    }
    return render(request, 'reports/reports_dashboard.html', context)
