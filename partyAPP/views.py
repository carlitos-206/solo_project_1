from django.shortcuts import render, HttpResponse, redirect
from .models import Users, Party
from django.contrib import messages
import bcrypt


### Register, Log-in and Log out###########################################

def index(request):
    return render(request, 'index.html')
def register(request):
    if request.method=="POST":
        errors = Users.objects.user_validation(request.POST)
        if len(errors) >0:
            for key, value in errors.items():
                messages.error(request, value)      
            return redirect('/')
        pw_hash=bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user=Users.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            gender=request.POST['gender'],
            username=request.POST['username'],
            password=pw_hash,
        )
        request.session['user_id']=new_user.id
        return redirect('/dashboard')
def terms(request):
    return render(request, 'terms.html')
def sign_in(request):
    if request.method=="GET":
        return redirect('/')
    if request.method=="POST":
        if not Users.objects.login_validation(request.POST['password'], request.POST['username']):
            messages.error(request, "Invalid info")
            return redirect('/')
        this_user = Users.objects.filter(username=request.POST['username'])
        request.session['user_id'] = this_user[0].id
    return redirect("/dashboard")

def logout(request):
    request.session.flush()
    return redirect('/goodbye')
def farewell(request):
    return render(request, 'goodbye.html')

################# END #########################################################


###########File Upload: Pic ##################################################
def my_pic(request):
    if 'user_id' not in request.session:
        return redirect('/')
    return render(request, 'profile_pic.html')
def upload_pic(request):
    this_user=Users.objects.get(id= request.session['user_id'])
    this_user.profile_pic=request.POST['pic']
    this_user.save()
    return redirect('/dashboard')

###################END######################################################

##########DASHBOARD#########################################################


def dashboard(request):
    if 'user_id' in request.session:
        this_user=Users.objects.filter(id=request.session['user_id'])
        newest_party=Party.objects.filter(host=this_user[0])
        context = {
        'user': this_user[0],
        'this_party':Party.objects.filter(host=this_user[0]).order_by('date'),
        'party_added':Party.objects.filter(joined=this_user[0]),
    }
        return render(request, 'dashboard.html', context)
    else:
        return redirect('/')


##########END#########################################################

#######Create Event, Edit Event And Remove Event ###########################

def party_form(request):
    if 'user_id' in request.session:
        return render(request, 'create_party.html')
    else:
        return redirect('/')

def build_party(request):
    errors=Party.objects.basic_validator(request.POST)
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/create_party')
    else:
        Party.objects.create(
            title=request.POST['title'],
            location=request.POST['location'],
            rules=request.POST['rules'],
            date=request.POST['date'],
            time=request.POST['time'],
            items=request.POST['items_needed'],
            host=Users.objects.get(id=request.session['user_id'])
            )
        return redirect('/dashboard')
def remove_party(request, party_id):
    owner= request.session['user_id']
    if Party.objects.filter(id=party_id, host=owner):
        one_Party=Party.objects.get(id=party_id)
        one_Party.delete()
        return redirect('/dashboard')
    else:
        messages.error(request, "Only host can delete thier party")
        return redirect('/dashboard')

def my_parties(request):
    if 'user_id' in request.session:
        this_user=Users.objects.filter(id=request.session['user_id'])
        context={
            'this_party':Party.objects.filter(host=this_user[0]).order_by('-created_at'),
        }
        return render(request, 'my_parties.html', context)
    else:
        return redirect('/dashboard')
def party_info(request, party_id):
    if 'user_id' in request.session:
        this_party=Party.objects.get(id=party_id)
        context={
            'members':this_party.joined.all(),
            'this_party':Party.objects.filter(id=party_id),
        }
        return render(request, 'party_info.html', context)
    else:
        return redirect("/")
def edit__form(request, party_id):
    if 'user_id' in request.session:
        owner=request.session['user_id']
        if Party.objects.filter(id=party_id, host=owner):
            this_party=Party.objects.get(id=party_id)
            context={
                'my_party':this_party
            }
            return render(request, 'editParty.html', context)
        else:
            messages.error(request, "Only host can edit trip")
            return redirect('/dashboard')
    else:
        return redirect("/")
def update(request, party_id):
    errors=Party.objects.basic_validator(request.POST)
    if len(errors)>0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f'/edit/{party_id}')
    else:
        update_party=Party.objects.get(id=party_id)
        update_party.title=request.POST['title']
        update_party.location=request.POST['location']
        update_party.rules=request.POST['rules']
        update_party.date=request.POST['date']
        update_party.time=request.POST['time']
        update_party.items=request.POST['items_needed']
        update_party.save()
        return redirect("/dashboard")
def dropParty(request, party_id):
    this_party=Party.objects.get(id=party_id)
    this_user=Users.objects.get(id=request.session['user_id'])
    this_user.rsvp.remove(this_party)
    return redirect("/dashboard")
#--------------------------------------------------------------------


#-------------------Joining Events---------------------------------
def other_parties(request):
    if 'user_id' in request.session:
        this_user=Users.objects.filter(id=request.session['user_id'])
        context={
            'not_my_parties':Party.objects.exclude(host=request.session['user_id']).exclude(joined=this_user[0]),
        }
        return render(request, 'other_parties.html', context)
    else:
        return redirect("/")
def joinParty(request, party_id):
    this_party=Party.objects.get(id=party_id)
    this_user=Users.objects.get(id=request.session['user_id'])
    if this_user==this_party.host:
        messages.error(request, "You're the host of this party")
        return redirect(f'/party_info/{party_id}')
    if this_user in this_party.joined.all():
        messages.error(request, "You're already part of this party")
        return redirect(f'/party_info/{party_id}')
    else:
        this_user.rsvp.add(this_party)
        return redirect('/dashboard')

#------------User profile----------------------------------
def userProfile(request, party_host_id):
    if 'user_id' in request.session:
        this_user=Users.objects.filter(id=party_host_id)
        context={
            'user_parties':Party.objects.filter(host=this_user[0]).order_by('-created_at')
        }
        return render(request, 'other_user.html', context)
    else:
        return redirect("/")