import re
import shutil
import sys
from pathlib import Path

from compile import execute_cmd


def compile_all():
    project_dir = Path(__file__).resolve().parent
    build_dir = project_dir / "build"
    if not build_dir.exists():
        build_dir.mkdir(parents=True, exist_ok=True)
    main_tex_file = project_dir / "main.tex"
    content_file_pattern = re.compile(
        "\\\\input\\{content\\/(?P<content_file_rel_path>[^\\}]+)\\}",
        re.MULTILINE,
    )
    content_files = content_file_pattern.findall(main_tex_file.read_text())

    for content_file in content_files:
        print("#" * 80)
        print(f"  Compiling {content_file}...  ".center(80, " "))
        print("#" * 80)
        tmp_main_content = re.sub(content_file_pattern, "", main_tex_file.read_text())
        tmp_main_content += f"\\input{{content/{content_file}}}"
        tmp_main_file = project_dir / "tmp_main.tex"
        tmp_main_file.write_text(tmp_main_content)

        cmd = f"""xelatex "{str(tmp_main_file)}" """
        try:
            exitcode = execute_cmd(cmd)
        except KeyboardInterrupt:
            # clean up
            cmd = f"""latexmk -C -outdir="{str(project_dir)}" "{str(tmp_main_file)}" """
            execute_cmd(cmd, raise_error=False)
            tmp_main_file.unlink(missing_ok=True)
            print("Compilation cancelled.")
            exitcode = 1
        if exitcode != 0:
            tmp_main_file.unlink(missing_ok=True)
            sys.exit(exitcode)
        generated_pdf_file = project_dir / f"{tmp_main_file.stem}.pdf"
        # rename to content_file.replace(".tex", ".pdf").replace("/", "-")
        # and move to build_dir
        shutil.move(generated_pdf_file, (build_dir / content_file.replace(".tex", "").replace("/", "-")).with_suffix(".pdf"))
        # clean up
        cmd = f"""latexmk -C -outdir="{str(project_dir)}" "{str(tmp_main_file)}" """
        exitcode = execute_cmd(cmd)
        if exitcode != 0:
            tmp_main_file.unlink(missing_ok=True)
            sys.exit(exitcode)
        # in case bbl file is not cleaned up
        bbl_file = project_dir / f"{tmp_main_file.stem}.bbl"
        if bbl_file.exists():
            bbl_file.unlink()
        # clear files of the pattern xelatex*.fls
        for fls_file in project_dir.glob("xelatex*.fls"):
            fls_file.unlink()
        tmp_main_file.unlink(missing_ok=True)

        print("#" * 80)
        print(f"   Compiled {content_file}.   ".center(80, " "))
        print("#" * 80)

    print("All files compiled.")
    return 0


if __name__ == "__main__":
    compile_all()
