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
    path('rapports/', views.rapports, name='rapports'), 
    path('edit_simulation/<int:id_simulation>/', views.edit_simulation, name='edit_simulation'),
    path('detail_simulation/<int:simulation_id>/', views.detail_simulation, name='detail_simulation'),

]