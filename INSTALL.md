# DreamTeam Install

## From clone (2 commands)

```powershell
git clone https://github.com/budagov/DreamTeam.git
cd DreamTeam

.\setup.ps1
# Linux/Mac: ./setup.sh
```

Setup installs dreamteam and creates project (`.dreamteam/`, `.cursor/`). Open folder in Cursor, run `/start` + goal, then `dreamteam run-next`.

## Separate project folder

To use DreamTeam for a different folder:

```powershell
cd C:\Projects\my-project
dreamteam new-project .
dreamteam run-next
```

## Project structure

```
project/
├── .dreamteam/   # db, memory, tasks, docs
├── .cursor/      # agents, rules
└── src/          # your code
```

## dreamteam not found

```
No module named dreamteam
```

Run `pip install -e .` from DreamTeam folder.

## Without install

Run from DreamTeam folder:

```powershell
cd C:\Projects\DreamTeam
python -m dreamteam new-project C:\Projects\my-project
```

Then set `DREAMTEAM_PROJECT` when working from another folder:

```powershell
$env:DREAMTEAM_PROJECT = "C:\Projects\my-project"
python -m dreamteam run-next
```
