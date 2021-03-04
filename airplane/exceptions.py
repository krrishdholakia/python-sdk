class RunPendingException(Exception):
    pass


class InvalidEnvironmentException(Exception):
    def __str__(self):
        return "This task must be run inside of the Airplane runtime."
