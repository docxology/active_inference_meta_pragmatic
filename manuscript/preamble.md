# LaTeX preamble

Required packages and layout choices for the pinned template renderer.

```latex
\usepackage[margin=0.35in,includefoot,footskip=0.18in]{geometry}
\usepackage{amsmath,amssymb,graphicx,booktabs,longtable,array}
\usepackage{float,caption,natbib,hyperref,microtype,xcolor,needspace}
\definecolor{PublicationRed}{HTML}{CC0000}
\hypersetup{colorlinks=true,linkcolor=PublicationRed,citecolor=PublicationRed,urlcolor=PublicationRed}
\setcounter{tocdepth}{2}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}
\emergencystretch=2em
```
