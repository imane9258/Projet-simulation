from django.urls import path
from . import views

urlpatterns = [
    path('', views.connexion, name='connexion'),
    path('accueil/', views.accueil, name='accueil'),
    path('creer_simulation/', views.creer_simulation, name='creer_simulation'),
    path('resultat_simulation/<str:ids_simulation>/', views.resultat_simulation, name='resultat_simulation'),
    path('download_pdf/<str:ids_simulation>/', views.download_pdf, name='download_pdf'),
    path('download_excel/<str:ids_simulation>/', views.download_excel, name='download_excel'),
    path('liste_simulations/', views.liste_simulations, name='liste_simulations'),
    path('rapport_simulation/', views.rapport_simulation, name='rapport_simulation'), 
    path('edit_simulation/<int:id_simulation>/', views.edit_simulation, name='edit_simulation'),
    path('detail_simulation/<int:id_simulation>/', views.detail_simulation, name='detail_simulation'),
    path('download_detail_pdf/<int:id_simulation>/', views.download_detail_pdf, name='download_detail_pdf'),
    path('download_detail_excel/<int:id_simulation>/', views.download_detail_excel, name='download_detail_excel'),
]
