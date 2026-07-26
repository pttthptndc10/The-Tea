from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from apps.tasks.models import Task, TaskAssignee
from apps.projects.models import Project
from apps.tasks.forms import TaskForm
from apps.tasks.services.task_service import TaskService
from apps.projects.services.project_service import ProjectService
from apps.accounts.models import User

@login_required
def task_list_view(request):
    """
    List tasks with status tabs (TODO, IN_PROGRESS, COMPLETED, CANCELLED).
    """
    status_filter = request.GET.get('status', 'ALL')
    project_id = request.GET.get('project')
    query = request.GET.get('q', '').strip()

    tasks = Task.objects.all().select_related('project', 'created_by').order_by('-created_at')

    if project_id:
        tasks = tasks.filter(project_id=project_id)

    if status_filter in [choice[0] for choice in Task.Status.choices]:
        tasks = tasks.filter(status=status_filter)

    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(notes__icontains=query))

    projects = Project.objects.all()

    context = {
        'tasks': tasks,
        'current_status': status_filter,
        'current_project_id': project_id,
        'query': query,
        'projects': projects,
        'status_choices': Task.Status.choices,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail_view(request, task_id):
    """
    Detailed task view.
    """
    task = get_object_or_404(Task.objects.select_related('project', 'created_by'), id=task_id)
    can_edit = TaskService.user_can_edit_task(request.user, task)
    assignees = TaskAssignee.objects.filter(task=task).select_related('user')

    context = {
        'task': task,
        'can_edit': can_edit,
        'assignees': assignees,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_create_view(request):
    """
    Create a new task. Can pre-select project via ?project=<uuid>
    """
    project_id = request.GET.get('project')
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

            # Assign members
            assignees = form.cleaned_data['assignees']
            TaskService.assign_members(task, assignees)

            messages.success(request, f"Tạo nhiệm vụ '{task.title}' thành công!")
            return redirect('projects:detail', project_id=task.project.id)
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập liệu.")
    else:
        form = TaskForm(project=project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Tạo Nhiệm Vụ Mới',
        'is_create': True,
        'project': project
    })


@login_required
def task_edit_view(request, task_id):
    """
    Edit task details.
    """
    task = get_object_or_404(Task, id=task_id)
    if not TaskService.user_can_edit_task(request.user, task):
        messages.error(request, "Bạn không có quyền chỉnh sửa nhiệm vụ này.")
        return redirect('tasks:detail', task_id=task.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=task.project)
        if form.is_valid():
            task = form.save()
            assignees = form.cleaned_data['assignees']
            TaskService.assign_members(task, assignees)

            messages.success(request, f"Cập nhật nhiệm vụ '{task.title}' thành công!")
            return redirect('tasks:detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, project=task.project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'task': task,
        'title': f"Chỉnh Sửa Nhiệm Vụ: {task.title}",
        'is_create': False
    })


@login_required
@require_POST
def task_update_status_view(request, task_id):
    """
    Quick status update for task.
    """
    task = get_object_or_404(Task, id=task_id)
    if not TaskService.user_can_edit_task(request.user, task):
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('tasks:detail', task_id=task.id)

    new_status = request.POST.get('status')
    if new_status in [choice[0] for choice in Task.Status.choices]:
        task.status = new_status
        task.save()
        messages.success(request, f"Đã đổi trạng thái nhiệm vụ '{task.title}' thành {task.get_status_display()}.")

    return redirect(request.META.get('HTTP_REFERER', 'tasks:list'))


@login_required
@require_POST
def task_cancel_view(request, task_id):
    """
    Soft cancel task (moves to "Đã hủy" tab, no DB deletion).
    """
    task = get_object_or_404(Task, id=task_id)
    if not TaskService.user_can_edit_task(request.user, task):
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('tasks:detail', task_id=task.id)

    TaskService.cancel_task(task)
    messages.warning(request, f"Nhiệm vụ '{task.title}' đã chuyển sang danh sách Đã Hủy.")
    return redirect(request.META.get('HTTP_REFERER', 'tasks:list'))


@login_required
@require_POST
def task_delete_view(request, task_id):
    """
    Delete task (with confirmation).
    """
    task = get_object_or_404(Task, id=task_id)
    if not request.user.is_admin() and task.project.manager != request.user:
        messages.error(request, "Chỉ Admin hoặc Manager dự án mới có quyền xóa hẳn task.")
        return redirect('tasks:detail', task_id=task.id)

    project_id = task.project.id
    title = task.title
    task.delete()
    messages.success(request, f"Đã xóa nhiệm vụ '{title}'.")
    return redirect('projects:detail', project_id=project_id)


@login_required
@require_POST
def task_quick_create_view(request, project_id):
    """
    Inline Task Creation directly on the Project Detail checklist card without opening new windows.
    """
    project = get_object_or_404(Project, id=project_id)
    if not ProjectService.user_can_edit(request.user, project):
        messages.error(request, "Dự án hiện ở chế độ View-Only.")
        return redirect('projects:detail', project_id=project.id)

    title = request.POST.get('title', '').strip()
    notes = request.POST.get('notes', '').strip()
    additional_notes = request.POST.get('additional_notes', '').strip()
    start_date = request.POST.get('start_date') or project.start_date
    end_date = request.POST.get('end_date') or project.end_date
    priority = request.POST.get('priority', Task.Priority.MEDIUM)
    assignee_ids = request.POST.getlist('assignees')

    if not title:
        messages.error(request, "Vui lòng nhập tên công việc.")
        return redirect('projects:detail', project_id=project.id)

    task = Task.objects.create(
        project=project,
        title=title,
        notes=notes,
        additional_notes=additional_notes,
        start_date=start_date,
        end_date=end_date,
        priority=priority,
        status=Task.Status.TODO,
        created_by=request.user
    )

    if assignee_ids:
        assignees = User.objects.filter(id__in=assignee_ids)
        TaskService.assign_members(task, assignees)

    messages.success(request, f"Đã tạo công việc '{task.title}' thành công!")
    return redirect('projects:detail', project_id=project.id)

