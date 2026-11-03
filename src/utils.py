import logging

def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    datefmt="%H:%M:%S"
    )
