from django.shortcuts import render,redirect
from .models import *
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import date

def index(request):
    return render(request,"index.html")

def signIn(request):
    if request.method=="POST":
        email=request.POST.get('email')
        pword=request.POST.get('pword')
        log=Registration.objects.filter(email=email,password=pword)
        mng=Manager.objects.filter(email=email,password=pword)
        rights=''
        for i in log:
            rights=i.rights
        for j in mng:
            rights=j.rights
        if rights=="User":
            request.session['email']=email
            return redirect("/user/")
        elif rights=="Manager":
            request.session['email']=email
            return redirect('/manager/')
        elif rights=='Admin':
            request.session['name']=i.name
            return redirect("/adminp/")
        else:
            print("Invalid user")
    return render(request,"sign.html")

def signUp(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        pword=request.POST.get('pword')
        reg=Registration(name=name,email=email,password=pword)
        reg.save()
    return render(request,"sign.html")

def user(request):
    return render(request,"user/user.html")

def admin(request):
    return render(request,"admin/admin.html")

def manager(request):
    return render(request,"manager/manager.html")

def add_manager(request):
    br=Branch.objects.all()
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        branch=request.POST.get('branch')
        pword=request.POST.get('password')
        reg=Manager(name=name,email=email,branch=branch,phone=phone,password=pword)
        reg.save()
    return render(request,"admin/add_manager.html",{'br':br})

def manage_branches(request):
    br=Branch.objects.all()
    if request.method=="POST":
        bname=request.POST.get('bname')
        loc=request.POST.get('loc')
        branch=Branch(bname=bname,location=loc)
        branch.save()
    return render(request,"admin/manage_branches.html",{'br':br})

def delete_branch(request,id):
    Branch.objects.filter(id=id).delete()
    return redirect('/manage_branches/')

def manage_managers(request):
    br=Manager.objects.all()
    return render(request,"admin/manage_managers.html",{'br':br})

def edit_manager(request,id):
    br=Manager.objects.filter(id=id)
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        branch=request.POST.get('branch')
        pword=request.POST.get('password')
        Manager.objects.filter(id=id).update(name=name,email=email,branch=branch,phone=phone,password=pword)
    return render(request,"admin/edit_manager.html",{'br':br})

def delete_manager(request,id):
    Manager.objects.filter(id=id).delete()
    return redirect('/manage_managers/')

def manage_loans(request):
    br=LoanType.objects.all()
    if request.method=="POST":
        name=request.POST.get('name')
        desc=request.POST.get('desc')
        branch=LoanType(name=name,description=desc)
        branch.save()
    return render(request,"admin/manage_loans.html",{'br':br})

def delete_loan(request,id):
    LoanType.objects.filter(id=id).delete()
    return redirect('/manage_loans/')

def application(request):
    loan=LoanType.objects.all()
    user=request.session['email']
    if request.method=="POST":
        loan_type=request.POST.get('loan_type')
        loan_amount=request.POST.get('loan_amount')
        interest_rate=request.POST.get('interest_rate')
        loan_tenure=request.POST.get('loan_tenure')
        documents=request.FILES['documents']
        remarks=request.POST.get('remarks')
        ln=LoanApplication(user=user,loan_type=loan_type,loan_amount=loan_amount,interest_rate=interest_rate,loan_tenure=loan_tenure,documents=documents,remarks=remarks)
        ln.save()
    return render(request,'user/application.html',{'loan':loan})

def emi_calculator(request):
    if request.method == 'POST':
        principal = float(request.POST.get('principal'))
        annual_rate = float(request.POST.get('annual_rate'))
        tenure_years = int(request.POST.get('tenure_years'))

        # Calculate EMI
        monthly_rate = annual_rate / (12 * 100)
        tenure_months = tenure_years * 12
        emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / ((1 + monthly_rate) ** tenure_months - 1)
        emi = round(emi, 2)

        return render(request, 'user/emi_result.html', {'emi': emi})
    
    return render(request, 'user/emi_form.html')

def view_loan_requests(request):
    loan=LoanApplication.objects.filter(status='Pending')
    return render(request,'manager/view_loan_applications.html',{'loan':loan})

def approve_loan(request,id):
    LoanApplication.objects.filter(id=id).update(status='Approved')
    return redirect('/view_loan_applications/')

def reject_loan(request,id):
    LoanApplication.objects.filter(id=id).update(status='Rejected')
    return redirect('/view_loan_applications/')

def view_loan_applications(request):
    loan=LoanApplication.objects.all()
    return render(request,'manager/loan_applications.html',{'loan':loan})

def view_loans(request):
    loan=LoanApplication.objects.all()
    return render(request,'admin/view_loans.html',{'loan':loan})

def my_application(request):
    email=request.session['email']
    loan=LoanApplication.objects.filter(user=email)
    return render(request,'user/my_application.html',{'loan':loan})

def payments_by_date(request, id):
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)  
    print(first_day_of_month)
    payments = LoanApplication.objects.filter(
        id=id,
        date=first_day_of_month,  
        status='Approved',
        is_paid=False
    )
    return render(request, 'user/payments_by_date.html', {'payments': payments})

def enable_payment(request, loan_id):
    loan = LoanApplication.objects.get(id=loan_id)
    emi = loan.calculate_payment()  

    return JsonResponse({
        'success': True,
        'loan_id': loan.id,
        'loan_amount': float(loan.loan_amount),
        'emi': emi,
        'applicant_name': loan.user
    })


def mark_as_paid(request, application_date):
    """Mark all applications for a specific date as paid."""
    LoanApplication.objects.filter(date=application_date, is_paid=True).update(status='Paid')
    return redirect('/my_application/')


def loan_payments(request):
    today = now().date()

    applications = LoanApplication.objects.filter(date=today)

    return render(request, 'user/loan_payments.html', {'applications': applications})

def loan_payment_details(request, pk):
    """Fetch EMI and payment details for a specific loan."""
    application = get_object_or_404(LoanApplication, pk=pk)
    emi = application.calculate_emi()

    return JsonResponse({
        'applicant_name': application.user,
        'emi': emi,
        'loan_amount': application.loan_amount,
        'loan_type': application.loan_type,
        'status': application.status,
    })

def process_payment(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        payment_amount = request.POST.get('payment_amount')

        loan = LoanApplication.objects.get(id=loan_id)

        loan.is_paid = True
        loan.save()

        return redirect('payments_by_date')
from django.http import HttpResponse

def payment_form(request, id):
    loan = get_object_or_404(LoanApplication, id=id, status='Approved', is_paid=False)

    if request.method == 'POST':
        loan.is_paid = True
        loan.save()
        return redirect('payment_success')

    return render(request, 'user/payment_form.html', {'loan': loan})

def payment_success(request):
    return render(request, 'user/payment_success.html')