# Generated by Django 5.0.1 on 2024-01-21 19:00

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_available', models.IntegerField()),
                ('image', models.ImageField(upload_to='product_images/')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(default='', max_length=255)),
                ('email', models.EmailField(default='', max_length=254)),
                ('address', models.TextField(default='')),
                ('city', models.CharField(default='', max_length=255)),
                ('pin_code', models.CharField(default='', max_length=6)),
                ('state', models.CharField(default='', max_length=255)),
                ('mobile', models.CharField(default='', max_length=15)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('payment_method', models.CharField(choices=[('cash_on_delivery', 'Cash on Delivery'), ('debit_credit_card', 'Debit/Credit Card'), ('upi', 'UPI')], default='', max_length=20)),
                ('order_id', models.CharField(default='', max_length=8, unique=True)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='processing', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('cash_on_delivery', 'Cash on Delivery'), ('debit_credit_card', 'Debit/Credit Card'), ('upi', 'UPI')], default='', max_length=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='store.OrderItem', to='store.product'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(through='store.CartItem', to='store.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.productcategory'),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('comment', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
