import argparse, logging

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def main():
    # Configure argument parser
    parser = argparse.ArgumentParser(prog='rpicenter', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true', help=('log detailed debugging messages'))
    parser.add_argument('-i', '--info', action='store_true', help=('log info messages'))
    parser.add_argument('-l', '--log', action='store_true', help=('log into a file instead to screen'))
    args = parser.parse_args()

    # Configure logging
    if args.debug:
        log_level = logging.DEBUG
    elif args.info:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    if args.log:
        logging.basicConfig(filename='rpicenter.log', level=log_level, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=log_level, format=LOG_FORMAT)

    from rpicenter import rpicenter

    try:
        logging.info("=== RPiCenter Started ===")
        if rpicenter is not None: rpicenter.run()
    except KeyboardInterrupt:
        logging.info("=== Shutdown requested! exiting ===")
    except Exception as ex:
        logging.error(ex, exc_info=True)
        raise
    finally:
        logging.debug("App terminated, cleanup...")
        if rpicenter is not None: rpicenter.cleanup()

if __name__ == '__main__':
    main()
