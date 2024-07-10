from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Simulation

# Create your views here.


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accueil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'connexion.html')


from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import now
from datetime import date
import json
from .models import Simulation
from decimal import Decimal

def get_week_number(date):
    return date.strftime("%U")

def get_week_start_date(week_number, year):
    return date.fromisocalendar(year, week_number, 1)

def accueil(request):
    total_simulations = Simulation.objects.count()
    total_investi = Simulation.objects.aggregate(Sum('total_prix_revient'))['total_prix_revient__sum']
    benefice = Simulation.objects.aggregate(Sum('marge_montant'))['marge_montant__sum']
    dernieres_simulations = Simulation.objects.order_by('-date_creation')[:5]

    # Calcul des bénéfices hebdomadaires
    current_year = now().year
    weekly_benefits = {}
    simulations = Simulation.objects.all()

    for simulation in simulations:
        week = get_week_number(simulation.date_creation)
        year = simulation.date_creation.year
        if year == current_year:
            key = f"{year}-W{week}"
            if key not in weekly_benefits:
                weekly_benefits[key] = Decimal(0)
            weekly_benefits[key] += simulation.marge_montant

    # Préparer les données pour le graphique
    sorted_weeks = sorted(weekly_benefits.keys())
    dates_benefice = [get_week_start_date(int(week.split('-W')[1]), int(week.split('-W')[0])).strftime("%Y-%m-%d") for week in sorted_weeks]
    data_benefice = [float(weekly_benefits[week]) for week in sorted_weeks]  # Convert Decimal to float

    context = {
        'total_simulations': total_simulations,
        'total_investi': total_investi,
        'benefice': benefice,
        'dernieres_simulations': dernieres_simulations,
        'dates_benefice': json.dumps(dates_benefice),
        'data_benefice': json.dumps(data_benefice)
    }
    return render(request, 'accueil.html', context)






@login_required
def liste_simulations(request):
    # Retrieve all simulations
    simulations = Simulation.objects.all()

    # Group simulations by title
    grouped_simulations = {}
    for simulation in simulations:
        if simulation.titre not in grouped_simulations:
            grouped_simulations[simulation.titre] = {
                'id_simulation': simulation.id_simulation,
                'total_prix_avec_isb': 0,
                'lines': []
            }
        grouped_simulations[simulation.titre]['total_prix_avec_isb'] += simulation.prix_vente_total_ht_avec_isb
        grouped_simulations[simulation.titre]['lines'].append(simulation)

    context = {
        'grouped_simulations': grouped_simulations
    }

    return render(request, 'liste_simulations.html', context)

@login_required
def rapports(request):
    return render(request, 'rapports.html')




from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Simulation

@login_required
@csrf_protect
def creer_simulation(request):
    if request.method == 'POST':
        titre = request.POST.get('titre')
        simulations_ids = []
        total_ht_devis = Decimal('0')
        total_ttc_devis = Decimal('0')
        marge_montant_total = Decimal('0')
        total_prix_revient = Decimal('0')
        total_isb = Decimal('0')
        total_tva = Decimal('0')

        data = request.POST.copy()
        del data['csrfmiddlewaretoken']

         

        for key, value in data.items():
            if key.startswith('designation') and value:
                index = key.replace('designation', '')
                try:
                    quantite = int(data[f'quantite{index}'])
                    prix_unitaire = Decimal(data[f'prix_unitaire{index}'])
                    frais_transit = Decimal(data[f'frais_transit{index}'])
                    frais_douane = Decimal(data[f'frais_douane{index}'])
                    marge_percentage = Decimal(data[f'marge_percentage{index}'])
                    pourcentage_banque = Decimal(data[f'pourcentage_banque{index}'])
                except (KeyError, ValueError):
                    return HttpResponse("Erreur de saisie : Veuillez vérifier que tous les champs sont remplis correctement.", status=400)

                # Calculs pour chaque ligne de simulation
                prix_total_achat = (quantite * prix_unitaire).quantize(Decimal('0.01'))
                pourcentage_banque_montant = ((prix_total_achat * pourcentage_banque) / Decimal('100.00')).quantize(Decimal('0.01'))
                prix_de_revient_total = (prix_total_achat + frais_transit + frais_douane + pourcentage_banque_montant).quantize(Decimal('0.01'))
                marge_montant = ((prix_de_revient_total * marge_percentage) / Decimal('100.00')).quantize(Decimal('0.01'))
                prix_vente_total_ht_sans_isb = (prix_de_revient_total + marge_montant).quantize(Decimal('0.01'))
    
                prix_vente_total_ht_avec_isb = ((prix_vente_total_ht_sans_isb) / Decimal('0.98')).quantize(Decimal('0.01'))
                isb_montant = (prix_vente_total_ht_avec_isb * Decimal('0.02')).quantize(Decimal('0.01'))
                prix_vente_total_ht = ((prix_vente_total_ht_avec_isb) / quantite).quantize(Decimal('0.01'))
              

                # Cumul des totaux pour toutes les lignes de simulation
                marge_montant_total += marge_montant
                total_prix_revient += prix_de_revient_total
                total_isb += isb_montant
                total_ht_devis += prix_vente_total_ht_avec_isb
                total_tva = (prix_vente_total_ht_avec_isb * Decimal('0.19')).quantize(Decimal('0.01'))
                total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))
  # Calcul du TTC et TVA basé sur le total HT
                
               
                # Création de l'instance Simulation
                simulation = Simulation(
                    titre=titre,
                    designation=value,
                    quantite=quantite,
                    prix=prix_unitaire,
                    prix_total_achat=prix_total_achat,
                    montant_transit=frais_transit,
                    montant_douane=frais_douane,
                    pourcentage_banque=pourcentage_banque,
                    pourcentage_banque_montant=pourcentage_banque_montant,
                    prix_de_revient_total=prix_de_revient_total,
                    marge_pourcentage=marge_percentage,
                    marge_montant=marge_montant,
                    isb=isb_montant,
                    prix_vente_total_ht_sans_isb=prix_vente_total_ht_sans_isb,
                    prix_vente_total_ht_avec_isb=prix_vente_total_ht_avec_isb,
                    prix_vente_total_ht=prix_vente_total_ht,
                    total_ht_devis=total_ht_devis,
                    total_ttc_devis=total_ttc_devis,
                    total_tva=total_tva,
                    marge_montant_total=marge_montant_total,
                    total_prix_revient=total_prix_revient,
                    total_isb=total_isb

                )
                simulation.save()
                simulations_ids.append(str(simulation.id_simulation))

        # Redirection vers la liste des simulations après sauvegarde
        ids_simulation = ','.join(simulations_ids)
        return redirect('resultat_simulation', ids_simulation=ids_simulation)

    return render(request, 'creer_simulation.html')

@login_required
def resultat_simulation(request, ids_simulation):
    ids = ids_simulation.split(',')
    simulations = Simulation.objects.filter(id_simulation__in=ids)

    total_ht_devis = (sum(simulation.prix_vente_total_ht_avec_isb for simulation in simulations)).quantize(Decimal('0.01'))
    marge_montant_total = (sum(simulation.marge_montant for simulation in simulations)).quantize(Decimal('0.01'))
    total_prix_revient =(sum(simulation.prix_de_revient_total for simulation in simulations)).quantize(Decimal('0.01'))
    total_isb = (sum(simulation.isb for simulation in simulations)).quantize(Decimal('0.01'))
    
    # Calculating total_tva based on total_ht_devis
    total_tva = (total_ht_devis * Decimal('0.19')).quantize(Decimal('0.01'))
    # Calculating total_ttc_devis based on total_ht_devis and total_tva
    total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))

    context = {
        'simulations': simulations,
        'total_ht_devis': total_ht_devis,
        'marge_montant_total': marge_montant_total,
        'total_prix_revient': total_prix_revient,
        'total_isb': total_isb,
        'total_tva': total_tva,
        'total_ttc_devis': total_ttc_devis,
        'simulation_titre': simulations[0].titre if simulations else 'Aucune simulation disponible',
        'ids_simulation': ids_simulation,  # Add this line to include ids_simulation in the context
    }
    return render(request, 'resultat_simulation.html', context)


# views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import A3
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from .models import Simulation
from django.contrib.auth.decorators import login_required
from decimal import Decimal

@login_required
def download_pdf(request, ids_simulation):
    ids = ids_simulation.split(',')
    simulations = Simulation.objects.filter(id_simulation__in=ids)

    total_ht_devis = (sum(simulation.prix_vente_total_ht_avec_isb for simulation in simulations)).quantize(Decimal('0.01'))
    marge_montant_total = (sum(simulation.marge_montant for simulation in simulations)).quantize(Decimal('0.01'))
    total_prix_revient = (sum(simulation.prix_de_revient_total for simulation in simulations)).quantize(Decimal('0.01'))
    total_isb = (sum(simulation.isb for simulation in simulations)).quantize(Decimal('0.01'))
    total_tva = (sum(simulation.prix_vente_total_ht_avec_isb * Decimal('0.19') for simulation in simulations)).quantize(Decimal('0.01'))
    total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resultat_simulation.pdf"'

    p = canvas.Canvas(response, pagesize=A3)
    width, height = A3

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(20 * mm, height - 30 * mm, "Résultats de la Simulation")
# Subtitle
    p.setFont("Helvetica-Bold", 14)
    titre_simulation = simulations[0].titre if simulations else 'Aucune simulation disponible'
    p.drawString(20 * mm, height - 40 * mm, f"Client: {titre_simulation}")


    y_position = height - 50 * mm

    # Simulation Data
    for simulation in simulations:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(30 * mm, y_position, f"Désignation: {simulation.designation}")
        y_position -= 10 * mm

        p.setFont("Helvetica", 10)
        p.drawString(20 * mm, y_position, f"Prix d'Achat Unitaire: {simulation.prix}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Quantité: {simulation.quantite}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix Total Achat: {simulation.prix_total_achat} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Frais Transit: {simulation.montant_transit} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Frais Douane: {simulation.montant_douane} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Pourcentage Banque: {simulation.pourcentage_banque}%")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Montant Banque: {simulation.pourcentage_banque_montant} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Marge Pourcentage: {simulation.marge_pourcentage}%")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Montant Marge: {simulation.marge_montant} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix Vente Unitaire: {simulation.prix_vente_total_ht} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix de Revient: {simulation.prix_vente_total_ht_sans_isb} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"ISB: {simulation.isb} FCFA")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Total HT avec ISB: {simulation.prix_vente_total_ht_avec_isb} FCFA")
        y_position -= 10 * mm

    # Totals
    y_position -= 10 * mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(20 * mm, y_position, "Totaux")
    y_position -= 10 * mm

    p.setFont("Helvetica", 10)
    p.drawString(20 * mm, y_position, f"Marge Montant Total: {marge_montant_total} FCFA")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total Prix Revient: {total_prix_revient} FCFA")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"ISB: {total_isb} FCFA")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total HT du Devis: {total_ht_devis} FCFA")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"TVA: {total_tva} FCFA")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total TTC du Devis: {total_ttc_devis} FCFA")

    p.showPage()
    p.save()

    return response


# views.py
import openpyxl
from django.http import HttpResponse
from .models import Simulation
from django.contrib.auth.decorators import login_required
from decimal import Decimal

@login_required
def download_excel(request, ids_simulation):
    ids = ids_simulation.split(',')
    simulations = Simulation.objects.filter(id_simulation__in=ids)

    total_ht_devis = sum(simulation.prix_vente_total_ht_avec_isb for simulation in simulations)
    marge_montant_total = sum(simulation.marge_montant for simulation in simulations)
    total_prix_revient = sum(simulation.prix_de_revient_total for simulation in simulations)
    total_isb = sum(simulation.isb for simulation in simulations)
    total_tva = sum(simulation.prix_vente_total_ht_avec_isb * Decimal('0.19') for simulation in simulations)
    total_ttc_devis = total_ht_devis + total_tva

    # Create a workbook and select the active worksheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Résultats de la Simulation"

    # Add headers
    headers = [
        "Désignation", "Prix d'Achat Unitaire", "Quantité", "Prix Total Achat",
        "Frais Transit", "Frais Douane", "Pourcentage Banque","Montant Banque", "Marge Pourcentage",
        "Montant Marge", "Prix Vente Unitaire", "Prix de Revient", "ISB", 
        "Total HT avec ISB"
    ]
    ws.append(headers)

    # Add data
    for simulation in simulations:
        row = [
            simulation.designation, simulation.prix, simulation.quantite, 
            simulation.prix_total_achat, simulation.montant_transit, 
            simulation.montant_douane, simulation.pourcentage_banque,simulation.pourcentage_banque_montant,
            simulation.marge_pourcentage, simulation.marge_montant, 
            simulation.prix_vente_total_ht, simulation.prix_vente_total_ht_sans_isb, 
            simulation.isb, simulation.prix_vente_total_ht_avec_isb
        ]
        ws.append(row)

    # Add totals
    ws.append([])
    ws.append(["", "", "", "", "", "", "", "", "Marge Montant Total:", marge_montant_total])
    ws.append(["", "", "", "", "", "", "", "", "Total Prix Revient:", total_prix_revient])
    ws.append(["", "", "", "", "", "", "", "", "ISB:", total_isb])
    ws.append(["", "", "", "", "", "", "", "", "Total HT du Devis:", total_ht_devis])
    ws.append(["", "", "", "", "", "", "", "", "TVA:", total_tva])
    ws.append(["", "", "", "", "", "", "", "", "Total TTC du Devis:", total_ttc_devis])

    # Prepare response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=resultat_simulation.xlsx'

    # Save the workbook to the response
    wb.save(response)

    return response



# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Simulation
from .forms import SimulationForm
from .utils import recalculer_simulation



# views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import Simulation

def detail_simulation(request, id_simulation):
    simulation = get_object_or_404(Simulation, id_simulation=id_simulation)
    simulations_grouped_by_title = Simulation.objects.filter(titre=simulation.titre)

    # Calcul des totaux pour les simulations avec le même titre
    marge_montant_total = simulations_grouped_by_title.aggregate(Sum('marge_montant'))['marge_montant__sum']
    total_prix_revient = simulations_grouped_by_title.aggregate(Sum('prix_de_revient_total'))['prix_de_revient_total__sum']
    total_isb = simulations_grouped_by_title.aggregate(Sum('isb'))['isb__sum']
    total_ht_devis = simulations_grouped_by_title.aggregate(Sum('prix_vente_total_ht_avec_isb'))['prix_vente_total_ht_avec_isb__sum']
    total_tva = (total_ht_devis * Decimal('0.19')).quantize(Decimal('0.01'))
    total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))

    context = {
        'simulation': simulation,
        'simulations_grouped_by_title': simulations_grouped_by_title,
        'id_simulation': id_simulation,
        'marge_montant_total': marge_montant_total,
        'total_prix_revient': total_prix_revient,
        'total_isb': total_isb,
        'total_ht_devis': total_ht_devis,
        'total_tva': total_tva,
        'total_ttc_devis': total_ttc_devis,
    }
    return render(request, 'detail_simulation.html', context)


from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from .models import Simulation

def edit_simulation(request, id_simulation):
    simulation = get_object_or_404(Simulation, id_simulation=id_simulation)
    simulations_grouped_by_title = Simulation.objects.filter(titre=simulation.titre)

    if request.method == 'POST':
        titre = request.POST.get('titre')

        try:
            for line in simulations_grouped_by_title:
                designation = request.POST.get(f'designation_{line.id_simulation}')
                quantite = request.POST.get(f'quantite_{line.id_simulation}')
                prix_unitaire = request.POST.get(f'prix_unitaire_{line.id_simulation}')
                frais_transit = request.POST.get(f'frais_transit_{line.id_simulation}')
                frais_douane = request.POST.get(f'frais_douane_{line.id_simulation}')
                marge_percentage = request.POST.get(f'marge_percentage_{line.id_simulation}')
                pourcentage_banque = request.POST.get(f'pourcentage_banque_{line.id_simulation}')

                # Remplacer les virgules par des points pour les valeurs numériques
                quantite = quantite.replace(',', '.')
                prix_unitaire = prix_unitaire.replace(',', '.')
                frais_transit = frais_transit.replace(',', '.')
                frais_douane = frais_douane.replace(',', '.')
                marge_percentage = marge_percentage.replace(',', '.')
                pourcentage_banque = pourcentage_banque.replace(',', '.')

                # Convertir les valeurs récupérées en Decimal
                try:
                    quantite = Decimal(quantite)
                    prix_unitaire = Decimal(prix_unitaire)
                    frais_transit = Decimal(frais_transit)
                    frais_douane = Decimal(frais_douane)
                    marge_percentage = Decimal(marge_percentage)
                    pourcentage_banque = Decimal(pourcentage_banque)
                except InvalidOperation:
                    return render(request, 'edit_simulation.html', {
                        'simulation': simulation,
                        'simulations_grouped_by_title': simulations_grouped_by_title,
                        'error': 'Invalid input. Please enter valid numeric values.'
                    })

                # Vérifier les valeurs pour éviter la division par zéro
                if quantite == 0 or prix_unitaire == 0:
                    return render(request, 'edit_simulation.html', {
                        'simulation': simulation,
                        'simulations_grouped_by_title': simulations_grouped_by_title,
                        'error': 'Quantité et Prix Unitaire doivent être supérieurs à zéro.'
                    })

                prix_total_achat = (quantite * prix_unitaire).quantize(Decimal('0.01'))
                pourcentage_banque_montant = ((prix_total_achat * pourcentage_banque) / Decimal('100.00')).quantize(Decimal('0.01'))
                prix_de_revient_total = (prix_total_achat + frais_transit + frais_douane + pourcentage_banque_montant).quantize(Decimal('0.01'))
                marge_montant = ((prix_de_revient_total * marge_percentage) / Decimal('100.00')).quantize(Decimal('0.01'))
                prix_vente_total_ht_sans_isb = (prix_de_revient_total + marge_montant).quantize(Decimal('0.01'))
                prix_vente_total_ht_avec_isb = (prix_vente_total_ht_sans_isb / Decimal('0.98')).quantize(Decimal('0.01'))
                isb_montant = (prix_vente_total_ht_avec_isb * Decimal('0.02')).quantize(Decimal('0.01'))
                prix_vente_total_ht = (prix_vente_total_ht_avec_isb / quantite).quantize(Decimal('0.01'))

                # Mettre à jour l'objet simulation avec les nouvelles valeurs
                line.titre = titre
                line.designation = designation
                line.quantite = quantite
                line.prix = prix_unitaire
                line.montant_transit = frais_transit
                line.montant_douane = frais_douane
                line.marge_pourcentage = marge_percentage
                line.pourcentage_banque = pourcentage_banque
                line.prix_total_achat = prix_total_achat
                line.pourcentage_banque_montant = pourcentage_banque_montant
                line.prix_de_revient_total = prix_de_revient_total
                line.marge_montant = marge_montant
                line.prix_vente_total_ht_sans_isb = prix_vente_total_ht_sans_isb
                line.prix_vente_total_ht_avec_isb = prix_vente_total_ht_avec_isb
                line.isb_montant = isb_montant
                line.prix_vente_total_ht = prix_vente_total_ht

                line.save()

        except InvalidOperation as e:
            return render(request, 'edit_simulation.html', {
                'simulation': simulation,
                'simulations_grouped_by_title': simulations_grouped_by_title,
                'error': f'An error occurred during calculations: {e}'
            })

        return redirect('detail_simulation', id_simulation=simulation.id_simulation)

    return render(request, 'edit_simulation.html', {'simulation': simulation, 'simulations_grouped_by_title': simulations_grouped_by_title})




from django.shortcuts import render
from .models import Simulation
from django.db.models import Sum, Avg, Count

def rapports(request):
    simulations = Simulation.objects.all()

    # Calculer les statistiques
    total_simulations = simulations.count()
    total_investi = simulations.aggregate(total=Sum('total_prix_revient'))['total']
    benefice = simulations.aggregate(total=Sum('marge_montant'))['total']
    cout_moyen = simulations.aggregate(avg=Avg('total_prix_revient'))['avg']
    marge_moyenne = simulations.aggregate(avg=Avg('marge_montant'))['avg']

    context = {
        'simulations': simulations,
        'total_simulations': total_simulations,
        'total_investi': total_investi,
        'benefice': benefice,
        'cout_moyen': cout_moyen,
        'marge_moyenne': marge_moyenne,
    }
    
    return render(request, 'rapports.html', context)

import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .models import Simulation
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Sum
from reportlab.lib import colors

@login_required
def download_detail_pdf(request, id_simulation):
    try:
        simulation = Simulation.objects.get(id_simulation=id_simulation)
    except Simulation.DoesNotExist:
        return HttpResponse("Simulation not found", status=404)

    # Fetch all simulation lines for the given title
    simulations_grouped_by_title = Simulation.objects.filter(titre=simulation.titre)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="detail_simulation_{id_simulation}.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 18)
    title_text = f"Détails de la Simulation {id_simulation}"
    title_width = p.stringWidth(title_text, "Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 30 * mm, title_text)

    # Client Title
    p.setFont("Helvetica", 12)
    client_title_text = f"Client: {simulation.titre}"
    client_title_width = p.stringWidth(client_title_text, "Helvetica", 12)
    p.drawString((width - client_title_width) / 2, height - 40 * mm, client_title_text)

    y_position = height - 50 * mm

    # Create Table Data
    data = []
    table_list = []  # To store each Table object
    styles = getSampleStyleSheet()
    for line in simulations_grouped_by_title:
        data.append([
            ("Désignation", Paragraph(line.designation, styles['BodyText'])),
            ("Prix d'Achat Unitaire", f"{line.prix} FCFA"),
            ("Quantité", line.quantite),
            ("Prix Total Achat", f"{line.prix_total_achat} FCFA"),
            ("Frais Transit", f"{line.montant_transit} FCFA"),
            ("Frais Douane", f"{line.montant_douane} FCFA"),
            ("Pourcentage Banque", f"{line.pourcentage_banque}%"),
            ("Montant Banque", f"{line.pourcentage_banque_montant} FCFA"),
            ("Marge Pourcentage", f"{line.marge_pourcentage}%"),
            ("Montant Marge", f"{line.marge_montant} FCFA"),
            ("Prix Vente Unitaire", f"{line.prix_vente_total_ht} FCFA"),
            ("Prix de Revient", f"{line.prix_de_revient_total} FCFA"),
            ("ISB", f"{line.isb} FCFA"),
            ("Total HT avec ISB", f"{line.prix_vente_total_ht_avec_isb} FCFA")
        ])

    # Calculate available space and adjust the table position
    table_start_y = y_position

    for item in data:
        table = Table(item, colWidths=[100, 200])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))

        table.wrapOn(p, width, height)
        if table_start_y - table._height < 20 * mm:  # Check if there's enough space on the page
            p.showPage()  # Start a new page
            table_start_y = height - 20 * mm  # Reset the table start position

        table.drawOn(p, 10 * mm, table_start_y - table._height)  # Adjust as needed
        table_start_y -= table._height + 5 * mm  # Adjust as needed

    # Totals Section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(10 * mm, table_start_y - 5 * mm, "Totaux")

    # Calcul des totaux pour les simulations avec le même titre
    marge_montant_total = simulations_grouped_by_title.aggregate(Sum('marge_montant'))['marge_montant__sum']
    total_prix_revient = simulations_grouped_by_title.aggregate(Sum('prix_de_revient_total'))['prix_de_revient_total__sum']
    total_isb = simulations_grouped_by_title.aggregate(Sum('isb'))['isb__sum']
    total_ht_devis = simulations_grouped_by_title.aggregate(Sum('prix_vente_total_ht_avec_isb'))['prix_vente_total_ht_avec_isb__sum']
    total_tva = (total_ht_devis * Decimal('0.19')).quantize(Decimal('0.01'))
    total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))

    # Draw Totals
    totals = [
        ("Marge Montant Total", f"{marge_montant_total} FCFA"),
        ("Total Prix Revient", f"{total_prix_revient} FCFA"),
        ("ISB", f"{total_isb} FCFA"),
        ("Total HT du Devis", f"{total_ht_devis} FCFA"),
        ("TVA", f"{total_tva} FCFA"),
        ("Total TTC du Devis", f"{total_ttc_devis} FCFA")
    ]

    table_start_y -= 2 * mm

    for item in totals:
        p.drawString(40 * mm, table_start_y, f"{item[0]}: {item[1]}")
        table_start_y -= 5 * mm

    p.showPage()
    p.save()

    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()

    return response




import io
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from django.contrib.auth.decorators import login_required
from .models import Simulation
from decimal import Decimal
from django.db.models import Sum

@login_required
def download_detail_excel(request, id_simulation):
    try:
        simulation = Simulation.objects.get(id_simulation=id_simulation)
    except Simulation.DoesNotExist:
        return HttpResponse("Simulation not found", status=404)

    # Fetch all simulation lines for the given title
    simulations_grouped_by_title = Simulation.objects.filter(titre=simulation.titre)

    # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active

    # Header 
    headers = [
        "Désignation", "Quantité", "Prix d'Achat Unitaire", "Prix Total Achat",
        "Frais Transit", "Frais Douane", "Pourcentage Banque", "Montant Banque",
        "Marge Pourcentage", "Montant Marge", "Prix Vente Unitaire", "Prix de Revient",
        "ISB", "Total HT avec ISB"
    ]
    header_font = Font(bold=True, color="000000")
    header_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = border
        ws.column_dimensions[cell.column_letter].width = 20

    # Function to replace dots with spaces
    def format_number(value):
        if value is not None:
            return str(int(value)).replace('.', ' ')
        return value

    # Add data
    row_num = 2
    for line in simulations_grouped_by_title:
        row = [
            line.designation,
            line.quantite,
            format_number(line.prix),
           
            format_number(line.prix_total_achat),
            format_number(line.montant_transit),
            format_number(line.montant_douane),
            format_number(line.pourcentage_banque) + "%",
            format_number(line.pourcentage_banque_montant),
            format_number(line.marge_pourcentage) + "%",
            format_number(line.marge_montant),
            format_number(line.prix_vente_total_ht),
            format_number(line.prix_de_revient_total),
            format_number(line.isb),
            format_number(line.prix_vente_total_ht_avec_isb)
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.alignment = Alignment(horizontal="center")
            cell.border = border

        row_num += 1

    # Totals
    total_font = Font(size=12, bold=True)
    total_fill = PatternFill(start_color="B0F2B6", end_color="B0F2B6", fill_type="solid")
    # Calcul des totaux pour les simulations avec le même titre
    marge_montant_total = simulations_grouped_by_title.aggregate(Sum('marge_montant'))['marge_montant__sum']
    total_prix_revient = simulations_grouped_by_title.aggregate(Sum('prix_de_revient_total'))['prix_de_revient_total__sum']
    total_isb = simulations_grouped_by_title.aggregate(Sum('isb'))['isb__sum']
    total_ht_devis = simulations_grouped_by_title.aggregate(Sum('prix_vente_total_ht_avec_isb'))['prix_vente_total_ht_avec_isb__sum']
    
    # Calculate total_tva and total_ttc_devis
    total_tva = (total_ht_devis * Decimal('0.19')).quantize(Decimal('0.01'))
    total_ttc_devis = (total_ht_devis + total_tva).quantize(Decimal('0.01'))

    # Format totals to string with spaces
    formatted_marge_montant_total = format_number(marge_montant_total)
    formatted_total_prix_revient = format_number(total_prix_revient)
    formatted_total_isb = format_number(total_isb)
    formatted_total_ht_devis = format_number(total_ht_devis)
    formatted_total_tva = format_number(total_tva)
    formatted_total_ttc_devis = format_number(total_ttc_devis)

    # Add totals to the bottom of respective columns
    ws.cell(row=row_num, column=10, value=formatted_marge_montant_total).font = total_font  # Marge Montant Total
    ws.cell(row=row_num, column=10).fill = total_fill
    ws.cell(row=row_num, column=12, value=formatted_total_prix_revient).font = total_font  # Total Prix Revient
    ws.cell(row=row_num, column=12).fill = total_fill
    ws.cell(row=row_num, column=13, value=formatted_total_isb).font = total_font  # ISB
    ws.cell(row=row_num, column=13).fill = total_fill
    
    # Totals with labels
    ws.cell(row=row_num, column=14, value="Total HT Devis").font = total_font
    ws.cell(row=row_num, column=14).alignment = Alignment(horizontal="center")
    ws.cell(row=row_num, column=14).fill = total_fill
    ws.cell(row=row_num, column=15, value=formatted_total_ht_devis).font = total_font
    ws.cell(row=row_num, column=15).fill = total_fill

    ws.cell(row=row_num + 1, column=14, value="TVA").font = total_font
    ws.cell(row=row_num + 1, column=14).alignment = Alignment(horizontal="center")
    ws.cell(row=row_num + 1, column=14).fill = total_fill
    ws.cell(row=row_num + 1, column=15, value=formatted_total_tva).font = total_font
    ws.cell(row=row_num + 1, column=15).fill = total_fill

    ws.cell(row=row_num + 2, column=14, value="Total TTC Devis").font = total_font
    ws.cell(row=row_num + 2, column=14).alignment = Alignment(horizontal="center")
    ws.cell(row=row_num + 2, column=14).fill = total_fill
    ws.cell(row=row_num + 2, column=15, value=formatted_total_ttc_devis).font = total_font
    ws.cell(row=row_num + 2, column=15).fill = total_fill

    # Save the workbook to a BytesIO buffer
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # Return the response as an Excel file
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="detail_simulation_{id_simulation}.xlsx"'

    return response

