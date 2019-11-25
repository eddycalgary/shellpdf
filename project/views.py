from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from datetime import datetime
from django.template import RequestContext

import pandas as pd
from django.contrib.auth.decorators import login_required
import tabula


@login_required
def HOME(request):
    if request.method=="GET":
        date = datetime.date(datetime.now())
        current_user = request.user
        return render(request, 'home.html', {"TEST": "User: ", "user1": current_user, "time": date, 'user': ""})

    return render(request, 'login.html')

@login_required
def contact(request):
    if request.method=="POST":

        if int(request.POST.get('test123')) > 0:
            val1 = int(request.POST['test123'])
            res = val1 * 3
            return render(request, 'res.html', {'result': res})
        else:
            return render(request, 'res.html', {'result': "The value is 0"})

    print(request.method)
    return render(request, 'res.html')

# Create your views here.

def upload(request):
    global column
    global list

    list = ['Total Slurry Treatment Volume', 'Total Stage Proppant',
            'Maximum Wellhead Pressure', 'Average Wellhead Pressure',
            'Stage', 'Average Bottomhole Pressure', 'Average Wellhead Rate',
            'Maximum Wellhead Rate', 'Document']

    column = pd.DataFrame(columns=list)

    if request.method=='POST' and request.POST.get('Vendors') != "None":
        file2 = request.POST.get('Vendors')
        print(file2)
        file1 = request.FILES.getlist("document")
        d=0
        for x in file1:
            df1 = tabula.read_pdf(x, lattice=True, pages='all', multiple_tables=True)
            df2 = Vendor_Liberty_doc(df1, d)
            d+=1
        #xw.Book().sheets[0].range('A1').value = df2
        return render(request, 'main.html', {"content": df2.to_html, "SIZE": len(file1)})
    else:
        return render(request, 'main.html', {"content": "No vendor was selected"})


def signup_views(request):
    global list

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'home.html')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_views(request):


    if request.method == "POST":
        date = datetime.date(datetime.now())
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return render(request, 'home.html', {'user': user, "time": date, "message": "; You have sucessfully logged in!!"})

    else:
        date = datetime.date(datetime.now())
        form = AuthenticationForm()

    return render(request, "login.html", {'form': form, "time": date})

def logout_views(request):
    if request.method=="POST":
        logout(request)
        return redirect('login')



def find_tables(doc):
    #df2 = tabula.read_pdf(doc, lattice=True, pages = 'all', multiple_tables=True)
    #for table in

    list = ['Total Slurry Treatment Volume', 'Total Stage Proppant',
            'Maximum Wellhead Pressure', 'Average Wellhead Pressure',
            'Stage', 'Average Bottomhole Pressure', 'Average Wellhead Rate',
            'Maximum Wellhead Rate', 'Document']

    for frame in doc:
        frame = pd.DataFrame(frame)
        if len(frame.index)>30:
            for x in frame.iloc[:,0]:
                if x == 'Stage':
                    table = frame.loc[frame.iloc[:,0].isin(list)]
                    break
                else:
                    continue
        else:
            continue
    return table

def Vendor_Liberty_doc(doc, axis):
    #df = tabula.read_pdf(doc, lattice=True, pages='all', multiple_tables=True)
    ab = axis

    for each_table in doc:
        each_table = pd.DataFrame(each_table)
        if len(each_table.index) > 30:
            for x in each_table.iloc[:,0]:
                if x == 'Stage':
                    table = each_table.loc[each_table.iloc[:,0].isin(list)]
                    axis = table.iloc[0,1]
                    column.loc[ab, 'Stage'] = table.iloc[0, 1]
                    column.loc[ab, 'Total Slurry Treatment Volume'] = table.iloc[1, 2]
                    column.loc[ab, 'Total Stage Proppant'] = table.iloc[2, 2]
                    column.loc[ab, 'Average Wellhead Pressure'] = table.iloc[3, 2]
                    column.loc[ab, 'Maximum Wellhead Pressure'] = table.iloc[4, 2]
                    column.loc[ab, 'Average Bottomhole Pressure'] = table.iloc[5, 2]
                    column.loc[ab, 'Average Wellhead Rate'] = table.iloc[6, 2]
                    column.loc[ab, 'Maximum Wellhead Rate'] = table.iloc[7, 2]
                    column.loc[ab, 'Document'] = "N/A"
                    print(column)
                    print(ab)
                    continue
                else:
                    continue
        else:
            continue
    return column
