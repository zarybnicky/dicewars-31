def get_logging_level(args):
    """
    Parse command-line arguments.
    """
    if args.debug.lower() == 'debug':
        logging = 10
    elif args.debug.lower() == 'info':
        logging = 20
    elif args.debug.lower() == 'error':
        logging = 40
    else:
        logging = 30

    return logging
