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
def accueil(request):
    return render(request, 'accueil.html')

@login_required

@login_required
def liste_simulations(request):
    simulations = Simulation.objects.all()
    context = {
        'simulations': simulations,
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
                prix_total_achat = quantite * prix_unitaire
                pourcentage_banque_montant = (prix_total_achat * pourcentage_banque) / Decimal('100.00')
                prix_de_revient_total = prix_total_achat + frais_transit + frais_douane + pourcentage_banque_montant
                marge_montant = (prix_de_revient_total * marge_percentage) / Decimal('100.00')
                prix_vente_total_ht_sans_isb = prix_de_revient_total + marge_montant
    
                prix_vente_total_ht_avec_isb = (prix_vente_total_ht_sans_isb) / Decimal('0.98')
                isb_montant = (prix_vente_total_ht_avec_isb * Decimal('0.02'))
                prix_vente_total_ht = (prix_vente_total_ht_avec_isb) / quantite
              

                # Cumul des totaux pour toutes les lignes de simulation
                marge_montant_total += marge_montant
                total_prix_revient += prix_de_revient_total
                total_isb += isb_montant
                total_ht_devis += prix_vente_total_ht_avec_isb
                total_tva = (prix_vente_total_ht_avec_isb * Decimal('0.19'))
                total_ttc_devis = total_ht_devis + total_tva
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

    total_ht_devis = sum(simulation.prix_vente_total_ht_avec_isb for simulation in simulations)
    marge_montant_total = sum(simulation.marge_montant for simulation in simulations)
    total_prix_revient = sum(simulation.prix_de_revient_total for simulation in simulations)
    total_isb = sum(simulation.isb for simulation in simulations)
    
    # Calculating total_tva based on total_ht_devis
    total_tva = total_ht_devis * Decimal('0.19')
    # Calculating total_ttc_devis based on total_ht_devis and total_tva
    total_ttc_devis = total_ht_devis + total_tva

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

    total_ht_devis = sum(simulation.prix_vente_total_ht_avec_isb for simulation in simulations)
    marge_montant_total = sum(simulation.marge_montant for simulation in simulations)
    total_prix_revient = sum(simulation.prix_de_revient_total for simulation in simulations)
    total_isb = sum(simulation.isb for simulation in simulations)
    total_tva = sum(simulation.prix_vente_total_ht_avec_isb * Decimal('0.19') for simulation in simulations)
    total_ttc_devis = total_ht_devis + total_tva

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
        p.drawString(20 * mm, y_position, f"Désignation: {simulation.designation}")
        y_position -= 10 * mm

        p.setFont("Helvetica", 10)
        p.drawString(20 * mm, y_position, f"Prix d'Achat Unitaire: {simulation.prix}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Quantité: {simulation.quantite}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix Total Achat: {simulation.prix_total_achat}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Frais Transit: {simulation.montant_transit}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Frais Douane: {simulation.montant_douane}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Pourcentage Banque: {simulation.pourcentage_banque}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Montant Banque: {simulation.pourcentage_banque_montant}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Marge Pourcentage: {simulation.marge_pourcentage}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Montant Marge: {simulation.marge_montant}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix Vente Unitaire: {simulation.prix_vente_total_ht}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Prix de Revient: {simulation.prix_vente_total_ht_sans_isb}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"ISB: {simulation.isb}")
        y_position -= 5 * mm
        p.drawString(20 * mm, y_position, f"Total HT avec ISB: {simulation.prix_vente_total_ht_avec_isb}")
        y_position -= 10 * mm

    # Totals
    y_position -= 10 * mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(20 * mm, y_position, "Totaux")
    y_position -= 10 * mm

    p.setFont("Helvetica", 10)
    p.drawString(20 * mm, y_position, f"Marge Montant Total: {marge_montant_total}")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total Prix Revient: {total_prix_revient}")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"ISB: {total_isb}")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total HT du Devis: {total_ht_devis}")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"TVA: {total_tva}")
    y_position -= 5 * mm
    p.drawString(20 * mm, y_position, f"Total TTC du Devis: {total_ttc_devis}")

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

@login_required
def liste_simulations(request):
    simulations = Simulation.objects.all()
    return render(request, 'liste_simulations.html', {'simulations': simulations})

from django.shortcuts import render, get_object_or_404
from .models import Simulation

def detail_simulation(request, simulation_id):
    simulation = get_object_or_404(Simulation, id_simulation=simulation_id)
    context = {
        'simulation': simulation
    }
    return render(request, 'detail_simulation.html', context)
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Simulation
from decimal import Decimal

from decimal import Decimal, InvalidOperation

def edit_simulation(request, id_simulation):
    simulation = Simulation.objects.get(id_simulation=id_simulation)

    if request.method == 'POST':
        titre = request.POST.get('titre', '')
        designation = request.POST.get('designation', '')
        quantite = request.POST.get('quantite', '0')
        prix_unitaire = request.POST.get('prix_unitaire', '0')
        frais_transit = request.POST.get('frais_transit', '0')
        frais_douane = request.POST.get('frais_douane', '0')
        marge_percentage = request.POST.get('marge_percentage', '0')
        pourcentage_banque = request.POST.get('pourcentage_banque', '0')

        # Ensure that numeric values are properly converted to Decimal
        try:
            quantite = Decimal(quantite)
            prix_unitaire = Decimal(prix_unitaire)
            frais_transit = Decimal(frais_transit)
            frais_douane = Decimal(frais_douane)
            marge_percentage = Decimal(marge_percentage)
            pourcentage_banque = Decimal(pourcentage_banque)
        except (InvalidOperation, ValueError):
            # Handle invalid input values
            quantite = Decimal('0')
            prix_unitaire = Decimal('0')
            frais_transit = Decimal('0')
            frais_douane = Decimal('0')
            marge_percentage = Decimal('0')
            pourcentage_banque = Decimal('0')

        # Perform calculations
        prix_total_achat = quantite * prix_unitaire
        pourcentage_banque_montant = (prix_total_achat * pourcentage_banque) / Decimal('100.00')
        prix_de_revient_total = prix_total_achat + frais_transit + frais_douane + pourcentage_banque_montant
        marge_montant = (prix_de_revient_total * marge_percentage) / Decimal('100.00')
        prix_vente_total_ht_sans_isb = prix_de_revient_total + marge_montant
        prix_vente_total_ht_avec_isb = (prix_vente_total_ht_sans_isb) / Decimal('0.98')
        isb_montant = (prix_vente_total_ht_avec_isb * Decimal('0.02'))
        prix_vente_total_ht = (prix_vente_total_ht_avec_isb) / quantite

        # Update simulation object with new values
        simulation.titre = titre
        simulation.designation = designation
        simulation.quantite = quantite
        simulation.prix = prix_unitaire
        simulation.montant_transit = frais_transit
        simulation.montant_douane = frais_douane
        simulation.marge_pourcentage = marge_percentage
        simulation.pourcentage_banque = pourcentage_banque
        simulation.save()

        return redirect('detail_simulation', simulation_id=simulation.id_simulation)

    return render(request, 'edit_simulation.html', {'simulation': simulation})
