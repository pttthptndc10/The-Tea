from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    Dashboard main overview view.
    """
    context = {
        'total_members': 0,
        'total_projects': 0,
        'in_progress_projects': 0,
        'completed_projects': 0,
        'overdue_projects': 0,
        'cancelled_projects': 0,
        'total_tasks': 0,
    }
    return render(request, 'dashboard/index.html', context)
