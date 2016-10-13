from .models import Unit
from django.shortcuts import render, get_object_or_404

def units(request):
	units = Unit.objects.filter(listed=True).order_by('id')
	return render(request, 'units/units.html', {'units': units})

def unit(request, unit_id=None, slug=None):
	unit = get_object_or_404(Unit, id=unit_id) if unit_id else get_object_or_404(Unit, slug=slug)
	challenges = unit.challenges.all().order_by('unitchallenge__display_order')
	resources = unit.resources.all()
	return render(request, 'units/unit.html', {
		'unit': unit,
		'challenges': challenges,
		'resources': resources
	})
