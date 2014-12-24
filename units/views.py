from .models import Unit
from django.shortcuts import render

def units(request):
	units = Unit.objects.all()
	return render(request, 'units.html', {'units': units})

def unit(request, unit_id):
	unit = Unit.objects.get(pk=unit_id)
	challenges = unit.challenges.all()
	return render(request, 'unit.html', {'unit': unit, 'challenges': challenges})
