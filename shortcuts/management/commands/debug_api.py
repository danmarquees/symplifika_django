from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from django.db import IntegrityError
import json

from shortcuts.models import Category, Shortcut
from shortcuts.serializers import CategorySerializer
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Debug API issues - tests pagination and request handling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-data',
            action='store_true',
            help='Create test data for debugging',
        )
        parser.add_argument(
            '--test-pagination',
            action='store_true',
            help='Test pagination warning issue',
        )
        parser.add_argument(
            '--test-requests',
            action='store_true',
            help='Test bad request issues',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting API Debug Tests'))

        # Create or get test user
        user = self.get_or_create_test_user()

        if options['create_data']:
            self.create_test_data(user)

        if options['test_pagination']:
            self.test_pagination_issue(user)

        if options['test_requests']:
            self.test_request_issues(user)

    def get_or_create_test_user(self):
        """Get or create test user"""
        try:
            user = User.objects.get(username='api_test_user')
            self.stdout.write('📋 Using existing test user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='api_test_user',
                email='test@symplifika.com',
                password='testpass123'
            )
            self.stdout.write(self.style.SUCCESS('✅ Created test user'))

        return user

    def create_test_data(self, user):
        """Create test data to reproduce issues"""
        self.stdout.write('📋 Creating test data...')

        # Create multiple categories to test pagination
        for i in range(15):
            try:
                category = Category.objects.create(
                    user=user,
                    name=f'Test Category {i+1}',
                    description=f'Description for category {i+1}',
                    color=f'#00{i%9}{i%9}ff'
                )

                # Create some shortcuts for each category
                for j in range(3):
                    Shortcut.objects.get_or_create(
                        user=user,
                        trigger=f'//test-cat{i+1}-shortcut{j+1}',
                        defaults={
                            'title': f'Shortcut {j+1} for Category {i+1}',
                            'content': f'Test content for shortcut {j+1}',
                            'category': category,
                            'expansion_type': 'static'
                        }
                    )

            except IntegrityError:
                # Category already exists
                pass

        self.stdout.write(self.style.SUCCESS('✅ Test data created'))

    def test_pagination_issue(self, user):
        """Test the pagination warning issue"""
        self.stdout.write('📋 Testing pagination warning...')

        # Get categories queryset similar to the view
        from django.db.models import Q, Count

        self.stdout.write('Testing direct queryset...')
        queryset = Category.objects.filter(user=user).annotate(
            shortcuts_count=Count('shortcuts', filter=Q(shortcuts__is_active=True))
        )

        self.stdout.write(f'Queryset without explicit ordering: {len(queryset)}')

        # Test with explicit ordering
        queryset_ordered = queryset.order_by('name')
        self.stdout.write(f'Queryset with explicit ordering: {len(queryset_ordered)}')

        # Test pagination
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        paginator.page_size = 5

        # This should trigger the warning if not properly ordered
        try:
            page = paginator.paginate_queryset(queryset, request=None)
            self.stdout.write(self.style.WARNING('⚠️  Unordered queryset pagination completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Pagination error: {e}'))

        # Test with ordered queryset
        try:
            page_ordered = paginator.paginate_queryset(queryset_ordered, request=None)
            self.stdout.write(self.style.SUCCESS('✅ Ordered queryset pagination completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ordered pagination error: {e}'))

    def test_request_issues(self, user):
        """Test bad request issues"""
        self.stdout.write('📋 Testing request issues...')

        # Test serializer validation directly
        self.stdout.write('Testing CategorySerializer validation...')

        # Test valid data
        valid_data = {
            'name': 'Valid Category',
            'description': 'Valid description',
            'color': '#ff5500'
        }

        # Create mock request context
        class MockRequest:
            def __init__(self, user):
                self.user = user

        mock_request = MockRequest(user)
        context = {'request': mock_request}

        serializer = CategorySerializer(data=valid_data, context=context)
        if serializer.is_valid():
            self.stdout.write(self.style.SUCCESS('✅ Valid data passes serializer validation'))
            try:
                category = serializer.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Category created: {category.name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error saving valid category: {e}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Valid data failed validation: {serializer.errors}'))

        # Test invalid data scenarios
        invalid_test_cases = [
            {'name': '', 'description': 'Empty name'},
            {'name': 'A', 'description': 'Too short name'},
            {'name': 'Valid Name', 'color': 'invalid-color'},
            {'description': 'Missing name field'},
            {'name': 'Duplicate Category', 'description': 'Will test duplicate'},
        ]

        for i, test_data in enumerate(invalid_test_cases):
            self.stdout.write(f'\nTesting invalid case {i+1}: {test_data}')

            serializer = CategorySerializer(data=test_data, context=context)
            if not serializer.is_valid():
                self.stdout.write(self.style.WARNING(f'⚠️  Expected validation error: {serializer.errors}'))
            else:
                self.stdout.write(self.style.ERROR(f'❌ Invalid data passed validation unexpectedly'))

        # Test duplicate name
        self.stdout.write('\nTesting duplicate name constraint...')
        duplicate_data = {
            'name': 'Valid Category',  # Same as created above
            'description': 'Duplicate name test',
            'color': '#00ff00'
        }

        serializer = CategorySerializer(data=duplicate_data, context=context)
        if not serializer.is_valid():
            self.stdout.write(self.style.SUCCESS(f'✅ Duplicate name properly rejected: {serializer.errors}'))
        else:
            # Try to save and see if IntegrityError occurs
            try:
                serializer.save()
                self.stdout.write(self.style.ERROR('❌ Duplicate name was allowed'))
            except IntegrityError:
                self.stdout.write(self.style.SUCCESS('✅ IntegrityError caught for duplicate name'))

        self.stdout.write(self.style.SUCCESS('🏁 Debug tests completed'))
