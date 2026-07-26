import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Sum
from apps.components.models import Component
from apps.projects.models import Project
from apps.projects.services.project_service import ProjectService
from apps.components.forms import ComponentForm
from apps.components.services.component_service import ComponentService

@login_required
def component_list_view(request):
    """
    Component List Page.
    """
    project_id = request.GET.get('project')
    projects = Project.objects.all()

    if project_id:
        selected_project = get_object_or_404(Project, id=project_id)
        components = Component.objects.filter(project=selected_project).order_by('-created_at')
    else:
        selected_project = projects.first()
        components = Component.objects.filter(project=selected_project).order_by('-created_at') if selected_project else Component.objects.none()

    total_cost = components.aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'projects': projects,
        'selected_project': selected_project,
        'components': components,
        'total_cost': total_cost,
        'form': ComponentForm()
    }
    return render(request, 'components/component_list.html', context)


@login_required
@require_POST
def component_create_view(request, project_id):
    """
    Create a component record for a project.
    """
    project = get_object_or_404(Project, id=project_id)
    if not ProjectService.user_can_edit(request.user, project):
        messages.error(request, "Dự án hiện ở chế độ View-Only.")
        return redirect('projects:detail', project_id=project.id)

    form = ComponentForm(request.POST)
    if form.is_valid():
        component = form.save(commit=False)
        component.project = project
        component.save()
        messages.success(request, f"Đã thêm linh kiện '{component.name}'.")
    else:
        messages.error(request, "Vui lòng nhập thông tin linh kiện hợp lệ.")

    redirect_url = request.META.get('HTTP_REFERER') or f"/projects/{project.id}/?tab=materials"
    return redirect(redirect_url)


@login_required
@require_POST
def component_auto_save_api(request):
    """
    Debounced AJAX Auto-Save API endpoint (~1s auto save requirement).
    """
    try:
        data = json.loads(request.body)
        component_id = data.get('id')
        component = get_object_or_404(Component, id=component_id)

        if not ProjectService.user_can_edit(request.user, component.project):
            return JsonResponse({'status': 'error', 'message': 'Không có quyền chỉnh sửa.'}, status=403)

        if 'name' in data:
            component.name = data['name'].strip()
        if 'quantity' in data:
            component.quantity = max(1, int(data['quantity']))
        if 'unit_price' in data:
            component.unit_price = max(0, float(data['unit_price']))
        if 'shop' in data:
            component.shop = data['shop'].strip()
        if 'notes' in data:
            component.notes = data['notes'].strip()

        component.save() # Auto calculates total_price

        # Calculate project total sum
        project_total = Component.objects.filter(project=component.project).aggregate(Sum('total_price'))['total_price__sum'] or 0

        return JsonResponse({
            'status': 'success',
            'message': 'Đã tự động lưu',
            'total_price': float(component.total_price),
            'project_total': float(project_total)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def component_delete_view(request, component_id):
    """
    Delete component record.
    """
    component = get_object_or_404(Component, id=component_id)
    project_id = component.project.id
    name = component.name

    if not ProjectService.user_can_edit(request.user, component.project):
        messages.error(request, "Dự án hiện ở chế độ View-Only.")
        return redirect('projects:detail', project_id=project_id)

    component.delete()
    messages.success(request, f"Đã xóa linh kiện '{name}'.")
    redirect_url = request.META.get('HTTP_REFERER') or f"/projects/{project_id}/?tab=materials"
    return redirect(redirect_url)


@login_required
def component_export_excel_view(request, project_id):
    """
    Export project components to Excel file (.xlsx).
    """
    project = get_object_or_404(Project, id=project_id)
    return ComponentService.export_project_components_to_excel(project)
