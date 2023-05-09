from manim import *
import os
from subprocess import Popen


def str_to_valid_filename(s: str):
    return "".join((s for s in s if s.isalnum() or s in "._-"))


def common_str_to_typst_str(common_str: str, font_size: int = 24, color: str = WHITE):
    template = rf"""#set text(fill: rgb("{color}"), size: {font_size}pt)

{common_str}"""
    return template


def math_str_to_common_str(math_str: str):
    return f"$ {math_str} $"


def typst_str_to_typ(typst_str: str, typst_file_path: str):
    if os.path.exists(typst_file_path):
        return typst_file_path
    with open(typst_file_path, "w") as f:
        f.write(typst_str)
    return typst_file_path


def typ_to_pdf(typ_file_path: str):
    pdf_file_path = typ_file_path.replace(".typ", ".pdf")
    if os.path.exists(pdf_file_path):
        return pdf_file_path
    p = Popen(f"typst compile {typ_file_path} {pdf_file_path}".split(" "))
    p.wait()
    return pdf_file_path


def pdf_to_svg(pdf_file_path: str):
    svg_file_path = pdf_file_path.replace(".pdf", ".svg")
    if os.path.exists(svg_file_path):
        return svg_file_path
    p = Popen(f"pdf2svg {pdf_file_path} {svg_file_path}".split(" "))
    p.wait()
    return svg_file_path


def common_str_to_svg(common_str: str, font_size: int = 48, color: str = WHITE):
    typst_str = common_str_to_typst_str(common_str, font_size, color)
    typ_file_path = typst_str_to_typ(typst_str, str_to_valid_filename(f"{common_str}.typ"))
    pdf_file_path = typ_to_pdf(typ_file_path)
    svg_file_path = pdf_to_svg(pdf_file_path)
    return svg_file_path


class Typst(SVGMobject):
    def __init__(self, common_str, font_size=48, font_color=WHITE, **kwargs):
        svg_file_path = common_str_to_svg(common_str, font_size, font_color)
        super().__init__(svg_file_path, height=24 / font_size, **kwargs)


class MathTypst(Typst):
    def __init__(self, math_str, font_size=48, font_color=WHITE, **kwargs):
        super().__init__(math_str_to_common_str(math_str), font_size, font_color, **kwargs)
        

class TypstScene(Scene):
    def construct(self):
        txt = Typst("Hello, World!")
        math = MathTypst("x^2 + y^2 = z^2")
        vg = VGroup(txt, math).arrange(DOWN)
        self.play(Succession(*[Write(m) for m in vg]))
