% =============================================================================
% resume.cls — single-column CV class in the MIT CV / classic academic style.
% Engine: pdfLaTeX.  Self-contained: only standard TeX Live packages.
%
% Extracted from resume.tex so tailored per-job CVs (applications/**/cv.tex) can
% share one look via \documentclass{resume}. Build resolves this file via
% TEXINPUTS (see scripts/build-application.sh); resume.tex resolves it locally.
% =============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2026/06/16 Radheem CV class]

% Pass class options (e.g. 11pt, a4paper) through to article.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

% ---- Packages ---------------------------------------------------------------
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
% English is the main language; \selectlanguage{ngerman} switches the appended
% German version (hyphenation, \today). See the bilingual application templates.
\RequirePackage[main=english,ngerman]{babel}
\RequirePackage{lmodern}
\RequirePackage[top=0.9cm,bottom=0.9cm,left=1.3cm,right=1.3cm]{geometry}
\RequirePackage{titlesec}
\RequirePackage{enumitem}
\RequirePackage{microtype}
\RequirePackage{xcolor}
\RequirePackage[hidelinks]{hyperref}

% ---- Colours / links --------------------------------------------------------
\definecolor{linkblue}{RGB}{0,84,159}
\hypersetup{colorlinks=true,urlcolor=linkblue,linkcolor=linkblue}

% ---- Spacing ----------------------------------------------------------------
\setlength{\parindent}{0pt}
\pagestyle{empty}

% ---- Section headings: small-caps + full-width rule (MIT CV style) ----------
\titleformat{\section}{\large\scshape\bfseries}{}{0pt}{}[\vspace{-6pt}\rule{\linewidth}{0.8pt}]
\titlespacing{\section}{0pt}{3pt}{1pt}

% ---- Helper macros ----------------------------------------------------------
% Single-line role/education header: bold title (left), location + dates (right).
\newcommand{\role}[3]{\textbf{#1}\hfill\textit{#2~$\cdot$~#3}\par\vspace{1pt}}
\newcommand{\edu}[3]{\textbf{#1}\hfill\textit{#3}\\\textit{#2}\par\vspace{1pt}}
% Project one-liner: linked name + description.
\newcommand{\project}[3]{%
  \item \href{#2}{\textbf{#1}} — #3%
}
\newcommand{\bullets}{\begin{itemize}[leftmargin=1.4em,nosep,topsep=1pt,partopsep=0pt,itemsep=1.5pt,parsep=0pt]}
\newcommand{\bulletsend}{\end{itemize}}
% Two-line entry (classic one-column / "MIT" résumé style, per source/cvs/sample-cv.png):
%   \entry{Bold organisation}{Location}      -> line 1, location right-aligned
%   \entryrole{Italic role / degree}{Dates}  -> line 2, dates right-aligned
\newcommand{\entry}[2]{\textbf{#1}\hfill\textit{#2}\par}
\newcommand{\entryrole}[2]{\textit{#1}\hfill\textit{#2}\par\vspace{1pt}}
