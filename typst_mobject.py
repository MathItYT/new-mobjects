from manim import *
import shutil
import os
from subprocess import Popen


def str_to_valid_filename(s: str):
    return "".join((s for s in s if s.isalnum() or s in "._-"))


def common_str_to_typst_str(common_str: str, font_size: int = 24, color: str = WHITE):
    template = rf"""#set text(fill: rgb("{color}"), size: {font_size}pt)
#set page(width: 2000pt)

{common_str}"""
    return template


def math_str_to_common_str(math_str: str):
    return f"$ {math_str} $"


def typst_str_to_typ(typst_str: str, typst_file_name: str, folder: str = "typst"):
    file = os.path.join(folder, typst_file_name)
    if not os.path.exists(folder):
        os.mkdir(folder)
    if os.path.exists(file):
        return file
    with open(file, "w") as f:
        f.write(typst_str)
    return file


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


def common_str_to_svg(common_str: str, font_size: int = 48, color: str = WHITE, folder: str = "typst"):
    typst_str = common_str_to_typst_str(common_str, font_size, color)
    typ_file_path = typst_str_to_typ(typst_str, str_to_valid_filename(f"{common_str}.typ"), folder)
    pdf_file_path = typ_to_pdf(typ_file_path)
    svg_file_path = pdf_to_svg(pdf_file_path)
    return svg_file_path


class Typst(SVGMobject):
    def __init__(self, common_str, font_size=48, color=WHITE, folder: str = "typst", **kwargs):
        self.svg_file_path = common_str_to_svg(common_str, font_size, color, folder)
        self.font_size = font_size
        self.folder = folder
        self.kwargs = kwargs
        if "stroke_width" not in kwargs:
            self.kwargs["stroke_width"] = 0
        super().__init__(self.svg_file_path, height=None, color=color, **kwargs)
        self.scale(1 / 100)
    
    def set_text(self, text: str, font_size: int = None, color: str = None, folder: str = None):
        fp = self.svg_file_path
        os.remove(fp)
        os.remove(fp.replace(".svg", ".pdf"))
        os.remove(fp.replace(".svg", ".typ"))
        if font_size is None:
            font_size = self.font_size
        if color is None:
            color = self.color.get_hex()
        if folder is None:
            folder = self.folder
        new_mob = type(self)(text, self.font_size, color, self.folder, **self.kwargs)
        self.become(new_mob)
        self.svg_file_path = new_mob.svg_file_path
        return self


class MathTypst(Typst):
    def __init__(self, math_str, font_size=48, color=WHITE, folder: str = "typst", **kwargs):
        super().__init__(math_str_to_common_str(math_str), font_size, color, folder, **kwargs)


class TypstScene(Scene):
    def construct(self):
        if os.path.exists("typst"):
            shutil.rmtree("typst")
        txt = Typst("Hello, World!")
        math = MathTypst("x^2 + y^2 = z^2")
        vg = VGroup(txt, math).arrange(DOWN)
        self.play(LaggedStartMap(FadeIn, txt, scale=2))
        self.wait()
        self.play(Write(math))
        self.wait()
        self.play(vg.animate.to_edge(UP))
        this_is_str = "This is a Typst text in Manim!"
        this_is = Typst(this_is_str)
        self.play(FadeIn(this_is, shift=UP))
        idx = this_is_str.index("Typst")
        self.play(Indicate(this_is[idx - 4:idx + 1]))
        self.wait()
        self.play(FadeOut(*self.mobjects))
        sq = Rectangle(width=2, height=2, fill_opacity=0.5, fill_color=BLUE)
        self.play(DrawBorderThenFill(sq))
        br_width = Brace(sq, UP)
        br_height = Brace(sq, RIGHT)
        width_typst = Typst(f"Width: ${sq.width}$")
        br_width.put_at_tip(width_typst)
        height_typst = Typst(f"Height: ${sq.height}$")
        br_height.put_at_tip(height_typst)
        self.play(GrowFromCenter(br_width), GrowFromCenter(br_height))
        self.play(Write(width_typst), Write(height_typst))
        self.wait()

        def width_typst_updater(m: Typst):
            m.set_text(f"Width: ${np.round(sq.width, decimals=2)}$")
            br_width.become(Brace(sq, UP))
            br_width.put_at_tip(m)
        
        def height_typst_updater(m: Typst):
            m.set_text(f"Height: ${np.round(sq.height, decimals=2)}$")
            br_height.become(Brace(sq, RIGHT))
            br_height.put_at_tip(m)
        
        width_typst.add_updater(width_typst_updater)
        height_typst.add_updater(height_typst_updater)

        self.play(sq.animate.stretch_to_fit_height(3))
        self.play(sq.animate.stretch_to_fit_width(3))
        self.play(sq.animate.stretch_to_fit_height(1))
        self.play(sq.animate.stretch_to_fit_width(1))
        self.play(sq.animate.stretch_to_fit_height(2))
        width_typst.clear_updaters()
        height_typst.clear_updaters()
        self.wait()
        this_was_rendered_so_fast = Typst("This was rendered so fast!").to_edge(UP)
        self.play(FadeIn(this_was_rendered_so_fast, scale=2))
        self.wait()


class TypstOutro(Scene):
    def construct(self):
        if os.path.exists("typst"):
            shutil.rmtree("typst")
        txt_str = "#set align(center)\n\nAvailable on GitHub!\n\nhttps://github.com/MathLike/new-mobjects"
        txt = Typst(txt_str)
        self.play(FadeIn(txt, shift=UP))
        github_idx = txt_str.replace("#set align(center)\n\n", "").replace(" ", "").find("GitHub")
        github = txt[github_idx:github_idx + 6]
        self.play(github.animate.set_color(YELLOW))
        self.wait()
