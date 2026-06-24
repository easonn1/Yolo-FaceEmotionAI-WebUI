from function.cli import main


if __name__ == "__main__":
    import sys

    extra_args = sys.argv[1:]
    if "--device" not in extra_args:
        extra_args = ["--device", "cuda", *extra_args]
    sys.argv = [sys.argv[0], *extra_args]
    raise SystemExit(main())
