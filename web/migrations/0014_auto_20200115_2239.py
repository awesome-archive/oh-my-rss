# Generated by Django 2.2.7 on 2020-01-15 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_auto_20200108_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='src_url',
            field=models.CharField(max_length=1024, unique=True, verbose_name='原始链接'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=200, verbose_name='标题'),
        ),
        migrations.AlterField(
            model_name='site',
            name='creator',
            field=models.CharField(blank=True, choices=[('system', '系统录入'), ('user', '用户提交'), ('wemp', '微信公众号')], db_index=True, default='system', max_length=20, null=True, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='site',
            name='link',
            field=models.CharField(max_length=1024, verbose_name='主页'),
        ),
        migrations.AlterField(
            model_name='site',
            name='rss',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='RSS地址'),
        ),
    ]
