"""P013-T009: documentary handoff, private project editor and verified activation."""
import copy
import difflib
import json
from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.context import IntakeContext
from harness_local.i18n import tr
from harness_local.core.engine.journal import JournalError
from harness_local.services.configuration import parse
from harness_local.services.configuration_setup import toml_document
from harness_local.services.project_registry import digest
from harness_local.storage.configuration import ConfigurationConflict
from harness_local.storage.models import (PlanningConversationRow as Conversation, PlanningProposalRow as Proposal,
    ProjectBootstrapRow as Bootstrap, ProjectImportRow as Import, ProjectPreparationOperationRow as Preparation)


class ProjectConfiguration:
    def __init__(self, runtime):
        self.runtime = runtime

    @property
    def repository(self):
        setup = self.runtime.setup
        if setup is None or setup.legacy:
            raise ConfigurationConflict('project_configuration_unavailable')
        return setup.repository

    def proposal(self, session, project_id):
        project = self.runtime.project(project_id)
        proposal = session.scalar(select(Proposal).join(Conversation, Conversation.id == Proposal.conversation_id)
            .where(Conversation.root == str(project.context.root), Proposal.kind == 'profile', Proposal.status == 'ACCEPTED'))
        if not proposal:
            raise ConfigurationConflict('accepted_profile_required')
        return proposal

    def check_candidate(self, project_id, data):
        project = self.runtime.project(project_id)
        with Session(self.runtime.engine) as session:
            proposal = self.proposal(session, project_id)
            candidate = json.loads(proposal.content)['candidate']
        if (data['project'] != {'id': project_id, 'root': str(project.context.root)}
                or data['profile_name'] != candidate['name'] or data['profile'] != candidate['profile']
                or data.get('provenance') != {'source': 'profile-proposal', 'sha256': proposal.proposal_sha256}):
            raise ConfigurationConflict('documentary_profile_changed')
        # T009 changes tool paths/command limits, never the admitted agent pair or policy.
        original = self.initial(project_id)
        if data['policy'] != original['policy'] or data['agents'] != original['agents']:
            raise ConfigurationConflict('intake_agent_policy_changed')
        if set(data['commands']['executables']) != {tool['name'] for tool in candidate['tools']}:
            raise ConfigurationConflict('profile_tools_changed')
        return data

    def initial(self, project_id):
        project = self.runtime.project(project_id)
        registrar = self.runtime.registry.registrar
        with Session(self.runtime.engine) as session:
            proposal = self.proposal(session, project_id)
            candidate = json.loads(proposal.content)['candidate']
        state = self.repository.read('global')
        if state['status'] != 'READY' or not state['active']:
            raise ConfigurationConflict('active_global_configuration_required')
        row = self.runtime.registry.repository.get(project_id)['row']
        declarations = ({role: registrar.presets[choice['preset_id']][1]
                         for role, choice in row['agent_selection'].items()} if row.get('agent_selection') else registrar.agents)
        from harness_local.services.local_config import CLI_KEYS, TOOL_KEYS
        agents = {role: {key: value for key, value in asdict(declaration).items()
                        if key in (*CLI_KEYS, *TOOL_KEYS, 'provider') and value is not None
                        and not (key == 'executable' and not value)} for role, declaration in declarations.items()}
        # CLI declarations use tuple pairs, while the editor accepts JSON/TOML tables and arrays.
        for role in agents:
            agents[role]['environment'] = dict(declarations[role].environment)
            if 'executable' in agents[role]:
                agents[role]['executable'] = list(agents[role]['executable'])
            for key in ('tools', 'allowed_tools', 'grantable_tools'):
                if key in agents[role]:
                    if role == 'reviewer' or declarations[role].provider != 'claude':
                        agents[role].pop(key)
                    else:
                        agents[role][key] = list(agents[role][key])
        agents['reviewer'].update(model=project.context.policy.reviewer_model, effort=project.context.policy.reviewer_effort)
        local = candidate.get('preparation_plan', {}).get('local_paths', [])
        base = local[0].removesuffix('/**') if local else '.harness-preparation'
        return {'format': 'project-config-1', 'project': {'id': project_id, 'root': str(project.context.root)},
                'global': {key: state['active'][key] for key in ('revision', 'sha256')},
                'profile_name': candidate['name'], 'profile': copy.deepcopy(candidate['profile']),
                'commands': {'executables': {tool['name']: '' for tool in candidate['tools']},
                    'environment': {'HOME': str(project.context.root / base / 'home'),
                                    'TMPDIR': str(project.context.root / base / 'tmp')},
                    'authorize_profile_commands': True, 'max_timeout_seconds': 1800, 'max_output_bytes': 1048576},
                'policy': row['policy'], 'agents': agents,
                'provenance': {'source': 'profile-proposal', 'sha256': proposal.proposal_sha256}}

    def candidate(self, project_id, *, text=None, form=None, validated=True):
        if (text is None) == (form is None):
            raise ValueError(tr('setup.invalid'))
        text = toml_document(form) if form is not None else text
        data = parse(text, 'project:' + project_id, validated=validated)
        if validated:
            self.check_candidate(project_id, data)
        else:
            commands = data.get('commands', {})
            if (not isinstance(data.get('profile_name'), str)
                    or not isinstance(commands.get('executables'), dict)
                    or not isinstance(commands.get('environment'), dict)
                    or any(not isinstance(value, str) for value in (
                        *commands['executables'].values(), *commands['environment'].values()))):
                raise ValueError(tr('setup.invalid'))
        return text

    def read(self, project_id):
        project = self.runtime.project(project_id)
        scope = 'project:' + project_id
        state = self.repository.read(scope)
        text = self.repository.document(scope, state['saved']['revision']) if state['saved'] else None
        with Session(self.runtime.engine) as session:
            proposal = self.proposal(session, project_id)
            payload = json.loads(proposal.content)
            documentary = session.scalar(select(Bootstrap).where(Bootstrap.root == str(project.context.root)))
            if documentary is None:
                documentary = session.scalar(select(Import).where(Import.root == str(project.context.root)))
        stage = 'PROFILE_PROPOSED'
        if documentary:
            stage = ('PREPARATION_REQUIRED' if state['saved'] else 'DOCUMENTS_COMMITTED') if documentary.status == 'COMPLETED' else 'PROFILE_PROPOSED'
        prepared = self.runtime.preparation.read(project_id)
        if prepared['prepared']:
            stage = 'READY_TO_ACTIVATE'
        if state['active'] and not isinstance(project.context, IntakeContext):
            try:
                receipt = self.active_receipt(project_id, state['active'])
                if state['status'] != 'READY' or not receipt:
                    raise ConfigurationConflict('project_preparation_changed')
                self.runtime.preparation.generic().verify_configuration(project, receipt, active=True)
                stage = 'ACTIVE'
            except (ValueError, OSError, JournalError):
                stage = 'PREPARATION_REQUIRED'
        return {**state, 'configuration_state': stage, 'text': text,
                'form': parse(text, scope, validated=False) if text else self.initial(project_id),
                'proposal_id': proposal.id, 'proposal_sha256': proposal.proposal_sha256,
                'profile': payload, 'preparation': prepared}

    def verify(self, session, scope, data):
        project = self.runtime.project(scope[8:])
        row = session.scalar(select(Preparation).where(Preparation.project_id == project.id,
            Preparation.status == 'COMPLETED').order_by(Preparation.created_at.desc(), Preparation.id.desc()).limit(1))
        if not row or not row.receipt or row.plan.get('configuration_data') != data:
            raise ConfigurationConflict('project_preparation_required')
        try:
            self.runtime.preparation.generic().verify_configuration(project, row.receipt)
        except (ValueError, OSError, JournalError):
            raise ConfigurationConflict('project_preparation_changed') from None
        # Activation requires the exact prepared HEAD and a clean index/worktree. Later tasks may evolve ordinary code.
        _, git = self.runtime.preparation.writer(project)
        if (git.text('rev-parse', 'HEAD') != row.receipt['commit']
                or git.run('status', '--porcelain=v1', '--untracked-files=all').strip()):
            raise ConfigurationConflict('prepared_head_changed')
        self.check_candidate(project.id, data)
        # Compose before the transaction can publish authority, without installing or running clients.
        self.runtime.registry.registrar.compose_profile(project, data, row.receipt, row.receipt['configuration'])
        return {'operation_id': row.id, 'receipt_sha256': digest(row.receipt), 'commit': row.receipt['commit']}

    def activation_preview(self, references, *, reason):
        preview = self.repository.activation_preview(references, reason=reason)
        changes = []
        for reference in preview['references']:
            scope = reference['scope']
            text = self.repository.document(scope, reference['revision'])
            previous = reference['previous']
            before = self.repository.document(scope, previous['revision']) if previous else ''
            changes.append({'scope': scope, 'sha256': reference['sha256'], 'text': text,
                'diff': ''.join(difflib.unified_diff(before.splitlines(True), text.splitlines(True),
                    fromfile='active', tofile='candidate'))})
        # Diffs are a derived view of the immutable before/after hashes already sealed in the preview.
        return {**preview, 'changes': changes}

    def active_receipt(self, project_id, reference):
        with Session(self.runtime.engine) as session:
            return session.scalar(select(Preparation.receipt).where(Preparation.project_id == project_id,
                Preparation.status == 'COMPLETED',
                Preparation.receipt['configuration']['sha256'].as_string() == reference['sha256'])
                .order_by(Preparation.created_at.desc(), Preparation.id.desc()).limit(1))

    def install_active(self, project):
        state = self.repository.read('project:' + project.id)
        if not state['active']:
            return project
        if state['status'] != 'READY':
            raise ConfigurationConflict('project_configuration_changed')
        data = parse(self.repository.document(state['scope'], state['active']['revision']), state['scope'])
        receipt = self.active_receipt(project.id, state['active'])
        if not receipt or receipt['configuration'] != state['active']:
            raise ConfigurationConflict('project_preparation_required')
        try:
            self.runtime.preparation.generic().verify_configuration(project, receipt, active=True)
        except (ValueError, OSError, JournalError):
            raise ConfigurationConflict('project_preparation_changed') from None
        composed = self.runtime.registry.registrar.compose_profile(project, data, receipt, state['active'])
        self.runtime.registry.registrar._receipts[project.context.root] = receipt
        return self.runtime.registry.registrar.install(composed)
