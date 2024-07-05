# utils.py

def recalculer_simulation(simulation):
    simulation.prix_total_achat = simulation.prix * simulation.quantite
    simulation.prix_de_revient_total = simulation.prix_total_achat + simulation.montant_transit + simulation.montant_douane
    simulation.marge_montant = (simulation.pourcentage_marge / 100) * simulation.prix_de_revient_total
    simulation.prix_vente_total_ht = simulation.prix_de_revient_total + simulation.marge_montant
    simulation.total_tva = simulation.prix_vente_total_ht * 0.19
    simulation.total_ttc_devis = simulation.prix_vente_total_ht + simulation.total_tva
    simulation.save()
