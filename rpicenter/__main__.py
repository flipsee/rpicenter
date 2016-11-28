import rpicenter

def main():
    try:
        if rpicenter.rpic is not None: rpicenter.rpic.run()
    except KeyboardInterrupt:
        print("=== Shutdown requested! exiting ===")
    except Exception as ex:
        print("Err: " + str(ex))
    finally:
        print("App terminated, cleanup...")
        if rpicenter.rpic is not None: rpicenter.rpic.cleanup()

if __name__ == '__main__':
    main()
