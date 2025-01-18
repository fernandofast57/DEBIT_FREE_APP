
class DistributionError(Exception):
    """Exception raised for errors in the distribution process."""
    def __init__(self, message="An error occurred during distribution"):
        self.message = message
        super().__init__(self.message)
