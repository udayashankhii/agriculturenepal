# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Vendor, Product
from .forms import VendorRegistrationForm, ProductForm
from .serializers import ProductSerializer, VendorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

@login_required  # Add a space here
def vendor_dashboard(request):  # And start function definition on new line
    try:
        vendor = Vendor.objects.get(user=request.user)
        products = Product.objects.filter(vendor=vendor)
        return render(request, 'vendor/dashboard.html', {
            'vendor': vendor,
            'products': products
        })
    except Vendor.DoesNotExist:
        return redirect('vendor_registration')

@login_required
def vendor_registration(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            messages.success(request, 'Vendor registration successful!')
            return redirect('vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    return render(request, 'vendor/registration.html', {'form': form})

@login_required
def add_product(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
        if not vendor.is_verified:
            messages.error(request, 'Your shop is not verified yet. Please wait for admin verification.')
            return redirect('vendor_dashboard')
        
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.vendor = vendor
                product.save()
                messages.success(request, 'Product added successfully!')
                return redirect('vendor_dashboard')
        else:
            form = ProductForm()
        return render(request, 'vendor/add_product.html', {'form': form})
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found.')
        return redirect('vendor_registration')

@login_required
def edit_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'vendor/edit_product.html', {'form': form})

@login_required
def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('vendor_dashboard')

@staff_member_required
def verify_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.is_verified = True
    vendor.save()
    return HttpResponseRedirect(reverse('admin:vendor_vendor_changelist'))

class ProductList(APIView):
    """
    Public API endpoint to list all products
    No authentication required
    """
    permission_classes = []  # Empty list means no permissions required

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class VendorDashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Welcome to Vendor Dashboard!"})

class VendorProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            vendor = Vendor.objects.get(user=request.user)
            serializer = VendorSerializer(vendor)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class VendorProductsAPI(APIView):
    """
    API endpoint for vendor-specific products
    GET: Public access to view products by vendor ID
    POST: Only authenticated vendors can add products
    """
    permission_classes_by_method = {
        'GET': [],  # No authentication for GET
        'POST': [IsAuthenticated],  # Authentication required for POST
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_method[self.request.method]]
        except KeyError:
            return []

    def get(self, request):
        try:
            # Get vendor_id from URL parameters
            vendor_id = request.query_params.get('vendor_id')
            
            if not vendor_id:
                return Response(
                    {"error": "Vendor ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if vendor exists
            vendor = get_object_or_404(Vendor, id=vendor_id)
            
            # Get products for specific vendor
            products = Product.objects.filter(vendor=vendor)
            
            if not products.exists():
                return Response(
                    {"message": f"No products found for vendor {vendor.shop_name}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ProductSerializer(products, many=True)
            return Response({
                "vendor": {
                    "id": vendor.id,
                    "shop_name": vendor.shop_name,
                    "is_verified": vendor.is_verified
                },
                "products": serializer.data
            })
            
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        try:
            vendor = Vendor.objects.get(user=request.user)
            data = request.data.copy()
            data['vendor'] = vendor.id
            
            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save(vendor=vendor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class VendorProductDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, vendor):
        try:
            return Product.objects.get(pk=pk, vendor=vendor)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        try:
            vendor = Vendor.objects.get(user=request.user)
            product = self.get_object(pk, vendor)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        try:
            vendor = Vendor.objects.get(user=request.user)
            product = self.get_object(pk, vendor)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        try:
            vendor = Vendor.objects.get(user=request.user)
            product = self.get_object(pk, vendor)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class VendorRegistrationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check if vendor already exists
            if Vendor.objects.filter(user=request.user).exists():
                return Response(
                    {"error": "Vendor profile already exists"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create new vendor
            vendor = Vendor.objects.create(
                user=request.user,
                shop_name=request.data.get('shop_name'),
                description=request.data.get('description'),
                phone_number=request.data.get('phone_number'),
                address=request.data.get('address'),
                pan_number_image=request.FILES.get('pan_number_image')
            )
            
            return Response({
                'message': 'Vendor registration successful! Awaiting verification.',
                'vendor': {
                    'id': vendor.id,
                    'shop_name': vendor.shop_name,
                    'description': vendor.description,
                    'phone_number': vendor.phone_number,
                    'address': vendor.address,
                    'pan_number_image': vendor.pan_number_image.url if vendor.pan_number_image else None,
                    'is_verified': vendor.is_verified
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, vendor):
        try:
            return Product.objects.get(pk=pk, vendor=vendor)
        except Product.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        try:
            vendor = Vendor.objects.get(user=request.user)
            product = self.get_object(pk, vendor)
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Vendor.DoesNotExist:
            return Response(
                {"error": "Vendor profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ProductDetailAPI(APIView):
    permission_classes = []  # Public access

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class VendorVerificationAPI(APIView):
    """
    API endpoint for admin to verify vendors
    Only admin users can access this endpoint
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # List all unverified vendors
        unverified_vendors = Vendor.objects.filter(is_verified=False)
        serializer = VendorSerializer(unverified_vendors, many=True)
        return Response(serializer.data)

    def post(self, request, vendor_id):
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            vendor.is_verified = True
            vendor.save()
            
            return Response({
                'message': f'Vendor {vendor.shop_name} has been verified successfully',
                'vendor': VendorSerializer(vendor).data
            }, status=status.HTTP_200_OK)
            
        except Vendor.DoesNotExist:
            return Response({
                'error': 'Vendor not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get_pending_verifications(self, request):
        # Get count of pending verifications
        pending_count = Vendor.objects.filter(is_verified=False).count()
        return Response({
            'pending_verifications': pending_count
        })

