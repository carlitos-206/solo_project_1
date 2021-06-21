from django.urls import path
from . import views

urlpatterns=[
#----------home---------------------------------
    path('', views.index),
    path('new_user', views.register),
    path('terms', views.terms),
    path('sign_in', views.sign_in),
    path('dashboard', views.dashboard),
    path('logout', views.logout),
    path('goodbye', views.farewell),
#----------end--------------------------------


#---------Event Building ----------------------
    path('profile_pic', views.my_pic),
    path('my_parties', views.my_parties),
    path('create_party', views.party_form),
    path('el_party', views.build_party),
    path("delete/<int:party_id>", views.remove_party),
    path("party_info/<int:party_id>", views.party_info),
    path("edit/<int:party_id>", views.edit__form),
    path("update/<int:party_id>", views.update),
#-------------------------------------------------------

#----------Joining Events ----------------------------
    path("party_info/<int:party_id>", views.party_info),
    path('other_parties', views.other_parties),
    path('join/<int:party_id>', views.joinParty),
    path('drop_party/<int:party_id>', views.dropParty),
#-----------------------------------------------------------

#---------Users min profile--------------------------------
    path('user_profile/<int:party_host_id>', views.userProfile),
#--------------------------------------------------------------
]
