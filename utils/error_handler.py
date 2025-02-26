from utils.logger import get_logger

logger = get_logger("ErrorHandler", "errors.log")

def log_and_raise(error: Exception, message: str = "", critical: bool = False):
    """
    Logs an error and optionally raises it.

    :param error: The Exception instance.
    :param message: Custom message for context (optional).
    :param critical: If True, logs as critical and raises exception.
    """
    error_message = f"{message} - {str(error)}"

    if critical:
        logger.critical(error_message, exc_info=True)
        raise error  # Stop execution for critical errors
    else:
        logger.error(error_message, exc_info=True)  # Log and continue

def safe_execute(func, *args, **kwargs):
    """
    Executes a function safely, logs errors but does not stop execution.

    :param func: Function to execute
    :return: Function result or None if error occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
        return None  # Fail gracefully
