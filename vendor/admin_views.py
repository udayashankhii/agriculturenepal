from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Vendor

@staff_member_required  # Only admin/staff can access
def verify_vendor(request, vendor_id):
    # Find vendor or return 404 if not found
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Set verification status to True
    vendor.is_verified = True
    vendor.save()
    
    # Redirect back to admin vendor list
    return HttpResponseRedirect(reverse('admin:vendor_vendor_changelist'))