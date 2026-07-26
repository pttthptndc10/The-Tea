from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.purchases.models import PurchaseSession, PurchaseSessionProject
from apps.projects.models import Project
from apps.purchases.forms import PurchaseSessionForm
from apps.purchases.services.purchase_service import PurchaseService

@login_required
def session_list_view(request):
    """
    List all Purchase Sessions (Phiên mua sắm).
    """
    status_filter = request.GET.get('status', 'ALL')
    sessions = PurchaseSession.objects.all().prefetch_related('session_projects__project').order_by('-created_at')

    if status_filter in [choice[0] for choice in PurchaseSession.Status.choices]:
        sessions = sessions.filter(status=status_filter)

    form = PurchaseSessionForm()

    context = {
        'sessions': sessions,
        'current_status': status_filter,
        'form': form,
    }
    return render(request, 'purchases/session_list.html', context)


@login_required
def session_detail_view(request, session_id):
    """
    Purchase Session Detail View.
    """
    session = get_object_or_404(PurchaseSession.objects.prefetch_related('session_projects__project'), id=session_id)
    session_projects = session.session_projects.select_related('project').all()
    form = PurchaseSessionForm(instance=session)

    context = {
        'session': session,
        'session_projects': session_projects,
        'total_amount': session.get_total_amount(),
        'form': form,
    }
    return render(request, 'purchases/session_detail.html', context)


@login_required
@require_POST
def session_create_view(request):
    """
    Create a new Purchase Session.
    """
    form = PurchaseSessionForm(request.POST)
    if form.is_valid():
        session = form.save(commit=False)
        session.created_by = request.user
        session.save()

        projects = form.cleaned_data['projects']
        PurchaseService.sync_session_projects(session, projects)

        messages.success(request, f"Tạo phiên mua sắm '{session.name}' thành công!")
        return redirect('purchases:detail', session_id=session.id)
    else:
        messages.error(request, "Vui lòng nhập tên phiên hợp lệ.")
        return redirect('purchases:list')


@login_required
@require_POST
def session_edit_view(request, session_id):
    """
    Edit Purchase Session details and linked projects.
    """
    session = get_object_or_404(PurchaseSession, id=session_id)
    form = PurchaseSessionForm(request.POST, instance=session)

    if form.is_valid():
        session = form.save()
        projects = form.cleaned_data['projects']
        PurchaseService.sync_session_projects(session, projects)

        messages.success(request, f"Cập nhật phiên mua sắm '{session.name}' thành công!")
    else:
        messages.error(request, "Vui lòng nhập thông tin hợp lệ.")

    return redirect('purchases:detail', session_id=session.id)


@login_required
@require_POST
def toggle_session_status_view(request, session_id):
    """
    Toggles status between OPEN and CLOSED (Đóng phiên / Mở lại).
    """
    session = get_object_or_404(PurchaseSession, id=session_id)
    new_status = PurchaseService.toggle_session_status(session)

    if new_status == PurchaseSession.Status.CLOSED:
        messages.warning(request, f"Đã ĐÓNG phiên mua sắm '{session.name}'.")
    else:
        messages.success(request, f"Đã MỞ LẠI phiên mua sắm '{session.name}'.")

    return redirect(request.META.get('HTTP_REFERER', 'purchases:list'))
