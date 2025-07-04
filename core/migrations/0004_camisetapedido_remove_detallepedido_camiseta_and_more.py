# Generated by Django 4.2.11 on 2025-06-11 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_detallepedido_camiseta'),
    ]

    operations = [
        migrations.CreateModel(
            name='CamisetaPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('talla', models.CharField(max_length=5)),
                ('color', models.CharField(max_length=20)),
                ('calidad', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='detallepedido',
            name='camiseta',
        ),
        migrations.AddField(
            model_name='detallepedido',
            name='camiseta_pedido',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.camisetapedido'),
        ),
    ]
