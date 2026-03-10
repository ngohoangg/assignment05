from django.db import migrations, models
import django.db.models.deletion


def move_name_to_fullname(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    FullName = apps.get_model('customers', 'FullName')

    for customer in Customer.objects.all().iterator():
        full_name_obj = FullName.objects.create(full_name=customer.name)
        customer.fullname_id = full_name_obj.id
        customer.save(update_fields=['fullname'])


def rollback_fullname_to_name(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')

    for customer in Customer.objects.select_related('fullname').all().iterator():
        if customer.fullname_id:
            customer.name = customer.fullname.full_name
            customer.save(update_fields=['name'])


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(blank=True, default='', max_length=255)),
                ('line2', models.CharField(blank=True, default='', max_length=255)),
                ('city', models.CharField(blank=True, default='', max_length=120)),
                ('state', models.CharField(blank=True, default='', max_length=120)),
                ('postal_code', models.CharField(blank=True, default='', max_length=30)),
                ('country', models.CharField(blank=True, default='', max_length=120)),
            ],
            options={
                'db_table': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='FullName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'fullnames',
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer', to='customers.address'),
        ),
        migrations.AddField(
            model_name='customer',
            name='fullname',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer', to='customers.fullname'),
        ),
        migrations.RunPython(move_name_to_fullname, rollback_fullname_to_name),
        migrations.RemoveField(
            model_name='customer',
            name='name',
        ),
    ]
