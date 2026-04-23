from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from datetime import datetime, UTC


class GeneratedDatePostprocessor(Postprocessor):
    def run(self, text):
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        footer = f"\n\n---\n\n*Page generated on: {now}*"
        return text + footer


class GeneratedDateExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(GeneratedDatePostprocessor(), 'generated_date', 27)


def makeExtension(**kwargs):
    return GeneratedDateExtension(**kwargs)
