"""Codec JSON versionado, sin pickle ni dependencias de almacenamiento."""

from dataclasses import asdict
import json
from pathlib import Path

from harness_local.core.engine.acceptance import AcceptanceDecision
from harness_local.core.engine.context import Command, EnginePolicy, ProjectContext, ProjectProfile
from harness_local.core.engine.contracts import (
    AgentRequest, AgentResult, Attempt, OperationalStop, RunHistory, Selection, freeze,
)
from harness_local.core.engine.evidence import ContentEvidence, PathPolicyResult
from harness_local.core.engine.review import ReviewCycle
from harness_local.core.engine.validation import CommandResult, ValidationEntry, ValidationReport


def restore_command(data: dict) -> Command:
    return Command(tuple(data["argv"]), data["cwd"], tuple(tuple(item) for item in data["environment"]),
                   data["timeout_seconds"])


def restore_context(snapshot: str) -> ProjectContext:
    data = json.loads(snapshot)
    profile = data["profile"]
    for key in ("preparation", "validations"):
        profile[key] = tuple(restore_command(item) for item in profile[key])
    profile["allowed_command_prefixes"] = tuple(tuple(item) for item in profile["allowed_command_prefixes"])
    for key in ("protected_paths", "sensitive_paths", "sensitive_allowlist", "formatter_argv", "formatter_paths"):
        profile[key] = tuple(profile[key])
    policy = data["policy"]
    for key in ("executor_models", "executor_efforts"):
        policy[key] = tuple(policy[key])
    return ProjectContext(Path(data["root"]), ProjectProfile(**profile), EnginePolicy(**policy),
                          data["next_steps_file"], data["state_file"])


def restore_request(data: dict) -> AgentRequest:
    return AgentRequest(**{**data, "selection": Selection(**data["selection"])})


def _evidence(data: dict) -> ContentEvidence:
    return ContentEvidence(**{**data, "changed_paths": tuple(data["changed_paths"])})


def dump_history(history: RunHistory) -> str:
    return freeze({"format": 1, "history": asdict(history)})


def load_history(snapshot: str) -> RunHistory:
    value = json.loads(snapshot)
    if value["format"] != 1:
        raise ValueError("Unknown managed history format")
    data = value["history"]
    data["attempts"] = tuple(Attempt(restore_request(item["request"]), AgentResult(**item["result"]))
                             for item in data["attempts"])
    cycles = []
    for item in data["cycles"]:
        report = item["validation"]
        entries = tuple(ValidationEntry(restore_command(entry["command"]) if entry["command"] else None,
                                       entry["requested"], CommandResult(**entry["result"]))
                        for entry in report["entries"])
        cycles.append(ReviewCycle(item["number"], _evidence(item["evidence"]),
                                  PathPolicyResult(tuple(item["policy"]["violations"])),
                                  ValidationReport(_evidence(report["evidence"]), entries), item["review_json"],
                                  _evidence(item["before_execution"]) if item["before_execution"] else None,
                                  item["permission_denials_json"]))
    data["cycles"] = tuple(cycles)
    data["preparation_json"] = tuple(data["preparation_json"])
    data["stop"] = OperationalStop(**data["stop"]) if data["stop"] else None
    data["stops"] = tuple(OperationalStop(**item) for item in data["stops"])
    if data["acceptance"]:
        item = data["acceptance"]
        data["acceptance"] = AcceptanceDecision(item["eligible"], tuple(item["reasons"]), _evidence(item["evidence"]))
    return RunHistory(**data)
