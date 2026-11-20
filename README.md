# dueline

Track your course assignment deadlines with natural-language due dates —
locally, with zero dependencies.

## Motivation

Coursework is scattered across Canvas, external sites, and email. `dueline`
gives you one local ledger: add an assignment in plain words, and it sorts
everything by urgency.

## Installation

pip install dueline

## Usage

dueline add "CS1302 project" --due "next sunday 11:59 pm" --course CS1302
dueline add "线性代数作业" --due "11月22日 23:59" --course MA1001
dueline list
dueline done "CS1302 project"
dueline due --days 3
