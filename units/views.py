from .models import Unit
from django.shortcuts import render

def units(request):
	units = Unit.objects.filter(draft=False).order_by('id')
	return render(request, 'units/units.html', {'units': units})

def unit(request, unit_id):
	unit = Unit.objects.get(pk=unit_id)
	challenges = unit.challenges.all().order_by('unitchallenge__display_order')
	resources = unit.resources.all()
	return render(request, 'units/unit.html', {
		'unit': unit,
		'challenges': challenges,
		'resources': resources
	})
