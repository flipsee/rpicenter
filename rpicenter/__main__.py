from rpicenter import rpicenter

def main():
    try:
        if rpicenter is not None: rpicenter.run()
    except KeyboardInterrupt:
        print("=== Shutdown requested! exiting ===")
    except Exception as ex:
        print("Err: " + str(ex))
        raise
    finally:
        print("App terminated, cleanup...")
        if rpicenter is not None: rpicenter.cleanup()

if __name__ == '__main__':
    main()
