#!/usr/bin/env python3

import argparse
from stuff.gapps import Gapps
from stuff.litegapps import LiteGapps
from stuff.magisk import Magisk
from stuff.mindthegapps import MindTheGapps
from stuff.ndk import Ndk
from stuff.houdini import Houdini
from stuff.houdini_hack import Houdini_Hack
from stuff.widevine import Widevine
import tools.helper as helper
import subprocess


def main():
    dockerfile = ""
    tags = []
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-a', '--android-version',
                        dest='android',
                        help='Specify the Android version to build',
                        default='11.0.0',
                        choices=['14.0.0', '13.0.0', '12.0.0', '12.0.0_64only', '11.0.0', '10.0.0', '9.0.0', '8.1.0'])
    parser.add_argument('-g', '--install-gapps',
                        dest='gapps',
                        help='Install OpenGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-lg', '--install-litegapps',
                        dest='litegapps',
                        help='Install LiteGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-n', '--install-ndk-translation',
                        dest='ndk',
                        help='Install libndk translation files',
                        action='store_true')
    parser.add_argument('-i', '--install-houdini',
                        dest='houdini',
                        help='Install houdini files',
                        action='store_true')
    parser.add_argument('-mtg', '--install-mindthegapps',
                        dest='mindthegapps',
                        help='Install MindTheGapps to ReDroid',
                        action='store_true')
    parser.add_argument('-m', '--install-magisk', dest='magisk',
                        help='Install Magisk ( Bootless )',
                        action='store_true')
    parser.add_argument('-w', '--install-widevine', dest='widevine',
                        help='Integrate Widevine DRM (L3)',
                        action='store_true')
    parser.add_argument('-c', '--container', 
                        dest='container',
                        default='docker',
                        help='Specify container type', 
                        choices=['docker', 'podman'])
    parser.add_argument('--base-image',
                        dest='base_image',
                        default=None,
                        help='Custom base image instead of redroid/redroid:<android>-latest')
    parser.add_argument('--output-image',
                        dest='output_image',
                        default=None,
                        help='Custom output image name:tag')

    args = parser.parse_args()
    base_image = args.base_image if args.base_image else "redroid/redroid:{}-latest".format(args.android)
    dockerfile = dockerfile + "FROM {}\n".format(base_image)
    tags.append(args.android)
    if args.gapps:
        if args.android in ["11.0.0"]:
            Gapps().install()
            dockerfile = dockerfile + "COPY gapps /\n"
            tags.append("gapps")
        else:
            helper.print_color( "WARNING: OpenGapps only supports 11.0.0", helper.bcolors.YELLOW)
    if args.litegapps:
        LiteGapps(args.android).install()
        dockerfile = dockerfile + "COPY litegapps /\n"
        tags.append("litegapps")
    if args.mindthegapps:
        MindTheGapps(args.android).install()
        dockerfile = dockerfile + "COPY mindthegapps /\n"
        tags.append("mindthegapps")
    if args.ndk:
        if args.android in ["11.0.0", "12.0.0", "12.0.0_64only"]:
            arch = helper.host()[0]
            if arch == "x86" or arch == "x86_64":
                Ndk().install()
                dockerfile = dockerfile+"COPY ndk /\n"
                tags.append("ndk")
        else:
            helper.print_color(
                "WARNING: Libndk seems to work only on redroid:11.0.0 or redroid:12.0.0", helper.bcolors.YELLOW)
    if args.houdini:
        if args.android in ["8.1.0", "9.0.0", "11.0.0", "12.0.0", "13.0.0", "14.0.0"]:
            arch = helper.host()[0]
            if arch == "x86" or arch == "x86_64":
                Houdini(args.android).install()
                if not args.android == "8.1.0":
                    Houdini_Hack(args.android).install()
                dockerfile = dockerfile+"COPY houdini /\n"
                tags.append("houdini") 
        else:
            helper.print_color(
                "WARNING: Houdini seems to work only above redroid:11.0.0", helper.bcolors.YELLOW)
    if args.magisk:
        Magisk().install()
        dockerfile = dockerfile+"COPY magisk /\n"
        tags.append("magisk")
    if args.widevine:
        Widevine(args.android).install()
        dockerfile = dockerfile+"COPY widevine /\n"
        tags.append("widevine")
    print("\nDockerfile\n"+dockerfile)
    with open("./Dockerfile", "w") as f:
        f.write(dockerfile)
    if args.output_image:
        new_image_name = args.output_image
    elif args.base_image:
        if ":" in args.base_image:
            repo, base_tag = args.base_image.rsplit(":", 1)
            new_image_name = "{}:{}_{}".format(repo, base_tag, "_".join(tags[1:])) if len(tags) > 1 else args.base_image
        else:
            new_image_name = "{}:{}".format(args.base_image, "_".join(tags))
    else:
        new_image_name = "redroid/redroid:"+"_".join(tags)
    subprocess.run([args.container, "build", "-t", new_image_name, "."])
    helper.print_color("Successfully built {}".format(
        new_image_name), helper.bcolors.GREEN)


if __name__ == "__main__":
    main()
