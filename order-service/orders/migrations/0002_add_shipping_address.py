from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_city',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_country',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_line1',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_line2',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_postal_code',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_state',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
    ]
