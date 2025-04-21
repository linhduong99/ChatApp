from django.db import migrations
from django.contrib.auth.hashers import make_password

def add_sample_data(apps, schema_editor):
    User = apps.get_model('chat', 'User')
    Group = apps.get_model('auth', 'Group')
    Room = apps.get_model('chat', 'Room')

    # Create groups
    admin_group, _ = Group.objects.get_or_create(name='admin')
    user_group, _ = Group.objects.get_or_create(name='user')

    # Create admin user
    admin_user = User.objects.create(
        username='admin',
        password=make_password('admin123'),
        name='Administrator',
        is_staff=True,
        is_superuser=True
    )
    admin_user.groups.add(admin_group)

    # Create sample users
    users = [
        {
            'username': 'user1',
            'password': 'user123',
            'name': 'User One',
            'bio': 'First sample user'
        },
        {
            'username': 'user2',
            'password': 'user123',
            'name': 'User Two',
            'bio': 'Second sample user'
        },
        {
            'username': 'user3',
            'password': 'user123',
            'name': 'User Three',
            'bio': 'Third sample user'
        }
    ]

    for user_data in users:
        user = User.objects.create(
            username=user_data['username'],
            password=make_password(user_data['password']),
            name=user_data['name'],
            bio=user_data['bio']
        )
        user.groups.add(user_group)

    # Create sample rooms
    rooms = [
        {
            'name': 'General',
            'password': None,
            'created_by': admin_user
        },
        {
            'name': 'Private Room',
            'password': 'private123',
            'created_by': User.objects.get(username='user1')
        }
    ]

    for room_data in rooms:
        Room.objects.create(**room_data)

def remove_sample_data(apps, schema_editor):
    User = apps.get_model('chat', 'User')
    Group = apps.get_model('auth', 'Group')
    Room = apps.get_model('chat', 'Room')

    # Remove all sample data
    User.objects.all().delete()
    Group.objects.all().delete()
    Room.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_sample_data, remove_sample_data),
    ] 