from rpicenter import rpic

def main():
    try:
        rpic.run()
    except KeyboardInterrupt:
        print("=== Shutdown requested! exiting ===")
    except Exception as ex:
        print("Err: " + str(ex))
    finally:
        print("App terminated, cleanup...")
        rpic.cleanup()

if __name__ == '__main__':
    print(str(rpic))
    main()
