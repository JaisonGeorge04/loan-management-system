from django.db import models

class Registration(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=50)
    rights=models.CharField(max_length=40,default="User")
    def __str__(self):
        return self.name

class Manager(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    phone=models.IntegerField()
    branch=models.CharField(max_length=50,null=True)
    password=models.CharField(max_length=50)
    rights=models.CharField(max_length=40,default="Manager")
    def __str__(self):
        return self.name
    
class Branch(models.Model):
    bname=models.CharField(max_length=50)
    location=models.CharField(max_length=100)
    def __str__(self):
        return self.bname

class LoanType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    def __str__(self):
        return self.name

class LoanApplication(models.Model):    
    user = models.CharField(max_length=50)
    loan_type = models.CharField(max_length=50,null=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_tenure = models.IntegerField()  # in months
    documents = models.FileField(upload_to='loan_documents/', blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    date=models.DateField(auto_now_add=True,null=True)
    status = models.CharField(max_length=20, default='Pending')
    is_paid = models.BooleanField(default=False)
    def __str__(self):
        return f"Loan Application #{self.id} - {self.user}"
    def calculate_payment(self):
        """Calculate monthly payment using the EMI formula."""
        principal = self.loan_amount
        rate = self.interest_rate / 12 / 100  # Monthly interest rate
        tenure = self.loan_tenure

        if rate == 0:  # No interest scenario
            return principal / tenure

        emi = principal * rate * ((1 + rate) ** tenure) / (((1 + rate) ** tenure) - 1)
        return round(emi, 2)