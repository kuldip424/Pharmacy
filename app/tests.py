from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import CategoryModel, SupplierModel, ProductModel, RegistrationModel, OrderModel, orderItemModel
import datetime

class ModelTesting(TestCase):
    def setUp(self):
        # Set up a category
        self.category = CategoryModel.objects.create(name="Medicines")
        
        # Set up a supplier
        self.supplier = SupplierModel.objects.create(
            name="HealthTech Supplies",
            contact_person="John Doe",
            email="johndoe@example.com",
            mobile="1234567890",
            address="123 Health Ave"
        )

        # Mock image
        self.test_image = SimpleUploadedFile(name='test.jpg', content=b'', content_type='image/jpeg')

        # Set up a product
        self.product = ProductModel.objects.create(
            name="Paracetamol",
            image=self.test_image,
            price=15.00,
            buy_price=10.00,
            stock=100,
            description="Pain reliever",
            categories=self.category,
            supplier=self.supplier,
            manufacture_date=datetime.date.today(),
            expiry_date=datetime.date.today() + datetime.timedelta(days=365)
        )

        # Set up a user
        self.user = RegistrationModel.objects.create(
            name="Test User",
            email="test@user.com",
            mobile="0987654321",
            password="testpassword",
            otp="123456"
        )

    def test_category_creation(self):
        """Test if the category was created successfully"""
        self.assertEqual(self.category.name, "Medicines")
        self.assertEqual(str(self.category), "Medicines")

    def test_supplier_creation(self):
        """Test if the supplier was created successfully"""
        self.assertEqual(self.supplier.name, "HealthTech Supplies")
        self.assertEqual(str(self.supplier), "HealthTech Supplies")

    def test_product_creation(self):
        """Test if the product was created successfully"""
        self.assertEqual(self.product.name, "Paracetamol")
        self.assertEqual(self.product.price, 15.00)
        self.assertEqual(str(self.product), "Paracetamol")

    def test_order_creation(self):
        """Test creating an order and an order item"""
        order = OrderModel.objects.create(
            user=self.user,
            total_price=30.00,
            name="Test User",
            mobile="0987654321",
            address="Test Address",
            city="Test City",
            state="Test State",
            zipcode="123456",
            payment_mode="COD"
        )
        order_item = orderItemModel.objects.create(
            order=order,
            product=self.product,
            qty=2,
            price=15.00
        )
        self.assertEqual(order.user.name, "Test User")
        self.assertEqual(order.total_price, 30.00)
        self.assertEqual(order_item.product.name, "Paracetamol")
        self.assertEqual(order_item.qty, 2)

class ViewTesting(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = CategoryModel.objects.create(name="Medicines")
        
        # Mock image
        self.test_image = SimpleUploadedFile(name='test.jpg', content=b'', content_type='image/jpeg')
        
        self.product = ProductModel.objects.create(
            name="Aspirin",
            image=self.test_image,
            price=10.00,
            stock=50,
            description="Fever reducer",
            categories=self.category,
            manufacture_date=datetime.date.today(),
            expiry_date=datetime.date.today() + datetime.timedelta(days=365)
        )
        # Create corresponding detail for the product
        from .models import ProductDetailModel
        ProductDetailModel.objects.create(
            product=self.product,
            moredescription="Detailed info about Aspirin"
        )

    def test_index_view(self):
        """Test if the index page loads successfully"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_product_view(self):
        """Test if the product page loads successfully"""
        response = self.client.get(reverse('product'))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        """Test if the product detail page loads successfully"""
        response = self.client.get(reverse('detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
