from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dealer_portal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=13, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(13)])),
                ('area', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='dealer_portal.Area')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('brand', models.CharField(max_length=50)),  
                ('model', models.CharField(max_length=50)),  
                ('weight', models.CharField(max_length=50)),  
                ('category', models.CharField(max_length=10, choices=[('İHA0', 'İHA0'), ('İHA1', 'İHA1'), ('İHA2', 'İHA2'), ('İHA3', 'İHA3')])),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rent', models.CharField(max_length=8)),
                ('days', models.CharField(max_length=3)),
                ('dealer', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='dealer_portal.Dealer')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='dealer_portal.Vehicles')),
            ],
        ),
    ]
