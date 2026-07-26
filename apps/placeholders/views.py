from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def video_meeting_placeholder(request):
    return render(request, 'placeholders/placeholder.html', {
        'title': 'Video Meeting',
        'icon': 'fa-video',
        'description': 'Tính năng Họp Trực tuyến & Gọi Video cho nhóm dự án sẽ được tích hợp ở phiên bản tiếp theo.'
    })

@login_required
def inventory_placeholder(request):
    return render(request, 'placeholders/placeholder.html', {
        'title': 'Inventory (Quản Lý Kho Linh Kiện)',
        'icon': 'fa-boxes-stacked',
        'description': 'Tính năng Quản lý Tồn kho, Nhập/Xuất kho linh kiện tập trung đang được nâng cấp.'
    })

@login_required
def pdf_export_placeholder(request):
    return render(request, 'placeholders/placeholder.html', {
        'title': 'PDF Export (Xuất Báo Cáo PDF)',
        'icon': 'fa-file-pdf',
        'description': 'Tính năng Xuất Báo cáo Dự án & Phiên Mua sắm dạng tài liệu PDF chuẩn định dạng.'
    })

@login_required
def file_storage_placeholder(request):
    return render(request, 'placeholders/placeholder.html', {
        'title': 'File Storage (Lưu Trữ Tệp Dự Án)',
        'icon': 'fa-cloud-arrow-up',
        'description': 'Tính năng Lưu trữ & Chia sẻ tài liệu, minh chứng dự án đám mây.'
    })
