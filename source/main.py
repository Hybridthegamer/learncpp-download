import argparse
import sys
import logging
from helper import weasy


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weasy", action="store_true")
    parser.add_argument("--pisa", action="store_true")
    parser.add_argument("--sequential", action="store_true")

    return parser.parse_args()


args = argument_parser()

logging.getLogger('weasyprint').setLevel(100)


if args.sequential:
    instance = weasy.WeasySequential()
else:
    import ray

    from helper import render

    ray.init(log_to_driver=False)
    if args.weasy:
        instance = render.WeasyRender()
    elif args.pisa:
        instance = render.PisaRender()
    else:
        instance = render.WkRender()

if __name__ == "__main__":
    instance.download()
