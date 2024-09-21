class ContentRequest:
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

    def __init__(self, category, description, platforms, word_count, writing_style):
        self.category = category
        self.description = description
        self.platforms = platforms
        self.word_count = word_count
        self.writing_style = writing_style

    def __str__(self):
        return f"{self.category} - {self.platforms}"