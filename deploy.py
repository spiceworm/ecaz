#!/usr/bin/env python
import argparse
import subprocess

import git


def get_latest_tag():
    repo = git.Repo(".")
    return sorted(repo.tags, key=lambda tag: tag.name)[-1]


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-p",
        "--push",
        action="store_true",
        help="Push the last image without building.",
    )
    parser.add_argument(
        "-t",
        "--tag",
        default=get_latest_tag(),
        help="Tag the newly built image before pushing. Tag HEAD with TAG if not in git history.",
    )
    return parser.parse_args()


def main(args):
    registry_url = f"registry.digitalocean.com/ecaz-xyz"
    image_url = f"{registry_url}/app:{args.tag}"

    sp_kwargs = {}
    if args.push:
        subprocess.check_call(["docker", "push", image_url], **sp_kwargs)
    else:
        subprocess.check_call(["docker", "compose", "build", "--no-cache"], **sp_kwargs)
        subprocess.check_call(
            ["docker", "tag", f"{registry_url}/app:latest", image_url], **sp_kwargs
        )
        subprocess.check_call(["docker", "push", image_url], **sp_kwargs)


if __name__ == "__main__":
    main(parse_args())
