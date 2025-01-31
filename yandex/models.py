class ResponseYaGpt:
  def __init__(self, answer, sources, answer_without_sources, is_main = False):
    self.is_main = is_main
    self.answer = answer
    self.sources = sources
    self.answer_without_sources = answer_without_sources

  def __repr__(self):
    return (
            f"ResponseYaGpt(\n"
            f"  answer={self.answer},\n"
            f"  sources=[\n    " +
            ",\n    ".join(str(source) for source in self.sources) +
            "\n  ],\n"
            f"  answer_without_sources={self.answer_without_sources}\n"
            f")"
    )


class ResponseSource:
  def __init__(self, title: str, url: str, index: str):
    self.title = title
    self.url = url
    self.index = index

  def __repr__(self):
    return f"ResponseSource(index='{self.index}', title='{self.title}', url='{self.url}')"
