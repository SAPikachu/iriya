import argparse
from collections import namedtuple
import logging
import sys
import re

from pysubs2 import SSAFile

from .nativeapi import FontContext

ENTRYPOINT = "iriya"

ContextKey = namedtuple("ContextKey", ["name", "bold", "italics"])
ContextKey.__str__ = lambda self: "{}{}{}".format(
    self.name, "+Bold" if self.bold else "", "+Italics" if self.italics else ""
)

TAG_RE = re.compile(r"(\{.*?\})")
TAG_PART_RE = re.compile(r"(fn|b(?=[01])|i(?=[01]))(.+)", flags=re.I)


def key_from_style(style):
    return ContextKey(style.fontname, style.bold, style.italic)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=ENTRYPOINT,
        description="Checks whether all characters in ASS file exist in declared fonts"
    )
    parser.add_argument("files", nargs="+")
    parser.add_argument("--log-level", "-l", default="info",
                        choices=("debug", "info", "warn", "error"))

    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level.upper())
    log = logging.getLogger(ENTRYPOINT)
    contexts = {}
    have_nonexistent_char = False

    def get_context(key):
        if key not in contexts:
            log.debug("New font: %s", key)
            contexts[key] = FontContext(**key._asdict())

        return contexts[key]

    for name in args.files:
        ssa = SSAFile.load(name)
        line_number = 0
        for event in ssa.events:
            line_number += 1
            if "type=Comment" in str(event):
                continue
            style = ssa.styles[event.style]
            key = key_from_style(style)
            context = get_context(key)

            text = event.text
            while text:
                m = TAG_RE.search(text)
                display_text = text if not m else text[:m.start()]
                log.debug("Text block: %s", display_text)
                result = context.check(display_text)
                if result:
                    have_nonexistent_char = True
                    log.warning("%s Dialogue #%s: [%s] does not exist in %s",
                             name, line_number, "".join(result), key)

                text = "" if not m else text[m.end():]
                if not text:
                    break

                ovr_tags = m.group(0)[1:-1].split("\\")
                log.debug("Override tags: %s", ovr_tags)
                for tag in ovr_tags:
                    tag = tag.rstrip()
                    if tag[:1].lower() == "r":
                        if len(tag) == 1:
                            key = key_from_style(style)
                        else:
                            style_str = tag[1:]
                            key = key_from_style(ssa.styles[style_str])
                        continue

                    tag_match = TAG_PART_RE.match(tag)
                    if not tag_match:
                        continue

                    type = tag_match.group(1).lower()
                    if type == "fn":
                        key = key._replace(name=tag_match.group(2))
                    elif type == "b":
                        key = key._replace(bold=bool(int(tag_match.group(2))))
                    elif type == "i":
                        key = key._replace(italics=bool(int(tag_match.group(2))))

                context = get_context(key)

    sys.exit(1 if have_nonexistent_char else 0)


if __name__ == '__main__':
    main()
