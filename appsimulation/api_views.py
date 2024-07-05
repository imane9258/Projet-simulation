from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Simulation
from .serializers import SimulationSerializer

@api_view(['GET'])
def get_simulations(request):
    simulations = Simulation.objects.all()
    serializer = SimulationSerializer(simulations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def connexion(request):
    # Logique de connexion ici
    return Response({'success': True})
