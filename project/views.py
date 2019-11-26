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
        if request.POST.get('Vendors')=='Liberty':
            file2 = request.POST.get('Vendors')
            file1 = request.FILES.getlist("document")
            d=0
            for x in file1:
                df1 = tabula.read_pdf(x, lattice=True, pages='all', multiple_tables=True)
                df2 = Vendor_Liberty_doc(df1, d)
                d+=1
                #xw.Book().sheets[0].range('A1').value = df2
            return render(request, 'main.html', {"content": df2.to_html, "SIZE": len(file1), 'name': x.name})
        elif request.POST.get('Vendors')=='WPX':
            file1 = request.FILES.getlist("document")
            d=0
            for x in file1:
                df1 = tabula.read_pdf(x, lattice=True, pages='all', multiple_tables=True)
                print(x.name)
                df2 = Vendor_WPX(df1, d, str(x.name))
                d+=1
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

def Vendor_WPX(Folder, index, name):
    #t=0
    print(name)

    #df1=tabula.read_pdf(doc, lattice=True, pages = '1-3', multiple_tables=True)
    for d in Folder:
        if len(d) !=0 and len(d.index) > 6 and len(d.columns) > 6:
            index_value = First_ValueIndex(d)  # run function to find index value
            tableType = Table_type(d)  # find if first or second table
            if tableType == 'First':
                FirstTable(d, index_value, index, name)
                continue
            elif tableType == 'Second':
                SecondTable(d, index_value, index, name)
                break
        else:
            continue
    return column.sort_values(by=['Stage'])

def First_ValueIndex(df):
    Index = df.iloc[:,0].first_valid_index()
    return Index

def FirstTable(df, index,j, title):
    docName = name(title)
    table1 = df.iloc[index:,0:]
    table2 = table1.dropna(thresh=len(table1)-2, axis=1)
    table2 = table2.iloc[:,[2,9]].astype(float)
    total_slurry = round(table2.iloc[:,0].sum())
    total_propant= round(table2.iloc[:,1].sum())
    column.loc[j, 'Total Slurry Treatment Volume']= total_slurry
    column.loc[j, 'Stage']= docName
    column.loc[j, 'Total Stage Proppant']= total_propant

def SecondTable(df, index, j, name):
    table2 = df.iloc[index:,0:]
    table3 = table2.dropna(thresh=len(table2)-2, axis=1)
    table3 = table3.reset_index(drop=True)
    cf = table3.loc[table3.iloc[:,1]=='PAD'].index[0]
    table3 = table3.iloc[:,[2,3,4,5]].astype(float)
    Max_wellheadPressure= table3.iloc[:,3].max()
    Ave_wellheadPressure= table3.iloc[cf+1:,2].mean()
    Max_treatingRate    = table3.iloc[:,1].max()
    Ave_treatingRate    = table3.iloc[cf+1:,0].mean()
    column.loc[j, 'Maximum Wellhead Pressure']= Max_wellheadPressure
    column.loc[j, 'Average Wellhead Pressure']= Ave_wellheadPressure
    column.loc[j, 'Average Wellhead Rate']    = Ave_treatingRate
    column.loc[j, 'Maximum Wellhead Rate']    = Max_treatingRate
    column.loc[j, 'Document']= name

def Table_type(df):
    x1 = df.iloc[0:3,0:4]
    for each_row in df.iterrows():
        if 'Stage Pressu' in str(each_row):
            table = 'Second'
            return table
        elif 'As Measur' in str(each_row):
            table = 'First'
            return table

def name(doc):
    test1 = doc.find('Stage')
    test2 = doc.find('.p')
    result = doc[test2-2:test2]
    return result