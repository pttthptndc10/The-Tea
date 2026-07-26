from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.notifications.models import Notification

@login_required
def notification_list_view(request):
    """
    List all notifications for current user.
    """
    notifications = Notification.objects.filter(user=request.user)
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_POST
def mark_as_read_view(request, notification_id):
    """
    Mark single notification as read and redirect to its link if available.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect(request.META.get('HTTP_REFERER', 'notifications:list'))


@login_required
@require_POST
def mark_all_read_view(request):
    """
    Mark all unread notifications of the current user as read.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Đã đánh dấu tất cả thông báo là đã đọc.")
    return redirect(request.META.get('HTTP_REFERER', 'notifications:list'))


def notification_context_processor(request):
    """
    Global Context Processor rendering unread notification count & recent dropdown items.
    """
    if request.user.is_authenticated:
        unread_qs = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications_count': unread_qs.count(),
            'header_notifications': unread_qs[:5]
        }
    return {
        'unread_notifications_count': 0,
        'header_notifications': []
    }
