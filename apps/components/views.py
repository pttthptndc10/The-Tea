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
    Create a component record for a project (supports both AJAX JSON and Form POST).
    """
    project = get_object_or_404(Project, id=project_id)
    if not ProjectService.user_can_edit(request.user, project):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Dự án hiện ở chế độ View-Only.'}, status=403)
        messages.error(request, "Dự án hiện ở chế độ View-Only.")
        return redirect(f"/projects/{project.id}/?tab=materials")

    name = request.POST.get('name') or ''
    quantity = int(request.POST.get('quantity') or 1)
    unit_price = float(request.POST.get('unit_price') or 0)
    shop = request.POST.get('shop', '')
    notes = request.POST.get('notes', '')

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            name = data.get('name') or ''
            quantity = int(data.get('quantity') or 1)
            unit_price = float(data.get('unit_price') or 0)
            shop = data.get('shop', '')
            notes = data.get('notes', '')
        except Exception:
            pass

    if not name:
        name = "Linh kiện mới"

    component = Component.objects.create(
        project=project,
        name=name,
        quantity=quantity,
        unit_price=unit_price,
        shop=shop,
        notes=notes
    )

    project_total = Component.objects.filter(project=project).aggregate(Sum('total_price'))['total_price__sum'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'id': str(component.id),
            'name': component.name,
            'quantity': component.quantity,
            'unit_price': float(component.unit_price),
            'total_price': float(component.total_price),
            'shop': component.shop,
            'notes': component.notes,
            'project_total': float(project_total)
        })

    messages.success(request, f"Đã thêm linh kiện '{component.name}'.")
    return redirect(f"/projects/{project.id}/?tab=materials")


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
    Delete component record (supports AJAX JSON and Form POST).
    """
    component = get_object_or_404(Component, id=component_id)
    project = component.project
    name = component.name

    if not ProjectService.user_can_edit(request.user, component.project):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Dự án hiện ở chế độ View-Only.'}, status=403)
        messages.error(request, "Dự án hiện ở chế độ View-Only.")
        return redirect(f"/projects/{project.id}/?tab=materials")

    component.delete()
    project_total = Component.objects.filter(project=project).aggregate(Sum('total_price'))['total_price__sum'] or 0

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"Đã xóa linh kiện '{name}'.",
            'project_total': float(project_total)
        })

    messages.success(request, f"Đã xóa linh kiện '{name}'.")
    return redirect(f"/projects/{project.id}/?tab=materials")


@login_required
def component_export_excel_view(request, project_id):
    """
    Export project components to Excel file (.xlsx).
    """
    project = get_object_or_404(Project, id=project_id)
    return ComponentService.export_project_components_to_excel(project)
