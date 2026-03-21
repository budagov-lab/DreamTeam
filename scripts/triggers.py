#!/usr/bin/env python3
"""Shared trigger constants for task counter and update-task. Learning (10), Researcher (20), Meta Planner (50), Auditor (200)."""

TRIGGER_RESEARCHER = 20
TRIGGER_META_PLANNER = 50
TRIGGER_AUDITOR = 200
TRIGGER_LEARNING = 10
# Return BATCH_DONE to switch Left↔Right before context overflow. Source of truth: update-task done output.
TRIGGER_BATCH_SWITCH = 15
