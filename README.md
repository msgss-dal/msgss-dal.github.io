# msgss-dal.github.io
Website for the society.

## Grad seminar page

The seminar page (`/seminar/`) is generated from `talks.yaml`.
To add or edit a talk, change `talks.yaml` and push to `main`: a GitHub Action
runs `build.py` and commits the rebuilt `seminar/index.html`.
