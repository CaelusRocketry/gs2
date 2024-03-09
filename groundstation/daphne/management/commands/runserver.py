from daphne.management.commands.runserver import Command as RunserverCommand

from groundstation.settings import CONFIG, CONFIG_SCHEMA, SKIP_CONF_CHECKS
from jsonschema import validate, Draft202012Validator

class Command(RunserverCommand):
    def check(self, *args, **kwargs):
        super().check(args, kwargs)

        if not SKIP_CONF_CHECKS:
            self.stdout.write("Checking configuration schema\n")
            validate(instance=CONFIG, schema=CONFIG_SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
        else:
            self.stdout.write("Skipping configuration schema validation...")