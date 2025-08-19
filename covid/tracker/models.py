from django.db import models

class CovidData(models.Model):
    """
    Model representing COVID-19 data for Indian states
    This maps to your existing 'c19' table in MySQL
    """
    state = models.CharField(max_length=100, unique=True, primary_key=True)
    confirmed = models.FloatField(default=0)
    active = models.FloatField(default=0)
    recovered = models.FloatField(default=0)
    deaths = models.FloatField(default=0)
    
    class Meta:
        db_table = 'c19'  # This tells Django to use your existing table
        verbose_name = 'COVID Data'
        verbose_name_plural = 'COVID Data'
        ordering = ['-confirmed']  # Order by confirmed cases (highest first)
    
    def __str__(self):
        return f"{self.state} - Confirmed: {self.confirmed}"
    
    @property
    def recovery_rate(self):
        """Calculate recovery rate percentage"""
        if self.confirmed > 0:
            return round((self.recovered / self.confirmed) * 100, 2)
        return 0
    
    @property
    def death_rate(self):
        """Calculate death rate percentage"""
        if self.confirmed > 0:
            return round((self.deaths / self.confirmed) * 100, 2)
        return 0
    
    @property
    def active_rate(self):
        """Calculate active cases percentage"""
        if self.confirmed > 0:
            return round((self.active / self.confirmed) * 100, 2)
        return 0