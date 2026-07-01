% =============================================================================
% coverletter.cls — cover-letter class matching resume.cls (same fonts, margins,
% link colour). Engine: pdfLaTeX. Self-contained: only standard TeX Live packages.
%
% Usage (see applications/_templates/cover-letter.tex):
%   \documentclass[11pt,a4paper]{coverletter}
%   \senderblock{Name}{Title}{Location \textbar\ email \textbar\ portfolio}
%   \begin{document}
%   \recipient{Company}{Hiring Team}{Location}   % any field may be empty
%   \opening{Dear Hiring Team,}
%   ... body paragraphs ...
%   \closing{Sincerely,}{Name}
%   \end{document}
% =============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{coverletter}[2026/06/16 Radheem cover-letter class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

% ---- Packages (mirror resume.cls) -------------------------------------------
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
% English main; \selectlanguage{ngerman} switches the appended German version
% (hyphenation, and \today → e.g. "16. Juni 2026").
\RequirePackage[main=english,ngerman]{babel}
\RequirePackage{lmodern}
\RequirePackage[top=1.6cm,bottom=1.6cm,left=1.9cm,right=1.9cm]{geometry}
\RequirePackage{microtype}
\RequirePackage{xcolor}
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{enumitem}

\definecolor{linkblue}{RGB}{0,84,159}
\hypersetup{colorlinks=true,urlcolor=linkblue,linkcolor=linkblue}

\newcommand{\bullets}{\begin{itemize}[leftmargin=1.4em,nosep,topsep=2pt,partopsep=0pt,itemsep=3pt,parsep=0pt]}
\newcommand{\bulletsend}{\end{itemize}}

\setlength{\parindent}{0pt}
\setlength{\parskip}{8pt}
\pagestyle{empty}

% ---- Sender block: defines the letterhead, printed by \maketitle-style macro -
% \senderblock{Name}{Title}{Contact line}
\newcommand{\@cvname}{}
\newcommand{\@cvtitle}{}
\newcommand{\@cvcontact}{}
\newcommand{\senderblock}[3]{%
  \renewcommand{\@cvname}{#1}%
  \renewcommand{\@cvtitle}{#2}%
  \renewcommand{\@cvcontact}{#3}%
}

% Letterhead printed at \begin{document} via \recipient (keeps order simple).
\newcommand{\printletterhead}{%
  \begin{center}
    {\huge\bfseries \@cvname}\\[3pt]
    {\large \@cvtitle}\\[6pt]
    \small \@cvcontact
  \end{center}
  \vspace{6pt}
  \hrule
  \vspace{10pt}
}

% \recipient{Company}{Attn / team}{Location} — prints letterhead, date, address.
\newcommand{\recipient}[3]{%
  \printletterhead
  {\raggedleft \today \par}
  \vspace{4pt}
  \textbf{#1}\\
  \ifx\relax#2\relax\else #2\\\fi
  \ifx\relax#3\relax\else #3\\\fi
  \vspace{6pt}
}

% \opening{Dear ...,}
\newcommand{\opening}[1]{#1\par}

% \closing{Sincerely,}{Name}
\newcommand{\closing}[2]{%
  \vspace{6pt}
  #1\\[24pt]
  \textbf{#2}\par
}
