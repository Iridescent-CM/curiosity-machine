from django.core.management.base import BaseCommand, CommandError
from seasons.middleware import get_season

STATEMENT = """
Is a season configured?     {configured}
Are we in season?           {in_season}

Season parameters:
    start:  {start}
    end:    {end}
    name:   {name}
"""

class Command(BaseCommand):
    help = "Output information on the currently configured season"

    def handle(self, *args, **options):
        season = get_season()
        print(STATEMENT.format(
            configured = 'yes' if season.season_configured() else 'no',
            in_season = 'yes' if season.in_season() else 'no',
            start = season.start,
            end = season.end,
            name = season.name
        ))
