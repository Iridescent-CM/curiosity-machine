from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from season_markers.middleware import get_season_marker_config
from season_markers.models import SeasonMarker

STATEMENT = """
Is a season configured?     {configured}
Are we in season?           {in_season}

Season marker parameters:
    start:  {start}
    end:    {end}
    name:   {name}

Can be created in database?     {creatable}
"""

class Command(BaseCommand):
    help = "Output information on the currently configured season marker"

    def handle(self, *args, **options):
        config = get_season_marker_config()
        model = SeasonMarker(**config.model_fields)

        validation_errors = None
        try:
            model.full_clean()
            creatable = True
        except ValidationError as e:
            validation_errors = e.message_dict
            creatable = False

        print(
            STATEMENT.format(
                configured = 'yes' if config.season_configured() else 'no',
                in_season = 'yes' if config.in_season() else 'no',
                start = config.start,
                end = config.end,
                name = config.name,
                creatable = 'yes' if creatable else 'no'
            )
        )

        if not creatable:
            print("Validation errors:")
            for field, msgs in validation_errors.items():
                for msg in msgs:
                    print("    {}: {}".format(field, msg))

