# Generated by Django 4.2.11 on 2025-06-11 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_carrito_itemcarrito'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallepedido',
            name='camiseta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.camiseta'),
        ),
    ]
