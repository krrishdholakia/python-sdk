class RunPendingException(Exception):
    pass


class InvalidEnvironmentException(Exception):
    def __str__(self) -> str:
        return "This task must be run inside of the Airplane runtime."
