from django.conf import settings
import django.core.validators
from django.db import migrations, models
from django.db.models import CASCADE, PROTECT, SET_NULL
from dealer_portal.models import Area, Dealer
from customer_portal.models import Vehicles
from django.contrib.auth.decorators import login_required


class Migration(migrations.Migration):

    initial = True

    dependencies = [ 
        ('dealer_portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('postcode', models.CharField(max_length=6, unique=True, validators=[django.core.validators.MinLengthValidator(6), django.core.validators.MaxLengthValidator(6)])),
                ('city', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Dealer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=13, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(13)])),
                ('area', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='dealer_portal.Area')),
                
                
            ],
        ),
        migrations.CreateModel(
            name='Vehicles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iha_name', models.CharField(max_length=100)),
                ('brand', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('weight', models.CharField(max_length=10)),
                ('category', models.CharField(max_length=100)),
                ('is_available', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=200)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dealer_portal.Area')),
                ('dealer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dealer_portal.Dealer')),
            ],
        ),
    ]
