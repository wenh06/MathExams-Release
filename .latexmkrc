# vim: set ft=perl:
# In latexmk 4.83+, bare names in $clean_ext are literal globs, not extensions.
# Use %R.EXT so they expand to $JOBNAME.EXT (e.g. %R.bbl -> main.bbl).
$clean_ext = '%R.thm %R.glo %R.gls %R.bbl %R.hd %R.loe %R.synctex.gz %R.run.xml %R.bcf %R.run %R.tdo %R-blx.bib %R.toe %R.fls %R.spl %R.nav %R.snm *.tex.bak';

# Explicitly use biber for biblatex (auto-detected via .bcf, but made explicit here)
$biber = 'biber %O %S';
# $out_dir = 'build';
$ENV{'TZ'}='Asia/Shanghai';
$pdf_mode = 5;
$dvi_mode = 0;
$postscript_mode = 0;
