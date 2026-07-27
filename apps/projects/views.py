from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum
from apps.projects.models import Project, ProjectMember
from apps.projects.forms import ProjectForm, AssignManagerForm
from apps.projects.services.project_service import ProjectService
from apps.accounts.models import User

@login_required
def project_list_view(request):
    """
    List all projects with status tabs and search.
    """
    status_filter = request.GET.get('status', 'ALL')
    query = request.GET.get('q', '').strip()

    projects = Project.objects.all().select_related('manager', 'created_by').prefetch_related('tasks').order_by('-created_at')

    # Status tab filtering
    if status_filter == 'UNMANAGED':
        projects = projects.filter(Q(manager__isnull=True) | Q(manager__status=User.Status.LOCKED))
    elif status_filter in [choice[0] for choice in Project.Status.choices]:
        projects = projects.filter(status=status_filter)

    # Keyword Search
    if query:
        projects = projects.filter(Q(name__icontains=query) | Q(description__icontains=query))

    context = {
        'projects': projects,
        'current_status': status_filter,
        'query': query,
        'status_choices': Project.Status.choices,
        'assign_form': AssignManagerForm(),
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_detail_view(request, project_id):
    """
    View details of a specific project with tabbed layout.
    """
    project = get_object_or_404(Project.objects.select_related('manager', 'created_by'), id=project_id)
    can_edit = ProjectService.user_can_edit(request.user, project)
    members = User.objects.filter(project_memberships__project=project)

    # Fetch tasks
    tasks = project.tasks.select_related('created_by').prefetch_related('assignees__user').all()
    todo_tasks = tasks.filter(status='TODO')
    in_progress_tasks = tasks.filter(status='IN_PROGRESS')
    completed_tasks = tasks.filter(status='COMPLETED')
    cancelled_tasks = tasks.filter(status='CANCELLED')

    # Fetch components
    components = project.components.all().order_by('-created_at')
    total_components_cost = components.aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'project': project,
        'can_edit': can_edit,
        'members': members,
        'tasks': tasks,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'cancelled_tasks': cancelled_tasks,
        'components': components,
        'total_components_cost': total_components_cost,
        'assign_form': AssignManagerForm(),
        'active_tab': request.GET.get('tab', 'checklist'),
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create_view(request):
    """
    Create a new project (Admin Only requirement).
    """
    if not request.user.is_admin():
        messages.error(request, "Chỉ Admin mới có quyền tạo Dự án mới.")
        return redirect('projects:list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            # Save project members
            members = form.cleaned_data['members']
            for m in members:
                ProjectMember.objects.get_or_create(project=project, user=m)

            # Ensure manager is also added as member if selected
            if project.manager:
                ProjectMember.objects.get_or_create(project=project, user=project.manager)

            messages.success(request, f"Tạo dự án '{project.name}' thành công!")
            return redirect('projects:detail', project_id=project.id)
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập liệu.")
    else:
        form = ProjectForm()

    return render(request, 'projects/project_form.html', {
        'form': form,
        'title': 'Tạo Dự Án Mới',
        'is_create': True
    })


@login_required
def project_edit_view(request, project_id):
    """
    Edit an existing project.
    """
    project = get_object_or_404(Project, id=project_id)

    if not ProjectService.user_can_edit(request.user, project):
        messages.error(request, "Dự án này hiện ở chế độ Chỉ Xem (View Only) do chưa có người quản lý hoặc bạn không có quyền sửa.")
        return redirect('projects:detail', project_id=project.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()

            # Sync members
            new_members = set(form.cleaned_data['members'])
            if project.manager:
                new_members.add(project.manager)

            # Delete removed members
            ProjectMember.objects.filter(project=project).exclude(user__in=new_members).delete()

            # Add new members
            for m in new_members:
                ProjectMember.objects.get_or_create(project=project, user=m)

            messages.success(request, f"Cập nhật dự án '{project.name}' thành công!")
            return redirect('projects:detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {
        'form': form,
        'project': project,
        'title': f"Chỉnh Sửa Dự Án: {project.name}",
        'is_create': False
    })


@login_required
@require_POST
def project_delete_view(request, project_id):
    """
    Delete a project (Admin Only, with confirmation).
    """
    if not request.user.is_admin():
        messages.error(request, "Chỉ Admin mới có quyền xóa dự án.")
        return redirect('projects:list')

    project = get_object_or_404(Project, id=project_id)
    name = project.name
    project.delete()
    messages.success(request, f"Đã xóa dự án '{name}' khỏi hệ thống.")
    return redirect('projects:list')


@login_required
@require_POST
def assign_manager_view(request, project_id):
    """
    Admin action to assign a new manager to a project.
    """
    if not request.user.is_admin():
        messages.error(request, "Chỉ Admin mới có quyền chỉ định người quản lý.")
        return redirect('projects:detail', project_id=project_id)

    project = get_object_or_404(Project, id=project_id)
    form = AssignManagerForm(request.POST)

    if form.is_valid():
        new_manager = form.cleaned_data['manager']
        ProjectService.assign_manager(project, new_manager)
        messages.success(request, f"Đã chỉ định {new_manager.full_name or new_manager.email} làm Người quản lý dự án '{project.name}'.")
    else:
        messages.error(request, "Vui lòng chọn người quản lý hợp lệ.")

    return redirect('projects:detail', project_id=project_id)
