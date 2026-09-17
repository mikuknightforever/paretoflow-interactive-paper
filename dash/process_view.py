"""Read-only views of recorded sampler decisions; no model execution in callbacks."""
import json
import math
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html, no_update


TRACE_PATH = Path(__file__).resolve().parent / 'data' / 'process_trace.json'
STAGES = ('Generate', 'Pool', 'Filter', 'Select', 'Archive')
BLUE = '#167b9b'
PURPLE = '#6950a1'
AMBER = '#ae741b'
GRAY = '#b5bdc9'
GRAPH_CONFIG = {'displayModeBar': False, 'responsive': True}


@lru_cache(maxsize=2)
def load_trace(path=TRACE_PATH):
    """Load static evidence once per process, without importing torch."""
    with Path(path).open(encoding='utf-8') as handle:
        trace = json.load(handle)
    if trace.get('schema_version') != 1:
        raise ValueError('Unsupported recorded process trace schema')
    if not trace.get('modes') or not trace.get('directions'):
        raise ValueError('Recorded process trace has no configurations or directions')
    return trace


def select_record(trace, mode, step, direction):
    """Return a frame and its receiving-direction record, without mutating data."""
    if mode not in trace['modes']:
        raise ValueError(f'Unknown recorded configuration: {mode}')
    if int(direction) not in trace['directions']:
        raise ValueError(f'Direction {direction} was not recorded')
    frames = trace['modes'][mode]['frames']
    step = int(step)
    if not 0 <= step < len(frames) or frames[step]['step'] != step:
        raise ValueError(f'Step {step} was not recorded')
    frame = frames[step]
    for record in frame['directions']:
        if record['id'] == int(direction):
            return frame, record
    raise ValueError(f'Direction {direction} is missing from step {step}')


def _integer(value, default):
    try:
        if isinstance(value, bool) or isinstance(value, float) and not value.is_integer():
            return default
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def normalize_process_context(trace, mode=None, step=None, direction=None, stage='Filter', candidate=None):
    """Validate URL/UI values against available records, without executing models."""
    default_mode = 'guided' if 'guided' in trace['modes'] else next(iter(trace['modes']))
    mode = mode if isinstance(mode, str) and mode in trace['modes'] else default_mode
    frames = trace['modes'][mode]['frames']
    default_step = len(frames) - 1
    step = _integer(step, default_step)
    if not 0 <= step < len(frames):
        step = default_step
    default_direction = 200 if 200 in trace['directions'] else trace['directions'][0]
    direction = _integer(direction, default_direction)
    if direction not in trace['directions']:
        direction = default_direction
    _, record = select_record(trace, mode, step, direction)
    stage = stage if stage in STAGES else 'Generate'
    if not record['candidates']:
        stage = None
    candidate = _integer(candidate, None)
    if candidate not in {item['id'] for item in record['candidates']}:
        candidate = None
    return {'mode': mode, 'step': step, 'direction': direction, 'stage': stage, 'candidate': candidate}


def parse_process_query(trace, search):
    """Read a shared record link. Invalid and missing fields fall back safely."""
    try:
        query = parse_qs(str(search or '').lstrip('?'), keep_blank_values=True, max_num_fields=32)
    except ValueError:
        query = {}
    def first(name, default=None):
        values = query.get(name)
        return values[0] if values else default
    return normalize_process_context(trace, first('mode'), first('step'), first('direction'),
                                     first('stage', 'Filter'), first('candidate'))


def _record_key(context):
    return f"{context['mode']}:{context['step']}:{context['direction']}"


def reduce_process_context(trace, previous, values, triggered):
    """One state reducer for link restoration and all user interactions."""
    changed = set(triggered)
    if not previous or 'process-location.search' in changed:
        return parse_process_query(trace, values.get('process-location.search'))
    context = normalize_process_context(
        trace, values.get('process-mode.value'), values.get('process-step.value'),
        values.get('process-direction.value'), values.get('process-stage.value'),
    )
    if 'process-prev.n_clicks' in changed or 'process-next.n_clicks' in changed:
        delta = -1 if 'process-prev.n_clicks' in changed else 1
        context['step'] = min(len(trace['modes'][context['mode']]['frames']) - 1, max(0, context['step'] + delta))
        context = normalize_process_context(trace, **context)
    same_record = _record_key(context) == _record_key(previous)
    if same_record:
        context['candidate'] = previous.get('candidate')
        if 'process-objective.clickData' in changed:
            click = values.get('process-objective.clickData') or {}
            points = click.get('points') or []
            data = points[0].get('customdata') if points else None
            if isinstance(data, (list, tuple)) and data and (len(data) < 4 or data[3] == _record_key(context)):
                context['candidate'] = data[0]
        elif 'process-table.active_cell' in changed:
            active = values.get('process-table.active_cell') or {}
            rows = values.get('process-table.derived_virtual_data') or []
            identifier = active.get('row_id')
            row_index = active.get('row', -1)
            row = next((row for row in rows if row.get('id') == identifier), None)
            if row is None and isinstance(row_index, int) and 0 <= row_index < len(rows):
                row = rows[row_index]
            if row and row.get('_record', _record_key(context)) == _record_key(context):
                context['candidate'] = row['id']
    return normalize_process_context(trace, **context)


def _figure(height=250):
    figure = go.Figure()
    figure.update_layout(
        template='plotly_white', height=height,
        margin=dict(l=56, r=15, t=35, b=43),
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=11, color='#24364a'),
        legend=dict(orientation='h', y=1.19, font=dict(size=10)),
        dragmode=False,
    )
    figure.update_xaxes(fixedrange=True)
    figure.update_yaxes(fixedrange=True)
    return figure


def _finite_angle(value):
    return value is not None and math.isfinite(value)


def _invalid_angles(record):
    return (not _finite_angle(record['half_angle_deg'])
            or any(not _finite_angle(item['angle_deg']) for item in record['candidates']))


def _candidate_status(candidate, record):
    valid = _finite_angle(candidate['angle_deg']) and _finite_angle(record['half_angle_deg'])
    if candidate['fallback'] and not valid:
        return 'Numerical safeguard'
    if candidate['fallback']:
        return 'Fallback retained'
    if not valid:
        return 'Excluded (invalid angle)'
    return 'Inside cone' if candidate['admitted'] else 'Excluded'


def _visible_candidates(record, stage):
    candidates = record['candidates']
    if stage == 'Generate':
        return [item for item in candidates if item['source_direction'] == record['id']]
    return candidates


def _stage_text(frame, record, stage, visible):
    if not record['candidates']:
        if frame['phase'] == 'initial':
            return ('Initial state', 'Sampling starts from noise and an existing clean-design archive. '
                    'No offspring have been generated or selected at this record.')
        return ('Flow transport', 'The noisy stream is moving, while the saved clean design stays unchanged. '
                'Candidate generation and selection have not started at this record.')
    admitted = sum(item['admitted'] for item in record['candidates'])
    fallback = sum(item['fallback'] for item in record['candidates'])
    chosen = next(item for item in record['candidates'] if item['selected'])
    if stage == 'Generate':
        return ('Generate offspring', f"These {len(visible)} recorded proposals originate from direction "
                f"{record['id']}. Each has a noisy stream state and a predicted clean endpoint.")
    if stage == 'Pool':
        return ('Share neighboring proposals', f"Direction {record['id']} receives "
                f"{len(record['candidates'])} proposals from {len(record['neighbors'])} neighboring streams, "
                'including itself. Candidate numbers identify positions in this record only.')
    if stage == 'Filter':
        threshold = f"{record['half_angle_deg']:.3f}°" if _finite_angle(record['half_angle_deg']) else 'unavailable'
        text = f"{admitted} of {len(record['candidates'])} candidates are admitted. The half-angle is {threshold}. "
        if not _invalid_angles(record):
            text += (f'{fallback} candidate is retained outside the cone as the smallest-angle fallback.'
                     if fallback else 'The smallest-angle safeguard requires no outside-cone fallback here.')
        return 'Apply the recorded angle filter', text
    if stage == 'Select':
        return ('Choose the next stream state', f"Candidate {chosen['id']} has the highest weighted score "
                f"among admitted candidates ({chosen['weighted_score']:.5f}; higher is better). "
                'Its noisy state becomes the next state. Excluded candidates cannot win.')
    return ('Update the saved clean design' if record['updated'] else 'Retain the saved clean design',
            f"Candidate {chosen['id']} is selected for the stream, "
            + ('and its predicted clean endpoint improves the archive score, so the archive is updated.'
               if record['updated'] else 'but its predicted clean endpoint does not improve the archive score. '
               'The previous archive design is retained.'))


def render_process(trace, mode='guided', step=160, direction=200, stage='Filter', candidate_id=None):
    """Pure renderer: figures, table rows and copy for one actual recorded decision."""
    if stage is None:
        stage = 'Generate'
    if stage not in STAGES:
        raise ValueError(f'Unknown process stage: {stage}')
    frame, record = select_record(trace, mode, step, direction)
    visible = _visible_candidates(record, stage)
    candidate = next((item for item in record['candidates'] if item['id'] == candidate_id), None)
    if candidate is None:
        candidate = next((item for item in visible if item['selected']), visible[0] if visible else None)
    selected_id = candidate['id'] if candidate else None
    candidate_visible = candidate is not None and any(item['id'] == candidate['id'] for item in visible)
    record_key = _record_key({'mode': mode, 'step': int(step), 'direction': int(direction)})
    chart = _figure()
    rows = []
    filtering_visible = stage in ('Filter', 'Select', 'Archive')
    for item in visible:
        rows.append({
            'id': item['id'], 'candidate': item['id'], 'source': item['source_direction'],
            'offspring': item['offspring'], 'f1': item['predicted'][0], 'f2': item['predicted'][1],
            'angle': item['angle_deg'], 'filter': _candidate_status(item, record),
            'safeguard': 'Yes' if item['id'] == record.get('safeguard_id') else '—',
            'score': item['weighted_score'], 'chosen': 'Yes' if item['selected'] else '—',
            '_record': record_key,
        })
    groups = [('Proposals', visible, BLUE)]
    if filtering_visible:
        groups = [
            ('Excluded', [item for item in visible if not item['admitted']], GRAY),
            ('Inside cone', [item for item in visible if item['admitted'] and not item['fallback']], BLUE),
            ('Fallback retained', [item for item in visible if _candidate_status(item, record) == 'Fallback retained'], AMBER),
            ('Recorded numerical safeguard', [item for item in visible if _candidate_status(item, record) == 'Numerical safeguard'], AMBER),
        ]
    for name, group, color in groups:
        if not group:
            continue
        chart.add_trace(go.Scatter(
            x=[item['predicted'][0] for item in group], y=[item['predicted'][1] for item in group],
            mode='markers', name=name, marker=dict(size=9, color=color, opacity=.82),
            customdata=[[item['id'], item['source_direction'], item['offspring'], record_key] for item in group],
            hovertemplate='Candidate %{customdata[0]} · source %{customdata[1]} / offspring %{customdata[2]}'
                          '<br>Predicted f₁ %{x:.4f}<br>Predicted f₂ %{y:.4f}<extra></extra>',
        ))
    if candidate_visible:
        chart.add_trace(go.Scatter(
            x=[candidate['predicted'][0]], y=[candidate['predicted'][1]],
            customdata=[[candidate['id'], candidate['source_direction'], candidate['offspring'], record_key]],
            mode='markers', name='Inspecting', marker=dict(size=17, color=PURPLE, symbol='circle-open', line=dict(width=2)),
            hovertemplate='Inspecting candidate %{customdata[0]}<extra></extra>',
        ))
    if stage in ('Select', 'Archive'):
        chosen = next((item for item in visible if item['selected']), None)
        if chosen:
            chart.add_trace(go.Scatter(
                x=[chosen['predicted'][0]], y=[chosen['predicted'][1]],
                customdata=[[chosen['id'], chosen['source_direction'], chosen['offspring'], record_key]],
                mode='markers', name='Selected for stream', marker=dict(size=13, color=PURPLE, symbol='star'),
                hovertemplate='Selected candidate %{customdata[0]}<extra></extra>',
            ))
    if not visible:
        chart.add_annotation(x=.5, y=.5, xref='paper', yref='paper', showarrow=False,
                             text='No candidate pool at this step.<br>Inspect the recorded stream state below.',
                             font=dict(color='#677589', size=12))
        chart.update_xaxes(range=[0, 1])
        chart.update_yaxes(range=[0, 1])
    chart.update_xaxes(title='Proxy-predicted objective f₁ ↓')
    chart.update_yaxes(title='Proxy-predicted objective f₂ ↓')

    design, state = _figure(215), _figure(215)
    dims = list(range(1, 31))
    for key, label, color, dash in (
        ('archive_before', 'Archive before', GRAY, 'dot'),
        ('archive_after', 'Archive after', PURPLE, 'solid'),
    ):
        design.add_trace(go.Scatter(x=dims, y=record[key], mode='lines', name=label,
                                   line=dict(color=color, width=2, dash=dash),
                                   hovertemplate='x%{x} = %{y:.5f}<extra>%{fullData.name}</extra>'))
    if candidate:
        design.add_trace(go.Scatter(x=dims, y=candidate['design'], mode='lines+markers',
                                   name=f"Candidate {selected_id}", marker=dict(size=3),
                                   line=dict(color=BLUE, width=2, dash='dash'),
                                   hovertemplate='x%{x} = %{y:.5f}<extra>%{fullData.name}</extra>'))
    for key, label, color, dash in (
        ('state_before', 'Stream before', GRAY, 'dot'),
        ('state_after', 'Stream after', PURPLE, 'solid'),
    ):
        state.add_trace(go.Scatter(x=dims, y=record[key], mode='lines', name=label,
                                  line=dict(color=color, width=2, dash=dash),
                                  hovertemplate='State x%{x} = %{y:.5f}<extra>%{fullData.name}</extra>'))
    if candidate:
        state.add_trace(go.Scatter(x=dims, y=candidate['state'], mode='lines+markers',
                                  name=f"Candidate {selected_id}", marker=dict(size=3),
                                  line=dict(color=BLUE, width=2, dash='dash'),
                                  hovertemplate='State x%{x} = %{y:.5f}<extra>%{fullData.name}</extra>'))
    for figure in (design, state):
        figure.update_xaxes(title='Design variable', range=[.5, 30.5], dtick=5)
    design.update_yaxes(title='Original units', range=[-.04, 1.04])
    state.update_yaxes(title='Standardized units')
    heading, description = _stage_text(frame, record, stage, visible)
    if record['candidates'] and _invalid_angles(record):
        description += (f" This original run contains an invalid angle calculation. The recorded mask and "
                        f"numerical safeguard choice (candidate {record.get('safeguard_id', 'unavailable')}) are preserved; "
                        'this choice must not be interpreted as the smallest valid angle.')
    delta = sum((after - before) ** 2 for before, after in zip(record['state_before'], record['state_after'])) ** .5
    inspection = (f"Inspecting candidate {selected_id} · source direction {candidate['source_direction']} · "
                  f"offspring {candidate['offspring']} · {_candidate_status(candidate, record).lower()} · "
                  + ('selected for the next stream state' if candidate['selected'] else 'not selected for the next stream state')) if candidate else 'No candidate selected; the charts compare the recorded stream and archive states.'
    if candidate is not None and not candidate_visible:
        inspection += (f". This candidate is not shown in the {stage} plot or table, which only show offspring "
                       f"from direction {record['id']}. Its recorded design and state remain selected below.")
    return {
        'objective': chart, 'design': design, 'state': state, 'rows': rows,
        'heading': heading, 'description': description, 'inspection': inspection,
        'candidate_id': selected_id,
        'candidate_visible': candidate_visible,
        'has_candidates': bool(record['candidates']),
        'time_label': f"Step {frame['step']} / {len(trace['modes'][mode]['frames']) - 1} · t = {frame['time']:.3f}",
        'stats': [f"Direction {record['id']} · weights ({record['weights'][0]:.3f}, {record['weights'][1]:.3f})",
                  f"Stream change ‖Δx‖ = {delta:.4f}",
                  'Archive updated' if record['updated'] else 'Archive retained'],
        'archive_note': f"Archive score: {record['archive_score_before']:.5f} → {record['archive_score_after']:.5f} (higher is better).",
    }


def make_process_panel(server):
    """Mount the read-only process explorer at /process/ and return its Dash app."""
    trace = load_trace()
    app = Dash('pareto_process', server=server, url_base_pathname='/process/',
               assets_folder=str(Path(__file__).resolve().parent / 'assets'),
               title='ParetoFlow · Recorded sampling process')
    modes = trace['modes']
    default_mode = 'guided' if 'guided' in modes else next(iter(modes))
    default_step = len(modes[default_mode]['frames']) - 1
    default_direction = 200 if 200 in trace['directions'] else trace['directions'][0]
    app.layout = html.Div([
        dcc.Location(id='process-location', refresh=False),
        dcc.Store(id='process-context'), dcc.Download(id='process-download'),
        html.Div([
            html.Div([html.Span('RECORDED LOCAL EXPERIMENT', className='process-kind'),
                      html.H2('Inside one sampling step')]),
            html.Button('Download record', id='process-export', n_clicks=0, className='process-secondary'),
        ], className='process-heading'),
        html.Div([
            html.Div([html.Label('Recorded configuration', htmlFor='process-mode'),
                      dcc.Dropdown(id='process-mode', options=[{'label': data['label'], 'value': name} for name, data in modes.items()],
                                   value=default_mode, clearable=False)], className='process-config'),
            html.Div([html.Label('Receiving direction', htmlFor='process-direction'),
                      dcc.Dropdown(id='process-direction', options=[{'label': f'Direction {value}', 'value': value} for value in trace['directions']],
                                   value=default_direction, clearable=False)], className='process-direction'),
        ], className='process-controls'),
        html.Div([
            html.Div([html.Button('← Previous', id='process-prev', n_clicks=0),
                      html.Button('Next →', id='process-next', n_clicks=0),
                      html.Span(id='process-time')], className='process-stepper'),
            dcc.Slider(id='process-step', min=0, max=default_step, step=1, value=default_step,
                       marks={0: '0.00', 80: '0.50', 128: '0.80', 160: '1.00'}, updatemode='mouseup'),
        ], className='process-timeline'),
        dcc.RadioItems(id='process-stage', options=[{'label': value, 'value': value} for value in STAGES],
                       value='Filter', inline=True, className='process-stages'),
        html.Div([html.Strong(id='process-stage-heading'), html.P(id='process-stage-description'),
                  html.Div(id='process-stats', className='process-stats')], className='process-summary'),
        dcc.Graph(id='process-objective', config=GRAPH_CONFIG),
        html.P('These are predicted objectives in original units. The angle filter uses standardized score vectors, '
               'so its cone is not drawn on this chart.', className='process-caption'),
        html.Div([html.Strong('Recorded candidates'), html.Span(id='process-candidate-hint')], className='process-table-heading'),
        dash_table.DataTable(
            id='process-table', data=[], columns=[
                {'name': 'Candidate', 'id': 'candidate', 'type': 'numeric'},
                {'name': 'Source', 'id': 'source', 'type': 'numeric'},
                {'name': 'Offspring', 'id': 'offspring', 'type': 'numeric'},
                {'name': 'Pred. f₁ ↓', 'id': 'f1', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                {'name': 'Pred. f₂ ↓', 'id': 'f2', 'type': 'numeric', 'format': {'specifier': '.4f'}},
                {'name': 'Angle (°)', 'id': 'angle', 'type': 'numeric', 'format': {'specifier': '.3f', 'nully': 'Unavailable'}},
                {'name': 'Filter result', 'id': 'filter'},
                {'name': 'Safeguard', 'id': 'safeguard'},
                {'name': 'Score ↑', 'id': 'score', 'type': 'numeric', 'format': {'specifier': '.5f'}},
                {'name': 'Selected', 'id': 'chosen'},
            ],
            sort_action='native', page_action='none', fixed_rows={'headers': True},
            style_table={'height': '200px', 'overflowY': 'auto', 'overflowX': 'auto'},
            style_cell={'fontFamily': 'Arial, sans-serif', 'fontSize': 11, 'padding': '7px 8px',
                        'color': '#24364a', 'textAlign': 'right', 'minWidth': '62px'},
            style_header={'backgroundColor': '#f0f4f8', 'fontWeight': 'bold', 'border': '1px solid #e0e6ed'},
        ),
        html.P(id='process-inspection', className='process-inspection'),
        html.Div([
            html.Section([html.H3('Predicted clean design'), dcc.Graph(id='process-design', config=GRAPH_CONFIG),
                          html.P('All 30 variables in original [0,1] units. The archive stores clean endpoints.', className='process-caption')]),
            html.Section([html.H3('Noisy stream state'), dcc.Graph(id='process-state', config=GRAPH_CONFIG),
                          html.P('Standardized coordinates, with noise still present. These are not clean feasible designs.', className='process-caption')]),
        ], className='process-linked'),
        html.P(id='process-archive-note', className='process-caption'),
        html.Details([
            html.Summary('Source and interpretation'),
            html.P('Recorded from the local 30-variable ZDT2 experiment using the saved model checkpoint and '
                   f"sampling seed {trace.get('provenance', {}).get('sampling_seed', 'recorded in the download')}. "
                   'Five receiving directions are available. All points, masks and scores are recorded sampler values; '
                   'this is separate from the constructed neighboring-selection illustration.'),
            html.P('Filtering and weighted scoring use negative standardized proxy losses. The sampler retains one '
                   'candidate through its angle safeguard, even when none passes the cone test. For finite angles, '
                   'an outside-cone survivor is labeled as a fallback. If the original angle calculation is invalid, '
                   'the actual recorded mask and safeguard choice are preserved and labeled separately; unavailable '
                   'angles are not replaced with invented values. Selecting a noisy state '
                   'does not guarantee that the best saved clean design improves. Candidate numbers are local to '
                   'each step and receiving direction, not permanent identities across time.'),
            html.P('This small local run explains the mechanism. It is not a reproduction of the paper’s benchmark evaluation. '
                   'The record download includes provenance and the complete vectors for this direction and step.'),
        ], className='process-source'),
    ], className='process-panel')

    @app.callback(
        Output('process-mode', 'value'), Output('process-step', 'value'), Output('process-direction', 'value'),
        Output('process-stage', 'value'), Output('process-stage', 'options'), Output('process-context', 'data'),
        Output('process-table', 'active_cell'),
        Output('process-objective', 'figure'), Output('process-design', 'figure'), Output('process-state', 'figure'),
        Output('process-table', 'data'), Output('process-table', 'style_data_conditional'),
        Output('process-stage-heading', 'children'), Output('process-stage-description', 'children'),
        Output('process-time', 'children'), Output('process-stats', 'children'),
        Output('process-inspection', 'children'), Output('process-archive-note', 'children'),
        Output('process-prev', 'disabled'), Output('process-next', 'disabled'),
        Output('process-candidate-hint', 'children'),
        Input('process-location', 'search'),
        Input('process-mode', 'value'), Input('process-step', 'value'), Input('process-direction', 'value'),
        Input('process-stage', 'value'), Input('process-prev', 'n_clicks'), Input('process-next', 'n_clicks'),
        Input('process-objective', 'clickData'), Input('process-table', 'active_cell'),
        State('process-table', 'derived_virtual_data'), State('process-context', 'data'),
    )
    def update_view(search, mode, step, direction, stage, previous_clicks, next_clicks, click, active, rows, previous):
        changed = {item['prop_id'] for item in ctx.triggered if item.get('prop_id') != '.'}
        values = {'process-location.search': search, 'process-mode.value': mode, 'process-step.value': step,
                  'process-direction.value': direction, 'process-stage.value': stage,
                  'process-objective.clickData': click, 'process-table.active_cell': active,
                  'process-table.derived_virtual_data': rows}
        context = reduce_process_context(trace, previous, values, changed)
        mode, step, direction, stage = (context[key] for key in ('mode', 'step', 'direction', 'stage'))
        view = render_process(trace, mode, step, direction, stage, context['candidate'])
        # Store the effective default too: a stage switch must never silently
        # replace an inspected default candidate with a different winner.
        context['candidate'] = view['candidate_id']
        options = [{'label': value, 'value': value, 'disabled': not view['has_candidates']} for value in STAGES]
        clear_cell = (not previous or _record_key(previous) != _record_key(context)
                      or previous.get('stage') != stage or 'process-location.search' in changed)
        active_cell = None if clear_cell else no_update
        row_style = [
            {'if': {'filter_query': '{filter} = "Excluded"'}, 'color': '#8290a0'},
            {'if': {'filter_query': '{filter} = "Excluded (invalid angle)"'}, 'color': '#8290a0'},
            {'if': {'filter_query': '{filter} = "Fallback retained"'}, 'backgroundColor': '#fff5df'},
            {'if': {'filter_query': '{filter} = "Numerical safeguard"'}, 'backgroundColor': '#fff5df'},
        ]
        if view['candidate_id'] is not None:
            row_style.append({'if': {'filter_query': f"{{candidate}} = {view['candidate_id']}"},
                              'backgroundColor': '#eee8f8', 'color': '#4c3779'})
        return (mode, step, direction, stage, options, context, active_cell,
                view['objective'], view['design'], view['state'], view['rows'], row_style,
                view['heading'], view['description'], view['time_label'],
                [html.Span(value) for value in view['stats']], view['inspection'], view['archive_note'],
                int(step) == 0, int(step) == len(trace['modes'][mode]['frames']) - 1,
                'Click a point or a table cell to inspect its 30 variables.' if view['has_candidates']
                else 'No candidate pool at this step. Move the time slider to inspect another recorded state.')

    @app.callback(Output('process-download', 'data'), Input('process-export', 'n_clicks'),
                  State('process-context', 'data'),
                  prevent_initial_call=True)
    def export_record(_clicks, context):
        if not context:
            return no_update
        mode, step, direction = (context[key] for key in ('mode', 'step', 'direction'))
        frame, record = select_record(trace, mode, step, direction)
        result = {'schema_version': trace['schema_version'], 'provenance': trace['provenance'],
                  'configuration': mode, 'step': frame['step'], 'time': frame['time'],
                  'phase': frame['phase'], 'direction': record}
        return {'content': json.dumps(result, indent=2, allow_nan=False),
                'filename': f'paretoflow-process-{mode}-step-{step}-direction-{direction}.json',
                'type': 'application/json'}

    return app
