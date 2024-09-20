from django.db import models

class ContentRequest(models.Model):
    CATEGORY_CHOICES = [
        ('project', 'Project'),
        ('meetup', 'Meetup'),
        ('knowledge', 'Knowledge'),
        ('achievement', 'Achievement'),
        ('research', 'Research'),
        ('bug', 'Bug'),
    ]

    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('reddit', 'Reddit'),
        ('blog', 'Blog'),
        ('product_hunt', 'Product Hunt'),
    ]

    WRITING_STYLE_CHOICES = [
        ('formal', 'Formal'),
        ('casual', 'Casual'),
        ('technical', 'Technical'),
        ('storytelling', 'Storytelling'),
    ]
    platforms = models.CharField(max_length=100, default='linkedin') 
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
   # Store as comma-separated values
    word_count = models.IntegerField(default=100)
    writing_style = models.CharField(max_length=20, choices=WRITING_STYLE_CHOICES, default='casual')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.created_at}"